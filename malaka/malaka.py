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

parser = argparse.ArgumentParser(description="Script Malaka Books save")
parser.add_argument("-l", "--link", required=True, help="Link Malaka Books")
args = parser.parse_args()


link_malakabooks = args.link
parsed = urlparse(link_malakabooks)
domain = parsed.netloc
#path = parsed.path
print("Link:", link_malakabooks)
print()


options = webdriver.ChromeOptions()
options.debugger_address = "127.0.0.1:9222"

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
filename = os.path.join(safe_title, f"{save_title_book}.html")

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

# hasil akhir jadi string siap tulis ke file
cleaned_html = str(soup)

# --- Simpan hasil akhir ---

isiname = os.path.join(safe_title, "isi.html")
with open(isiname, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("🎉 Semua halaman selesai disimpan & dirapikan ke isi.html")
#########################################################################


#input("Tekan ENTER untuk keluar (Chrome tetap terbuka jika tidak ditutup manual)...")