import json
import subprocess

# Membaca file JSON
def load_json(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)

# Fungsi untuk memeriksa buku yang perlu diunduh
def check_and_download_books(data_file='data.json', downloaded_file='downloaded_books.json'):
    # Memuat data dari file JSON
    data_books = load_json(data_file)
    downloaded_books = load_json(downloaded_file)
    
    # Ambil link buku yang sudah diunduh (dari downloaded_books.json)
    downloaded_links = downloaded_books.keys()  # Kita ambil link sebagai kunci
    
    # Memulai proses unduhan untuk setiap buku yang ada di data.json
    for book in data_books:
        book_link = book['link']

        # Jika buku sudah diunduh (ada di downloaded_books.json), skip buku ini
        if book_link in downloaded_links:
            print(f"⚠️ Buku dengan link {book_link} sudah diunduh, melanjutkan ke buku berikutnya.")
            continue
        
        # Jika buku belum diunduh, jalankan malaka6.py untuk mengunduhnya
        print(f"📥 Mengunduh buku {book_link}...")
        
        # Menjalankan malaka6.py dengan subprocess dan argumen -l untuk link buku
        subprocess.run(["python", "malaka6.py", "-l", book_link])  # Sesuaikan dengan cara malaka6.py menerima link buku

        # Setelah mendownload, tambahkan buku ke downloaded_books.json
        # Data buku yang diunduh
        downloaded_books[book_link] = {
            "author": book["author"],
            "title": book["title"],
            "main_folder": "hasil",  # Sesuaikan jika perlu
            "folder": f"hasil/{book['title']}",
            "epub_name": f"{book['title']} - {book['author']} - MalakaBooks.epub"
        }

        # Simpan kembali updated downloaded_books.json
        with open(downloaded_file, 'w') as f:
            json.dump(downloaded_books, f, indent=4)
        
    print("✅ Proses unduhan selesai.")
