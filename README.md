# **README.md – iPusnas Screenshot & EPUB Downloader**  

**Perpus downloader. Script python otomatis digunakan untuk mengambil screenshot buku-buku atau menyimpan html dari epub yang dipinjam dari ipusnas dan aplikasi web sejenis dari pengembang Aksaramaya.**

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Selenium](https://img.shields.io/badge/selenium-4.x-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Status](https://img.shields.io/badge/status-aktif-brightgreen)

---

## Fitur Utama

| Fitur                              | Keterangan                                                                 |
|------------------------------------|-----------------------------------------------------------------------------|
| Screenshot seluruh halaman buku   | Full-page screenshot (2160×3200) dengan zoom otomatis                      |
| Mode EPUB (srcdoc)                 | Simpan isi iframe tiap halaman sebagai `.html` (bisa dikonversi ke PDF)   |
| Login otomatis                     | Menggunakan email + password dari file `.env`                              |
| Nama folder otomatis               | `Judul Buku - Penulis` (karakter ilegal dibersihkan)                      |
| Custom jumlah halaman              | Bisa batasi dengan `-j` atau otomatis deteksi semua halaman               |
| Zoom otomatis                      | Default 9× zoom (`-z`) agar teks terbaca jelas                             |
| Skip halaman awal                  | `--pd` untuk skip beberapa halaman pertama                                |
| Headless / GUI mode                | `--headless` (default) atau `-H` untuk tampilkan browser                   |
| Tambahan sleep                     | `-s` untuk tambah delay (berguna jika koneksi lambat / sering timeout)    |

---

## Prasyarat (Dependencies)

```bash
pip install selenium pillow python-dotenv
```

Pastikan kamu sudah menginstall **GeckoDriver** (untuk Firefox) dan Firefox terinstall.

### Cara install GeckoDriver (Windows / Linux / macOS)

```bash
# Paling mudah: gunakan geckodriver-autoinstaller
pip install geckodriver-autoinstaller
```

Atau download manual dari: https://github.com/mozilla/geckodriver/releases

---

## Struktur Folder

```
project/
│
├── ipusnas.py               ← Script utama
├── .env                     ← Simpan email & password (jangan di-commit!)
├── hasil/                   ← Folder hasil otomatis dibuat
│   └── Judul Buku - Penulis/
│       ├── 20250405_102345_1.png
│       ├── 20250405_102346_2.png
│       └── ...
└── README.md
```

### Contoh isi `.env`

```env
EMAIL=contoh@email.com
PASSWORD=rahasiamu123
```

---

## Cara Pakai

### 1. Screenshot Mode (Default)

```bash
python ipusnas.py -l "https://e-resources.perpusnas.go.id/book/123456"
```

### 2. Dengan opsi lengkap

```bash
python ipusnas.py \
  -l "https://e-resources.perpusnas.go.id/book/123456" \
  -f "Nama Folder Custom" \
  -j 150 \
  -s 2 \
  -z 10 \
  --pd 5 \
  -H
```

### 3. Mode EPUB (simpan srcdoc iframe)

```bash
python ipusnas.py -l "https://e-resources.perpusnas.go.id/book/123456" --epub -j 200
```

---

## Daftar Argumen (Command Line Options)

| Argumen         | Alias | Tipe     | Default | Keterangan |
|----------------|-------|----------|---------|-----------|
| `-l`, `--link` |       | string   | **wajib** | Link buku iPusnas |
| `-f`, `--folder` |     | string   | -       | Nama folder hasil (kosongkan = otomatis) |
| `-j`, `--jumlah` |    | int      | auto    | Jumlah halaman yang ingin diambil |
| `-s`, `--sleeps` |    | int      | 0       | Tambahan delay (detik) |
| `--epub`       |       | flag     | False   | Aktifkan mode simpan HTML iframe |
| `-H`, `--headless` |  | flag     | True    | Matikan headless (tampilkan browser) |
| `-z`, `--zoom` |       | int      | 9       | Berapa kali klik tombol zoom in |
| `--pd`         |       | int      | 0       | Skip berapa halaman di awal (PageDown) |

---

## Tips & Trik

1. **Koneksi lambat / sering timeout?** → Tambah `-s 3` atau `-s 5`
2. **Ingin hasil lebih tajam?** → Naikkan `-z 12` atau lebih
3. **Buku lebih dari 300 halaman?** → Gunakan `-j 300` agar tidak terlalu lama
4. **Mau simpan sebagai PDF?**  
   → Setelah selesai screenshot → gunakan tool seperti `img2pdf` atau NAPS2
5. **Mode EPUB** → File `.html` bisa dibuka di browser atau dikonversi ke PDF dengan `weasyprint` / `wkhtmltopdf`

---

## Contoh Output di Terminal

```
Link: https://e-resources.perpusnas.go.id/book/123456

Folder:   hasil/Pemrograman Python Untuk Pemula - John Doe
mulai dari halaman:  6
Jumlah page: 145

Screenshot 1/145 tersimpan: hasil/Pemrograman Python Untuk Pemula - John Doe/20250405_102345_1.png
Screenshot 2/145 tersimpan: hasil/.../20250405_102346_2.png
...
 _______
< Done! >
 -------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

---

## Catatan Penting

- Script ini **hanya untuk keperluan pribadi / pendidikan**.
- Hormati hak cipta dan ketentuan penggunaan iPusnas.
- Jangan gunakan untuk mengunduh massal atau komersial.
- Gunakan dengan bijak

---

## Kontribusi

Ingin membantu?

- Laporkan bug / request fitur di Issues
- Pull Request sangat diterima (misal: dukungan Chrome, konversi otomatis ke PDF, GUI, dll.)

---

**Terima kasih sudah menggunakan script ini!**  
Semoga membantu studi, penelitian, atau baca buku tanpa koneksi internet

Made with di Indonesia  
Dibuat dengan Python + Selenium + banyak kopi

--- 

**Happy reading!**  
*“Baca buku, bukan cuma notif WhatsApp.”*