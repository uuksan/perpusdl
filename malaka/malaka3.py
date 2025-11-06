import os
import time
import requests
import urllib.parse
from ebooklib import epub
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import socket

# Fungsi untuk memeriksa apakah port sudah digunakan
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Fungsi untuk membuka browser Chrome dengan remote debugging
def open_chrome(debug_port, chrome_path, user_data_dir):
    if not is_port_in_use(debug_port):
        subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={debug_port}",
            f'--user-data-dir={user_data_dir}'
        ])
        print("🚀 Membuka Chrome dengan remote debugging...")
        time.sleep(3)  # beri waktu agar Chrome siap

# Fungsi untuk mendapatkan HTML dari halaman utama
def get_html_from_page(driver, link):
    driver.get(link)
    driver.implicitly_wait(5)
    div_elem = driver.find_element("css selector", "div.lg\\:col-span-2.order-2.lg\\:order-1")
    inner_html = div_elem.get_attribute("innerHTML")
    return BeautifulSoup(inner_html, "html.parser")

# Fungsi untuk membersihkan HTML dari elemen yang tidak diinginkan
def clean_html(soup):
    # 1️⃣ Hapus semua <svg> dan isinya
    for svg in soup.find_all("svg"):
        svg.decompose()

    # 2️⃣ Ganti semua <a> dengan teks di dalamnya
    for a in soup.find_all("a"):
        a.replace_with(a.get_text())

    # 3️⃣ Tambahkan spasi antara dua <span> di dalam <div class="flex items-center gap-4">
    for div in soup.find_all("div", class_="flex items-center gap-4"):
        spans = div.find_all("span")
        if len(spans) == 2:
            spans[0].insert_after(" ")

    return str(soup)

# Fungsi untuk menyimpan HTML yang telah dibersihkan
def save_clean_html(filename, title, clean_html, link):
    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>{title}</title>
</head>
<body>
{clean_html}
<h2 class="text-xl font-bold text-neutral-900 dark:text-white">Link Buku</h2>
<p><a href={link}>{link}</a></p>
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ HTML berhasil dibersihkan dan disimpan sebagai: {filename}")

# Fungsi untuk mengunduh gambar (cover)
def download_cover(driver, safe_title):
    img = driver.find_element("css selector", "img.object-contain")
    srcset = img.get_attribute("srcset")
    start = srcset.find("url=") + 4
    end = srcset.find("&", start)
    encoded_url = srcset[start:end]
    decoded_url = urllib.parse.unquote(encoded_url)
    response = requests.get(decoded_url)
    covername = os.path.join(safe_title, "cover.png")
    with open(covername, "wb") as f:
        f.write(response.content)
    print("✅ Gambar berhasil disimpan sebagai cover.png")

# Fungsi untuk mengambil nama penulis
def get_author_name(driver):
    penulis_link = driver.find_element(By.XPATH, "//div[contains(@class, 'flex flex-wrap items-center gap-2')]/span/a")
    return penulis_link.text.strip()
    
#fungsi menyimpan html
# Fungsi untuk menyimpan chapter sebagai file HTML
def save_chapter(chapter_title, chapter_html_body, safe_title):
    # Menyusun nama file untuk chapter
    safe_fname = re.sub(r'[\\/*?:"<>|]', "_", chapter_title).strip()
    if len(safe_fname) > 150:
        safe_fname = safe_fname[:150].rstrip()

    chapter_filename = os.path.join(safe_title, f"{safe_fname}.html")

    # Bungkus HTML agar bisa dibuka langsung
    chapter_html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>{chapter_title}</title>
