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
import json
from urllib.parse import urljoin

# =======================================
# membuka chrome dengan headless mode
# =======================================
def start_chrome_headless():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--no-sandbox')
    
    user_data_dir = r"C:\chrome_selenium"
    options.add_argument(f'--user-data-dir={user_data_dir}')
    
    profile_dir = "Default"
    options.add_argument(f'--profile-directory={profile_dir}')
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("✅ Chrome berjalan dalam headless mode")
        driver.implicitly_wait(5)
        return driver
    except Exception as e:
        print(f"Error saat menginisialisasi Chrome: {e}")



# ============================================================
# Fungsi 1️⃣ - Buka Chrome Remote Debugging
# ============================================================
def start_chrome():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\chrome_selenium"
    debug_port = 9222

    # Cek apakah port sudah dipakai
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



    options = webdriver.ChromeOptions()
    options.debugger_address = f"127.0.0.1:{debug_port}"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("✅ Terhubung ke Chrome")
    driver.implicitly_wait(5)
    return driver
    
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
    # domain = parsed.netloc

    print(f"\nLink: {link_malakabooks}")
    return link_malakabooks



####################################
# Fungsi untuk memuat semua data buku
####################################
def click_load_more(driver):

    # Tunggu agar halaman dimuat (bisa menggunakan WebDriverWait jika diperlukan)
    time.sleep(2)  # Ganti dengan WebDriverWait jika perlu menunggu elemen tampil

    while True:
        try:
            # Menggunakan XPath untuk mencari tombol berdasarkan teks yang ada di dalamnya
            load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Muat lebih banyak')]")
            
            # Klik tombol
            load_more_button.click()

            # Tunggu sejenak untuk memuat lebih banyak konten
            time.sleep(2)
            print("✅ Tombol 'Muat lebih banyak' telah diklik.")
        except Exception as e:
            # Jika tombol tidak ditemukan (misalnya, sudah tidak ada lagi), keluar dari loop
            print("❌ Tidak ada tombol 'Muat lebih banyak' lagi atau tombol tidak bisa diklik.")
            break  # Keluar dari loop jika tombol tidak ditemukan atau gagal diklik

# Fungsi untuk mengambil semua link buku, nama buku, dan link profil penulis
def get_books_data(driver, link):
    base_url = link
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # Cari semua card buku (selector sesuai contoh HTMLmu)
    book_elements = soup.find_all('div', class_='flex flex-col gap-4 relative min-w-0')

    books = []
    for book in book_elements:
        # Default values
        book_link = None
        book_title = None
        author_profile_link = None
        author_name = None
        category = None

        # Ambil link buku
        a_book = book.find('a', href=True)
        if a_book:
            book_link = a_book['href']
            if base_url:
                book_link = urljoin(base_url, book_link)

        # Ambil judul
        h3 = book.find('h3')
        if h3:
            book_title = h3.get_text(strip=True)

        # Ambil link dan nama penulis (dalam scope elemen book)
        a_author = book.find('a', href=lambda x: x and '/author/' in x)
        if a_author:
            author_profile_link = a_author.get('href')
            if base_url:
                author_profile_link = urljoin(base_url, author_profile_link)
            author_name = a_author.get_text(strip=True)

        # Ambil kategori (span dengan class text-[11px])
        span_category = book.find('span', class_='text-[11px]')
        if span_category:
            category = span_category.get_text(strip=True)

        # Tambahkan ke list
        books.append({
            'book_link': book_link,
            'book_title': book_title,
            'author_name': author_name,
            'author_profile_link': author_profile_link,
            'category': category
        })

    return books

# Fungsi untuk menyimpan data buku ke dalam file JSON
def save_books_to_json(books, filename='books_data.json'):
    with open(filename, 'w') as f:
        json.dump(books, f, indent=4)
    print(f"✅ Data buku berhasil disimpan ke {filename}!")
    
    

# ============================================================
# MAIN
# ============================================================
def main():
    # link = get_link_from_args()
    link = "https://malakabooks.id/explore"
    driver = start_chrome()
    # driver = start_chrome_headless()
    driver.get(link)
    click_load_more(driver)
    time.sleep(3)
    books_data = get_books_data(driver, link)
    save_books_to_json(books_data)
    # driver.quit()

if __name__ == "__main__":
    main()