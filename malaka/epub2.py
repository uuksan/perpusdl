import os
from ebooklib import epub
from bs4 import BeautifulSoup

def create_epub_from_folder(folder_path, epub_file_name):
    # Membuat objek buku EPUB
    book = epub.EpubBook()

    # Menambahkan metadata (judul, penulis)
    book.set_title('Pertanyaan Kecil_ Jawaban Besar_ Evolusi di Kebun Binatang')
    book.add_author('Adrian Danar')

    # Menambahkan cover
    cover_path = os.path.join(folder_path, 'cover.png')
    if os.path.exists(cover_path):
        with open(cover_path, 'rb') as cover_file:
            cover_data = cover_file.read()
        cover_item = epub.EpubItem(
            uid='cover',
            file_name='cover.png',
            media_type='image/png',
            content=cover_data
        )
        book.add_item(cover_item)
        book.set_cover('cover.png', cover_data)

    # Menambahkan HTML dari folder
    html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
    html_files.sort()  # Mengurutkan file HTML jika perlu

    spine = ['cover']  # Menetapkan urutan yang harus dibaca pertama kali (cover)
    for i, html_file in enumerate(html_files):
        with open(os.path.join(folder_path, html_file), 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Menggunakan BeautifulSoup untuk membersihkan dan menyesuaikan HTML jika perlu
        soup = BeautifulSoup(html_content, 'html.parser')
        for img_tag in soup.find_all('img'):
            img_tag['src'] = os.path.basename(img_tag['src'])

        # Menambahkan HTML sebagai item EPUB
        item = epub.EpubItem(
            uid=f'html_{i}',
            file_name=f'html_{i}.xhtml',
            media_type='application/xhtml+xml',
            content=soup.prettify().encode('utf-8')
        )
        book.add_item(item)
        spine.append(item)

    # Menetapkan spine (urutan pembacaan)
    book.spine = spine

    # Menambahkan TOC (Table of Contents)
    book.toc = [(epub.Section('Section 1'), [book.get_item_with_id(f'html_{i}') for i in range(len(html_files))])]

    # Menambahkan NCX dan opf
    book.add_item(epub.EpubNav())

    # Menyimpan buku EPUB
    epub.write_epub(epub_file_name, book)

    print(f"EPUB telah berhasil dibuat dengan nama: {epub_file_name}")


# Ganti dengan folder yang sesuai yang berisi cover.png dan file HTML
folder_path = r"C:\Users\ehe\Documents\perpus\malaka\hasil"
epub_file_name = 'output_book.epub'

create_epub_from_folder(folder_path, epub_file_name)
