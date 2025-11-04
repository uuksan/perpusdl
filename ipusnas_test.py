from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from io import BytesIO
import argparse
from urllib.parse import urlparse
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Parser CLI
parser = argparse.ArgumentParser(description="Script Screenshot iPusnas")
parser.add_argument("-l", "--link", required=True, help="Link iPusnas")
parser.add_argument("-f", "--folder", required=True, help="Nama folder untuk simpan hasil")
parser.add_argument("-j", "--jumlah", type=int, required=True, help="Jumlah screenshot")
parser.add_argument("-s", "--sleeps", type=int, default=0, help="tambah waktu sleep (default = 0)")
parser.add_argument("--epub", action="store_true", help="Aktifkan mode EPUB")
parser.add_argument("-H", "--headless", action="store_false", help="Aktifkan mode headless")
parser.add_argument("-z", "--zoom", type=int, default=9, help="Zoom page (default = 9)")
parser.add_argument("--pd", type=int, default=0, help="Page down, menuju ke halaman (default=0)")

args = parser.parse_args()

# === Pengaturan awal ===

link_ipusnas = args.link
parsed = urlparse(link_ipusnas)
domain = parsed.netloc
#path = parsed.path


sleeps = args.sleeps
folder_name = os.path.join("hasil", args.folder)
os.makedirs(folder_name, exist_ok=True)
jumlah = args.jumlah-args.pd
zoom = args.zoom
pd = args.pd

print()
print("Link:", link_ipusnas)
print("Folder:", folder_name)
print("Jumlah halaman:", jumlah)
print()

# === Opsi Chrome ===
options = Options()
#HEADLESS
if args.headless:
    options.add_argument("--headless")

driver = webdriver.Firefox(options=options)

# Atur posisi window (misalnya monitor kedua, koordinat x=1920, y=0)
#driver.set_window_position(1920, 0)

# Atur ukuran window
monitor2_width = 2160
monitor2_height = 3200
driver.set_window_size(monitor2_width, monitor2_height)
#driver.maximize_window()

service = Service(r"C:\Users\asus-pc\AppData\Local\Microsoft\WinGet\Packages\Mozilla.GeckoDriver_Microsoft.Winget.Source_8wekyb3d8bbwe\geckodriver.exe")


driver.get(f"https://{domain}/login")  # ganti dengan URL target
time.sleep(2)

load_dotenv()
email_ipusnas = os.getenv("EMAIL")
password_ipusnas = os.getenv("PASSWORD")

username_input = driver.find_element(By.ID, "email")
password_input = driver.find_element(By.NAME, "password")
username_input.send_keys(email_ipusnas)
password_input.send_keys(password_ipusnas)
password_input.send_keys(Keys.RETURN)
time.sleep(9)
time.sleep(sleeps)

driver.get(link_ipusnas)
time.sleep(3)
time.sleep(sleeps)

pop_button = driver.find_element(By.CSS_SELECTOR, "button.ant-btn.ant-btn-default.ant-btn-lg.btn-popup-modal")
pop_button.click()
driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
time.sleep(2)
time.sleep(sleeps)

baca_button = driver.find_element(By.CSS_SELECTOR, "button.ant-btn.button-read")
baca_button.click()
time.sleep(9)
time.sleep(sleeps)

#fungsi screenshot
def screenshot_pages(driver, folder_name, jumlah, zoom, pd):
    body = driver.find_element(By.TAG_NAME, "body")  # ambil elemen <body>

    for _ in range(zoom):
        zoom_in_btn = driver.find_element(By.CSS_SELECTOR, "button[data-testid='zoom__in-button']")
        zoom_in_btn.click()
        time.sleep(0.5)

    time.sleep(0.5)
    element = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Page 1']")
    ActionChains(driver).move_to_element(element).perform()
    time.sleep(3)
    
    for b in range (pd):
        body.send_keys(Keys.PAGE_DOWN)  # tekan PageDown
        time.sleep(1)
    if args.pd:
        time.sleep(9)

    # === Loop screenshot ===
    
    for i in range(jumlah):
        file_name = os.path.join(folder_name, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.png")
        # --- Ambil full page screenshot (binary PNG) ---
        png_data = driver.get_full_page_screenshot_as_png()

        # --- Buka dengan Pillow ---
        image = Image.open(BytesIO(png_data))
        image = image.convert('RGB')
        
        
        #ambil htmlnya
        div_elem = driver.find_element(By.CSS_SELECTOR, f"div.rpv-core__text-layer[data-testid='core__text-layer-{i}']")
        
        div_text = div_elem.text

        # --- Simpan ke file ---
        output_path = os.path.join(folder_name, f"halaman{i+1}.txt")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(div_text)

        # --- Simpan ke file ---
        image.save(file_name, "PNG")
        print(f"Screenshot {i+1}/{jumlah}  tersimpan: {file_name}")
        
        body.send_keys(Keys.PAGE_DOWN)  # tekan PageDown
        time.sleep(1.4)

#fungsi epub
def epub_pages(driver, folder_name, jumlah):
    """
    Menyimpan konten iframe dari reader ke file HTML.
    
    :param driver: Selenium WebDriver
    :param folder_name: Folder output tempat menyimpan file
    :param jumlah: Banyak halaman yang ingin disimpan
    :param timeout: Waktu tunggu maksimum untuk elemen (detik)
    """
    wait = WebDriverWait(driver, 15)

    # Tombol pertama (ikon untuk buka viewer)
    svg_elem = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[viewBox="0 0 48 48"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", svg_elem)
    time.sleep(0.3)
    svg_elem.click()

    for i in range(jumlah):
        # Tunggu iframe muncul
        iframe = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.epub-view iframe"))
        )

        # Ambil isi HTML
        srcdoc_html = iframe.get_attribute("srcdoc")

        # Simpan ke file
        filename = os.path.join(folder_name, f"iframe_content_{i+1}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(srcdoc_html)
        print(f"✅ Halaman {i+1}/{jumlah} disimpan: {filename}")

        # Klik tombol Next
        try:
            svg_elem = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.tabler-icon-chevron-right"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", svg_elem)
            time.sleep(0.3)
            svg_elem.click()
            time.sleep(1)
        except:
            print(f"❌ Tidak bisa klik tombol Next di halaman {i+1}. Berhenti.")
            break


if args.epub:
    epub_pages(driver, folder_name=folder_name, jumlah=jumlah)
else:
    screenshot_pages(driver, folder_name=folder_name, jumlah=jumlah, zoom=zoom, pd=pd)


print()
print(r"""
  _______
< Done! >
  -------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
""")

#driver.quit()
if args.headless:
    driver.quit()