import os, time, re, shutil, socket, subprocess, urllib.parse, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from ebooklib import epub
import argparse
from urllib.parse import urlparse


# ============================================================
# Fungsi 1️⃣ - Buka Chrome Remote Debugging
# ============================================================
def start_chrome():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\chrome_selenium"
    debug_port = 9222

    # Cek apakah port sudah dipakai
    import socket, subprocess, time
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connected = s.connect_ex(("localhost", debug_port)) == 0

    if not connected:
        subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={debug_port}",
            f'--user-data-dir={user_data_dir}'
        ])
        print("🚀 Membuka Chrome dengan remote debugging...")
        time.sleep(5)  # tambah waktu agar Chrome siap

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    options = webdriver.ChromeOptions()
    options.debugger_address = f"127.0.0.1:{debug_port}"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("✅ Terhubung ke Chrome")
    driver.implicitly_wait(5)
    return driver



# ============================================================
# Fungsi 2️⃣ - Ambil Nama Penulis
# ============================================================
def get_author_name(driver):
    try:
        penulis_link = driver.find_element(By.XPATH, "//div[contains(@class, 'flex flex-wrap items-center gap-2')]/span/a")
        penulis_name = penulis_link.text.strip()
        print("Penulis: ",penulis_name)
        return penulis_name
    except Exception as e:
        print("⚠️ Gagal mengambil nama penulis:", e)
        return "Tanpa Nama"


# ============================================================
# Fungsi 3️⃣ - Ambil CHAPTER 0 & Cover
# ============================================================
def get_book_intro(driver, link):
    div_elem = driver.find_element(By.CSS_SELECTOR, "div.lg\\:col-span-2.order-2.lg\\:order-1")
    soup = BeautifulSoup(div_elem.get_attribute("innerHTML"), "html.parser")

    for svg in soup.find_all("svg"): svg.decompose()
    for a in soup.find_all("a"): a.replace_with(a.get_text())

    for div in soup.find_all("div", class_="flex items-center gap-4"):
        spans = div.find_all("span")
        if len(spans) == 2: spans[0].insert_after(" ")

    title = driver.find_element(By.TAG_NAME, "h1").text
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title).strip()
    folder = os.path.join("hasil", safe_title)
    os.makedirs(folder, exist_ok=True)

    html_out = f"""<!DOCTYPE html><html lang="id"><head><meta charset="UTF-8">
<title>{title}</title></head><body>{soup}<h2>Link Buku</h2><p><a href={link}>{link}</a></p></body></html>"""
    with open(os.path.join(folder, f"CHAPTER 0 - {safe_title}.html"), "w", encoding="utf-8") as f:
        f.write(html_out)
    print("✅ CHAPTER 0 disimpan.")

    img = driver.find_element(By.CSS_SELECTOR, "img.object-contain")
    srcset = img.get_attribute("srcset")
    encoded_url = srcset[srcset.find("url=") + 4: srcset.find("&", srcset.find("url="))]
    decoded_url = urllib.parse.unquote(encoded_url)
    response = requests.get(decoded_url)
    with open(os.path.join(folder, "cover.png"), "wb") as f:
        f.write(response.content)
    print("✅ Cover disimpan.")
    return title, folder


# ============================================================
# Fungsi 4️⃣ - Buka Bab Pertama
# ============================================================
def open_first_chapter(driver):
    wait = WebDriverWait(driver, 20)
    tombol = wait.until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "div.group.cursor-pointer.text-white"  # cukup spesifik tapi aman
        ))
    )

    # Klik tombolnya
    tombol.click()
    print("✅ Tombol berhasil diklik!")
    time.sleep(3)
    
    
    menu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
        'button[aria-haspopup="dialog"][data-slot="popover-trigger"]')))
    menu_button.click()
    chapter_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,
        'a.flex.items-start.font-light.justify-start.text-left.gap-2.text-base.hover\\:underline')))
    if chapter_links:
        chapter_links[0].click()
        print("✅ Bab pertama dibuka")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "reader-content")))
    time.sleep(3)


# ============================================================
# Fungsi 5️⃣ - Ambil Semua Halaman
# ============================================================
def scrape_all_chapters(driver, max_pages=100):
    wait = WebDriverWait(driver, 20)
    all_html = []
    for i in range(max_pages):
        reader = wait.until(EC.presence_of_element_located((By.ID, "reader-content")))
        all_html.append(reader.get_attribute("outerHTML"))
        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Next')]]")))
            next_btn.click()
        except:
            break
        time.sleep(2)
    return BeautifulSoup("\n".join(all_html), "html.parser")


