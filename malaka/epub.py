import os
from ebooklib import epub
from bs4 import BeautifulSoup

# --- Lokasi folder hasil ---
base_dir = r"C:\Users\ehe\Documents\perpus\malaka\hasil"
book_folder = "Pertanyaan Kecil_ Jawaban Besar_ Evolusi di Kebun Binatang"
book_path = os.path.join(base_dir, book_folder)

# --- Nama file output EPUB ---
output_file = os.path.join(base_dir, f"{book_folder}.epub")

# --- Buat objek EPUB ---
book = epub.EpubBook()

# --- Set metadata ---
nama_penulis = "Adrian Danar"
book.set_identifier("id123456")
book.set_title(book_folder)
book.set_language("id")
book.add_author(nama_penulis)
book.add_metadata("DC", "publisher", "MalakaBooks")

# --- Tambahkan cover ---
cover_path = os.path.join(book_path, "cover.png")
if os.path.exists(cover_path):
    with open(cover_path, "rb") as f:
        book.set_cover("cover.png", f.read())
    print("✅ Cover ditambahkan")
else:
    print("⚠️ Tidak menemukan cover.png")

# --- Ambil semua file HTML ---
# --- Ambil semua file HTML ---
html_files = sorted(
    [f for f in os.listdir(book_path)
     if f.lower().endswith(".html") and f.lower().startswith("chapter")],
    key=lambda x: int(x.split(" ")[1].split("–")[0])  # Urut berdasarkan nomor setelah "CHAPTER"
)

# --- Tambahkan setiap file HTML ke EPUB ---
spine = []
chapters_list = []

for html_file in html_files:
    file_path = os.path.join(book_path, html_file)
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    # Ambil judul dari h1 atau fallback ke nama file
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

# --- Tambahkan stylesheet sederhana ---
style = '''
body { font-family: "Helvetica", sans-serif; line-height: 1.5; }
h1 { text-align: center; }
img { max-width: 100%; height: auto; display: block; margin: auto; }
'''
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css",
                        media_type="text/css", content=style)
book.add_item(nav_css)

# --- Tambahkan item navigasi EPUB ---
book.add_item(epub.EpubNcx())
nav = epub.EpubNav()
book.add_item(nav)

# --- Atur urutan spine dan TOC ---
# Spine = urutan baca
# Kita ingin nav.xhtml (daftar isi bawaan EPUB) setelah Chapter 0
if len(chapters_list) > 1:
    book.spine = [chapters_list[0], nav] + chapters_list[1:]
else:
    book.spine = chapters_list

# TOC = semua bab
book.toc = tuple(chapters_list)

# --- Simpan EPUB ---
epub.write_epub(output_file, book, {})
print(f"🎉 EPUB berhasil dibuat: {output_file}")