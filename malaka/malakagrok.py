import json
import subprocess
import logging
import os

# Setup logging sederhana
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json(file_name):
    """
    Memuat file JSON dengan error handling.
    """
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File {file_name} tidak ditemukan.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Format JSON di {file_name} invalid.")
        raise

def save_json(file_name, data):
    """
    Simpan data ke file JSON dengan indentasi.
    """
    try:
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"File {file_name} berhasil disimpan.")
    except Exception as e:
        logger.error(f"Gagal menyimpan {file_name}: {e}")
        raise

def process_books(data_file='books_data.json', downloaded_file='downloaded_books.json'):
    """
    Fungsi utama: Proses buku dari data.json, cek di downloaded_books.json, 
    unduh jika belum, lalu update jika sukses.
    """
    # Muat data
    data_books = load_json(data_file)
    downloaded_books = load_json(downloaded_file)
    
    # Ambil link yang sudah diunduh (gunakan set untuk pencarian cepat)
    downloaded_links = set(downloaded_books.keys())
    
    # Loop melalui setiap buku di data.json
    for book in data_books:
        book_link = book.get('book_link')
        if not book_link:
            logger.warning(f"Buku tanpa link: {book.get('book_title', 'Unknown')}. Dilewati.")
            continue
        
        # Skip jika link sudah ada di downloaded_books.json
        if book_link in downloaded_links:
            logger.info(f"⚠️ Buku dengan link {book_link} sudah diunduh, dilewati.")
            continue
        
        # Jalankan malaka6.py untuk unduh
        logger.info(f"📥 Mengunduh buku {book_link}...")
        print("book_link: ", book_link)
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            result = subprocess.run(
                ["python", "malaka6.py", "-l", book_link],
                capture_output=True,
                text=True,
                check=True,  # Raise error jika gagal
                env=env  # Tambahkan ini
            )
            logger.debug(f"Output dari malaka6.py: {result.stdout}")
            
            # Jika sukses, tambahkan entry ke downloaded_books.json
            # title = book.get('book_title', 'Unknown')
            # author = book.get('author_name', 'Unknown')
            # downloaded_books[book_link] = {
                # "author": author,
                # "title": title,
                # "main_folder": "hasil",
                # "folder": f"hasil/{title}",
                # "epub_name": f"{title} - {author} - MalakaBooks.epub"
            # }
            # save_json(downloaded_file, downloaded_books)
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Gagal mengunduh {book_link}: {e.stderr}")
        except Exception as e:
            logger.error(f"Error tak terduga saat unduh {book_link}: {e}")
    
    logger.info("✅ Proses selesai.")

if __name__ == "__main__":
    process_books()