# ============================================================
# Fungsi 6️⃣ - Bersihkan & Split HTML
# ============================================================
def clean_and_split_html(soup, folder):
    for div in soup.find_all("div", class_="flex flex-col md:items-center select-none md:justify-center gap-1 text-left md:text-center mb-6 md:mb-10 md:mt-[0.5in] text-black bg-white"):
        p_tag = div.find("p")
        h1_tag = div.find("h1")
        if p_tag and h1_tag:
            # Gabungkan isi p dan h1
            combined_text = f"{p_tag.get_text(strip=True)} – {h1_tag.get_text(strip=True)}"
            new_h1 = soup.new_tag("h1")
            new_h1.string = combined_text
            new_h1["style"] = "text-align:center"
            div.replace_with(new_h1)
        
    for div in soup.find_all("div", class_="flex flex-col md:items-center select-none md:justify-center gap-1 text-left md:text-center mb-6 md:mb-10 mt-8 md:mt-[1in] text-black bg-white"):
        p_tag = div.find("p")
        h1_tag = div.find("h1")
        if p_tag and h1_tag:
            # Gabungkan isi p dan h1
            combined_text = f"{p_tag.get_text(strip=True)} – {h1_tag.get_text(strip=True)}"
            new_h1 = soup.new_tag("h1")
            new_h1.string = combined_text
            new_h1["style"] = "text-align:center"
            div.replace_with(new_h1)
            
    if soup.find("div", {"id": "reader-content"}):
        soup.find("div", {"id": "reader-content"}).unwrap()
    for d in soup.find_all("div"): d.unwrap()

    for div in soup.find_all("div", class_=re.compile("flex flex-col md:items-center")):
        p_tag, h1_tag = div.find("p"), div.find("h1")
        if p_tag and h1_tag:
            combined_text = f"{p_tag.get_text(strip=True)} – {h1_tag.get_text(strip=True)}"
            new_h1 = soup.new_tag("h1", style="text-align:center")
            new_h1.string = combined_text
            div.replace_with(new_h1)

    chapters = soup.find_all("h1")
    if not chapters:
        with open(os.path.join(folder, "isi.html"), "w", encoding="utf-8") as f:
            f.write(str(soup))
        return

    for i, h1 in enumerate(chapters):
        raw_title = re.sub(r'[\\/*?:"<>|]', "_", h1.get_text(strip=True))
        fname = os.path.join(folder, f"{raw_title}.html")
        next_h1 = chapters[i+1] if i+1 < len(chapters) else None
        content = []
        for elem in h1.next_siblings:
            if elem == next_h1: break
            content.append(str(elem))
        html_out = f"<html><title>{h1.get_text(strip=True)}</title><body>{h1}{''.join(content)}</body></html>"
        with open(fname, "w", encoding="utf-8") as f: f.write(html_out)
        print("✅ Bab disimpan:", fname)


# ============================================================
# Fungsi 7️⃣ - Buat EPUB
# ============================================================
# def create_epub(folder, title, author):
    # book = epub.EpubBook()
    # book.set_identifier("id123456")
    # book.set_title(title)
    # book.set_language("id")
    # book.add_author(author)
    # book.add_metadata("DC", "publisher", "MalakaBooks.id")

    # cover = os.path.join(folder, "cover.png")
    # if os.path.exists(cover):
        # with open(cover, "rb") as f:
            # book.set_cover("cover.png", f.read())

    # html_files = sorted([f for f in os.listdir(folder) if f.lower().startswith("chapter") and f.endswith(".html")])
    # chapters = []
    # for f_html in html_files:
        # with open(os.path.join(folder, f_html), encoding="utf-8") as f:
            # soup = BeautifulSoup(f, "html.parser")
        # title_html = soup.find("h1").get_text(strip=True) if soup.find("h1") else f_html
        # chapter = epub.EpubHtml(title=title_html, file_name=f_html, lang="id", content=str(soup))
        # book.add_item(chapter)
        # chapters.append(chapter)

    # nav = epub.EpubNav()
    # book.add_item(epub.EpubNcx())
    # book.add_item(nav)
    # book.spine = [chapters[0], nav] + chapters[1:]
    # book.toc = tuple(chapters)
    # time.sleep(2)
    # output = os.path.join("hasil", f"{title} - {author} - MalakaBooks.epub")
    # epub.write_epub(output, book, {})
    # print(f"🎉 EPUB dibuat: {output}")
    
