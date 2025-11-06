from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import argparse
from urllib.parse import urlparse
import subprocess
import re


parser = argparse.ArgumentParser(description="Script Malaka Books save")
parser.add_argument("-l", "--link", required=True, help="Link Malaka Books")
args = parser.parse_args()


link_malakabooks = args.link
parsed = urlparse(link_malakabooks)
domain = parsed.netloc
#path = parsed.path
print()
print("Link:", link_malakabooks)
print()


### run task ini untuk membuka chrome kusus selenium
### "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_selenium"

# --- Jalankan Chrome dalam mode remote debugging ---
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data_dir = r"C:\chrome_selenium"
debug_port = 9222

# Cek apakah sudah ada Chrome yang berjalan di port itu
# (agar tidak membuka lebih dari satu)
import socket
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

if not is_port_in_use(debug_port):
    subprocess.Popen([
        chrome_path,
        f"--remote-debugging-port={debug_port}",
        f'--user-data-dir={user_data_dir}'
    ])
    print("🚀 Membuka Chrome dengan remote debugging...")
    time.sleep(3)  # beri waktu agar Chrome siap

# --- Hubungkan Selenium ke Chrome yang sudah terbuka ---
options = webdriver.ChromeOptions()
options.debugger_address = f"127.0.0.1:{debug_port}"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)



driver.get(link_malakabooks)

# Tunggu halaman termuat penuh (opsional, bisa dihapus kalau cepat)
driver.implicitly_wait(5)




##########################################################

# Ambil HTML dari elemen utama
div_elem = driver.find_element("css selector", "div.lg\\:col-span-2.order-2.lg\\:order-1")
inner_html = div_elem.get_attribute("innerHTML")

# Parsing dengan BeautifulSoup
soup = BeautifulSoup(inner_html, "html.parser")

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

# Ambil kembali HTML hasil bersih
clean_html = str(soup)

# Ambil judul untuk nama file
title = driver.find_element("tag name", "h1").text
save_title_book = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title).strip()
safe_title = os.path.join("hasil", save_title_book)
os.makedirs(safe_title, exist_ok=True)
filename = os.path.join(safe_title, f"CHAPTER 0 - {save_title_book}.html")

