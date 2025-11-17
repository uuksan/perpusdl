import os
import time
import argparse
from datetime import datetime
from io import BytesIO
from urllib.parse import urlparse
from dotenv import load_dotenv
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================================================
# === FUNGSI: SETUP SELENIUM DRIVER =======================
# =========================================================
def setup_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(2160, 3200)
    return driver


# =========================================================
# === FUNGSI: LOGIN IPUSNAS ===============================
# =========================================================
def login_ipusnas(driver, link, sleep_time=0):
    print()
    print("Link:    ", link)
    parsed = urlparse(link)
    domain = parsed.netloc

    driver.get(f"https://{domain}/login")
    time.sleep(2)

    load_dotenv()
    email_ipusnas = os.getenv("EMAIL")
    password_ipusnas = os.getenv("PASSWORD")

    username_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys(email_ipusnas)
    password_input.send_keys(password_ipusnas)
    password_input.send_keys(Keys.RETURN)
    time.sleep(9 + sleep_time)

    driver.get(link)
    time.sleep(3 + sleep_time)

    try:
        pop_button = driver.find_element(By.CSS_SELECTOR, "button.ant-btn.ant-btn-default.ant-btn-lg.btn-popup-modal")
        pop_button.click()
        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(3):
            body.send_keys(Keys.ESCAPE)
        time.sleep(2 + sleep_time)
    except:
        pass
    
    # === Ambil data judul & penulis ===
    desc = driver.find_element(By.CSS_SELECTOR, "div.description-book")

    judul = desc.find_element(By.CSS_SELECTOR, "h2.book-title span").text
    penulis = desc.find_element(By.CSS_SELECTOR, "div.book-author").text

    # === Gabungkan jadi format folder ===
    folder_name = f"{judul} - {penulis}"

    # === Bersihkan karakter ilegal di nama folder ===
    for c in r'\/:*?"<>|':
        folder_name = folder_name.replace(c, "")
    
    # === Buat folder hasil ===
    folder_name = os.path.join("hasil", folder_name)
    os.makedirs(folder_name, exist_ok=True)
    
    baca_button = driver.find_element(By.CSS_SELECTOR, "button.ant-btn.button-read")
    baca_button.click()
    time.sleep(9 + sleep_time)
    
    print("Folder:  ", folder_name)
    
    return folder_name


# =========================================================
# === FUNGSI: SCREENSHOT MODE =============================
# =========================================================
def screenshot_pages(driver, folder_name, zoom, pd, jumlah):
    body = driver.find_element(By.TAG_NAME, "body")

    
    
    for _ in range(zoom):
        zoom_in_btn = driver.find_element(By.CSS_SELECTOR, "button[data-testid='zoom__in-button']")
        zoom_in_btn.click()
        time.sleep(0.5)

    element = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Page 1']")
    ActionChains(driver).move_to_element(element).perform()
    time.sleep(3)

    for _ in range(pd):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    if pd:
        time.sleep(9)
    
    jumlah = jumlah - pd
    try:

        
        # Jika jumlah halaman ditentukan lewat -j
        if jumlah:
            print(f"Jumlah -j: {jumlah}")
        else:
            # Jika tidak ada -j, hitung div dan tampilkan hasilnya
            # Ambil semua div dengan kelas 'rpv-thumbnail__container'
            divs = driver.find_elements(By.CLASS_NAME, 'rpv-thumbnail__container')
            
            # Hitung jumlah div yang ditemukan
            jumlah = len(divs)
            print(f"Jumlah page:{jumlah}")
            print()
        
    except Exception as e:
        print(f"Error: {e}")
    
    
    for i in range(jumlah):
        file_name = os.path.join(folder_name, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.png")
        png_data = driver.get_full_page_screenshot_as_png()
        image = Image.open(BytesIO(png_data)).convert('RGB')
        image.save(file_name, "PNG")

        print(f"Screenshot {i+1}/{jumlah} tersimpan: {file_name}")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1.4)


# =========================================================
# === FUNGSI: EPUB MODE ===================================
# =========================================================
def epub_pages(driver, folder_name, jumlah):
    wait = WebDriverWait(driver, 15)

    svg_elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[viewBox="0 0 48 48"]')))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", svg_elem)
    time.sleep(0.3)
    svg_elem.click()

    for i in range(jumlah):
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.epub-view iframe")))
        srcdoc_html = iframe.get_attribute("srcdoc")

        filename = os.path.join(folder_name, f"iframe_content_{i+1}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(srcdoc_html)
        print(f"Halaman {i+1}/{jumlah} disimpan: {filename}")

        try:
            svg_elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.tabler-icon-chevron-right")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center', inline:'center'});", svg_elem)
            time.sleep(0.3)
            svg_elem.click()
            time.sleep(1)
        except:
            print(f"Tidak bisa klik tombol Next di halaman {i+1}. Berhenti.")
            break


# =========================================================
# === FUNGSI: perser  =======================================
# =========================================================

def get_args():
    parser = argparse.ArgumentParser(description="Script Screenshot iPusnas")
    parser.add_argument("-l", "--link", required=True, help="Link iPusnas")
    # parser.add_argument("-f", "--folder", required=True, help="Nama folder hasil")
    parser.add_argument("-j", "--jumlah", type=int, help="Jumlah halaman")
    parser.add_argument("-s", "--sleeps", type=int, default=0, help="Tambahan waktu sleep")
    parser.add_argument("--epub", action="store_true", help="Aktifkan mode EPUB")
    parser.add_argument("-H", "--headless", action="store_false", help="Aktifkan mode headless")
    parser.add_argument("-z", "--zoom", type=int, default=9, help="Zoom halaman")
    parser.add_argument("--pd", type=int, default=0, help="Jumlah PageDown awal")

    return parser.parse_args()


# =========================================================
# === FUNGSI: UTAMA =======================================
# =========================================================
def main():

    args = get_args()
    driver = setup_driver(headless=args.headless)

    try:
        folder_name = login_ipusnas(driver, args.link, sleep_time=args.sleeps)
        if args.epub:
            epub_pages(driver, folder_name, args.jumlah)
        else:
            screenshot_pages(driver, folder_name, args.zoom, args.pd, args.jumlah)

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

    finally:
        driver.quit()


# =========================================================
# === ENTRY POINT =========================================
# =========================================================
if __name__ == "__main__":
    main()
