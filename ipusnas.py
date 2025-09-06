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


# Parser CLI
parser = argparse.ArgumentParser(description="Script Screenshot iPusnas")
parser.add_argument("-l", "--link", required=True, help="Link iPusnas")
parser.add_argument("-f", "--folder", required=True, help="Nama folder untuk simpan hasil")
parser.add_argument("-j", "--jumlah", type=int, required=True, help="Jumlah screenshot")
parser.add_argument("-s", "--sleeps", type=int, default=0, help="tambah waktu sleep (default = 0)")
parser.add_argument("--epub", action="store_true", help="Aktifkan mode EPUB")
parser.add_argument(
    "-H", "--headless",
    action="store_false",
    help="Aktifkan mode headless"
)
parser.add_argument(
    "-z", "--zoom",
    type=int,
    default=9,
    help="Zoom page (default = 9)"
)

args = parser.parse_args()

# === Pengaturan awal ===

link_ipusnas = args.link
parsed = urlparse(link_ipusnas)
domain = parsed.netloc
#path = parsed.path


sleeps = args.sleeps
folder_name = os.path.join("hasil", args.folder)
os.makedirs(folder_name, exist_ok=True)
jumlah = args.jumlah
epub_mode = args.epub   # True kalau --epub ditulis, False kalau tidak
zoom = args.zoom

print()
print("Link:", link_ipusnas)
print("Folder:", folder_name)
print("Jumlah screenshot:", jumlah)
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
monitor2_height = 3840
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

for _ in range(zoom):
    zoom_in_btn = driver.find_element(By.CSS_SELECTOR, "button[data-testid='zoom__in-button']")
    zoom_in_btn.click()
    time.sleep(0.5)

time.sleep(0.5)
element = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Page 1']")
ActionChains(driver).move_to_element(element).perform()
time.sleep(3)


# === Loop screenshot ===
body = driver.find_element(By.TAG_NAME, "body")  # ambil elemen <body>
for i in range(jumlah):
    file_name = os.path.join(folder_name, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.png")
    # --- Ambil full page screenshot (binary PNG) ---
    png_data = driver.get_full_page_screenshot_as_png()

    # --- Buka dengan Pillow ---
    image = Image.open(BytesIO(png_data))
    image = image.convert('RGB')

    # --- Simpan ke file ---
    image.save(file_name, "PNG")
    print(f"Screenshot {i+1}/{jumlah}  tersimpan: {file_name}")
    body.send_keys(Keys.PAGE_DOWN)  # tekan PageDown
    time.sleep(1.4)

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