# Bungkus dengan struktur HTML dasar
html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>{title}</title>
</head>
<body>
{clean_html}
</body>
</html>"""

# Simpan ke file
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ HTML berhasil dibersihkan dan disimpan sebagai: {filename}")


##############################################

# Cari elemen <img> dengan class "object-contain"
img = driver.find_element("css selector", "img.object-contain")

# Ambil atribut srcset
srcset = img.get_attribute("srcset")

# Ekstrak URL terenkripsi setelah "url=" dan sebelum "&"
start = srcset.find("url=") + 4
end = srcset.find("&", start)
encoded_url = srcset[start:end]

# Decode URL menjadi bentuk asli
decoded_url = urllib.parse.unquote(encoded_url)
# print("📸 URL gambar asli:", decoded_url)

# Download PNG-nya dan simpan sebagai cover.png
response = requests.get(decoded_url)
covername = os.path.join(safe_title, "cover.png")
with open(covername, "wb") as f:
    f.write(response.content)

print("✅ Gambar berhasil disimpan sebagai cover.png")
##########################

# Tunggu tombol muncul dan bisa diklik
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

######################################################
time.sleep(4)

# --- 1️⃣ Tunggu tombol menu (hamburger) muncul ---
menu_button = wait.until(EC.element_to_be_clickable((
    By.CSS_SELECTOR,
    'button[aria-haspopup="dialog"][data-slot="popover-trigger"]'
)))

# Klik tombol menu
driver.execute_script("arguments[0].scrollIntoView(true);", menu_button)
time.sleep(2)
menu_button.click()
print("✅ Tombol menu berhasil diklik")

# --- 2️⃣ Tunggu daftar link bab muncul ---
chapter_links = wait.until(EC.presence_of_all_elements_located((
    By.CSS_SELECTOR,
    'a.flex.items-start.font-light.justify-start.text-left.gap-2.text-base.hover\\:underline'
)))

# --- 3️⃣ Klik link pertama (halaman awal buku) ---
if chapter_links:
    first_link = chapter_links[0]
    driver.execute_script("arguments[0].scrollIntoView(true);", first_link)
    time.sleep(2)
    first_link.click()
    print("✅ Klik link pertama (halaman awal buku)")
else:
    print("⚠️ Tidak menemukan link bab di halaman ini")

# --- 4️⃣ Tunggu konten reader muncul ---
reader = wait.until(EC.presence_of_element_located((By.ID, "reader-content")))
print("📖 Halaman awal berhasil dibuka!")

# --- (Selanjutnya kamu bisa lanjut ke loop ambil HTML dan klik Next di sini) ---

#######################################################
time.sleep(4)

all_html = []

# --- Loop ambil isi beberapa halaman ---
for i in range(100):
    reader = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="reader-content"]')))
    html_content = reader.get_attribute("outerHTML")
    all_html.append(html_content)
    print(f"✅ Halaman {i+1} diambil")

    try:
        next_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[.//span[contains(text(), 'Next')]]"
            ))
        )
        next_button.click()
        print("➡️ Klik tombol Next")
    except Exception as e:
        print(f"⚠️ Tidak menemukan tombol Next di halaman {i+1}: {e}")
        break

    time.sleep(2)

# --- Gabungkan semua HTML ---
combined_html = "\n\n".join(all_html)

# --- 🧹 Bersihkan & ubah HTML ---
soup = BeautifulSoup(combined_html, "html.parser")

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



####################################################################
# --- Simpan hasil akhir ---

#isiname = os.path.join(safe_title, "isi.html")
#with open(isiname, "w", encoding="utf-8") as f:
#    f.write(str(soup))

#print("🎉 Semua halaman selesai disimpan & dirapikan ke isi.html")
#########################################################################


###########################
#input("Tekan ENTER untuk keluar (Chrome tetap terbuka jika tidak ditutup manual)...")

#################################
#hapus div
# Cari elemen utama reader-content
reader_content = soup.find("div", {"id": "reader-content"})

if reader_content:
    # Hapus tag <div id="reader-content"> tapi biarkan semua isinya tetap ada
    reader_content.unwrap()
    print("✅ Tag <div id='reader-content'> telah dihapus, isi di dalamnya tetap dipertahankan.")
    
    for div in soup.find_all("div"):
      div.unwrap()
      print("🧹 Semua <div> dihapus, isi di dalamnya tetap dipertahankan.")
else:
    print("⚠️ Tidak menemukan <div id='reader-content'>.")
    


####################

# --- Ganti blok penyimpanan isi.html dengan kode ini ---
# Cari semua tag h1 di dalam soup (dimanapun posisinya)
chapters = soup.find_all("h1")

# Jika tidak ada h1 sama sekali, simpan seluruh isi
if not chapters:
    fallback_path = os.path.join(safe_title, "isi.html")
    with open(fallback_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"⚠️ Tidak menemukan <h1>. Menyimpan keseluruhan sebagai: {fallback_path}")
else:
    for i, h1_tag in enumerate(chapters):
        # Ambil teks dari h1 sebagai judul bab
        raw_title = h1_tag.get_text(strip=True)
        safe_fname = re.sub(r'[\\/*?:"<>|]', "_", raw_title).strip()
        if len(safe_fname) > 150:
            safe_fname = safe_fname[:150].rstrip()

        chapter_filename = os.path.join(safe_title, f"{safe_fname}.html")

        # Tentukan batas: dari h1 ini sampai sebelum h1 berikutnya
        start = h1_tag
        end = chapters[i + 1] if i + 1 < len(chapters) else None

        # Kumpulkan semua elemen antar kedua h1 tersebut
        content = []
        for elem in h1_tag.next_siblings:
            if elem == end:
                break
            content.append(str(elem))

        # Gabungkan isi dan tambahkan h1 di awal
        chapter_html_body = str(h1_tag) + "".join(content)

        # Bungkus HTML agar bisa dibuka langsung
        html_out = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>{raw_title}</title>
</head>
<body>
{chapter_html_body}
</body>
</html>"""

        # Simpan file
        with open(chapter_filename, "w", encoding="utf-8") as out:
            out.write(html_out)

        print(f"✅ Disimpan bab {i+1}: {chapter_filename}")

print("📚 Pemisahan bab selesai. Cek folder:", safe_title)