def create_epub(folder, title, author):
    # Pastikan folder hasil ada, jika tidak buat
    output_folder = "hasil"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Validasi input
    if not title or not author:
        raise ValueError("Judul dan penulis tidak boleh kosong!")

    # Membuat objek EPUB
    book = epub.EpubBook()
    book.set_identifier("id123456")
    book.set_title(title)
    book.set_language("id")
    book.add_author(author)
    book.add_metadata("DC", "publisher", "MalakaBooks.id")

    # Menambahkan cover jika ada
    cover = os.path.join(folder, "cover.png")
    if os.path.exists(cover):
        with open(cover, "rb") as f:
            book.set_cover("cover.png", f.read())
    else:
        print("Cover tidak ditemukan, melanjutkan tanpa cover...")

    # Mencari dan membaca file HTML untuk bab
    html_files = sorted([f for f in os.listdir(folder) if f.lower().startswith("chapter") and f.endswith(".html")])
    if not html_files:
        raise ValueError("Tidak ada file HTML bab ditemukan dalam folder!")

    chapters = []
    for f_html in html_files:
        chapter_file_path = os.path.join(folder, f_html)
        try:
            with open(chapter_file_path, encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Menentukan judul bab, mencari tag <h1> jika ada
            title_html = soup.find("h1").get_text(strip=True) if soup.find("h1") else f_html
            chapter = epub.EpubHtml(title=title_html, file_name=f_html, lang="id", content=str(soup))
            book.add_item(chapter)
            chapters.append(chapter)

        except Exception as e:
            print(f"Error membaca file {f_html}: {e}")
            continue  # Lanjutkan ke bab berikutnya jika ada kesalahan

    if not chapters:
        raise ValueError("Tidak ada bab yang berhasil ditambahkan ke dalam EPUB.")

    # Menambahkan navigasi
    nav = epub.EpubNav()
    book.add_item(epub.EpubNcx())  # Menambahkan file NCX
    book.add_item(nav)

    # Menentukan spine dan TOC (Table of Contents)
    book.spine = [chapters[0], nav] + chapters[1:]
    book.toc = tuple(chapters)

    # Membuat nama file output
    safe_title = "".join([c if c.isalnum() else "_" for c in title])  # Mengganti karakter yang tidak aman untuk nama file
    safe_author = "".join([c if c.isalnum() else "_" for c in author])  # Mengganti karakter yang tidak aman
    # output = os.path.join(output_folder, f"{safe_title} - {safe_author} - MalakaBooks.epub")
    output = os.path.join(output_folder, f"{title} - {author} - MalakaBooks.epub")

    try:
        # Menulis file EPUB
        epub.write_epub(output, book, {})
        print(f"🎉 EPUB berhasil dibuat: {output}")
    except Exception as e:
        print(f"Error saat menulis file EPUB: {e}")


# ============================================================
# Fungsi 8️⃣ - Hapus Folder
# ============================================================
def hapus_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"🗑️ Folder {path} dihapus.")

# ============================================================
# Fungsi 9 - argparse
# ============================================================

def get_link_from_args():
    """
    Membaca argumen baris perintah untuk mendapatkan link buku MalakaBooks.
    Contoh penggunaan:
        python malaka.py -l "https://malakabooks.id/book/abc123"
    Returns:
        tuple: (link, domain)
    """
    parser = argparse.ArgumentParser(description="Script Malaka Books save")
    parser.add_argument("-l", "--link", required=True, help="Link Malaka Books")
    args = parser.parse_args()

    link_malakabooks = args.link.strip()
    parsed = urlparse(link_malakabooks)
    domain = parsed.netloc

    print(f"\nLink: {link_malakabooks}")
    return link_malakabooks, domain
    
    
# ============================================================
# MAIN
# ============================================================
def main():
    link, domain = get_link_from_args()
    driver = start_chrome()
    driver.get(link)
    author = get_author_name(driver)
    title, folder = get_book_intro(driver, link)
    open_first_chapter(driver)
    soup = scrape_all_chapters(driver)
    clean_and_split_html(soup, folder)
    create_epub(folder, title, author)
    # hapus_folder(folder)
    print("✅ Semua proses selesai.")


if __name__ == "__main__":
    main()