</head>
<body>
{chapter_html_body}
</body>
</html>"""

    # Simpan file HTML untuk chapter
    with open(chapter_filename, "w", encoding="utf-8") as out:
        out.write(chapter_html_content)

    print(f"✅ Disimpan bab: {chapter_filename}")


# Fungsi untuk membuat file EPUB
def create_epub(safe_title, penulis_name, book_folder, output_file):
    book = epub.EpubBook()
    book.set_identifier("id123456")
    book.set_title(book_folder)
    book.set_language("id")
    book.add_author(penulis_name)
    book.add_metadata("DC", "publisher", "MalakaBooks.id")

    # Menambahkan cover
    cover_path = os.path.join(safe_title, "cover.png")
    if os.path.exists(cover_path):
        with open(cover_path, "rb") as f:
            book.set_cover("cover.png", f.read())
        print("✅ Cover ditambahkan")
    else:
        print("⚠️ Tidak menemukan cover.png")

    # Menambahkan file HTML ke EPUB
    html_files = sorted(
        [f for f in os.listdir(safe_title)
         if f.lower().endswith(".html") and f.lower().startswith("chapter")],
        key=lambda x: int(x.split(" ")[1].split("–")[0])  # Urut berdasarkan nomor setelah "CHAPTER"
    )

    spine = []
    chapters_list = []

    for html_file in html_files:
        file_path = os.path.join(safe_title, html_file)
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        h1 = soup.find("h1")
        chapter_title = h1.get_text(strip=True) if h1 else os.path.splitext(html_file)[0]

        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=html_file,
            lang="id",
            content=str(soup)
        )

        book.add_item(chapter)
        chapters_list.append(chapter)
        print(f"📄 Ditambahkan: {chapter_title}")

    # Menambahkan stylesheet
    style = '''
    body { font-family: "Helvetica", sans-serif; line-height: 1.5; }
    h1 { text-align: center; }
    img { max-width: 100%; height: auto; display: block; margin: auto; }
    '''
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css",
                            media_type="text/css", content=style)
    book.add_item(nav_css)

    # Menambahkan item navigasi EPUB
    book.add_item(epub.EpubNcx())
    nav = epub.EpubNav()
    book.add_item(nav)

    # Spine dan TOC
    book.spine = [chapters_list[0], nav] + chapters_list[1:] if len(chapters_list) > 1 else chapters_list
    book.toc = tuple(chapters_list)

    # Menyimpan EPUB
    epub.write_epub(output_file, book, {})
    print(f"🎉 EPUB berhasil dibuat: {output_file}")

# Fungsi utama
def main(link_malakabooks):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\chrome_selenium"
    debug_port = 9222
    open_chrome(debug_port, chrome_path, user_data_dir)

    # --- Hubungkan Selenium ke Chrome yang sudah terbuka ---
    options = webdriver.ChromeOptions()
    options.debugger_address = f"127.0.0.1:{debug_port}"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(link_malakabooks)

    # --- Ambil HTML dan bersihkan ---
    soup = get_html_from_page(driver, link_malakabooks)
    clean_html_content = clean_html(soup)

    # --- Menyimpan hasil HTML ---
    title = driver.find_element("tag name", "h1").text
    save_title_book = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title).strip()
    safe_title = os.path.join("hasil", save_title_book)
    os.makedirs(safe_title, exist_ok=True)
    filename = os.path.join(safe_title, f"CHAPTER 0 - {save_title_book}.html")
    save_clean_html(filename, title, clean_html_content, link_malakabooks)
    #menyimpan html chapter
    
    #save_chapter(chapter_title, chapter_html_body, safe_title)
    
    # --- Dapatkan penulis dan simpan cover ---
    penulis_name = get_author_name(driver)
    download_cover(driver, safe_title)

    # --- Buat EPUB ---
    output_file = os.path.join(safe_title, f"{save_title_book}.epub")
    create_epub(safe_title, penulis_name, save_title_book, output_file)

# Panggil fungsi utama
if __name__ == "__main__":
    link_malakabooks = "https://malakabooks.id/book/8dfd94ee-3080-4983-ac10-b7aa7a4cea53"  # Ganti dengan URL yang sesuai
    main(link_malakabooks)
