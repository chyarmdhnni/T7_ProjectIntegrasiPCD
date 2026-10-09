# T7_ProjectIntegrasiPCD - Integrasi OCR Nomor Ijazah dan Deteksi Tanda Tangan

## Deskripsi

Mini project ini merupakan implementasi integrasi pengolahan citra digital untuk membantu proses verifikasi informasi pada dokumen ijazah.

Sistem melakukan peningkatan kualitas citra nomor ijazah menggunakan beberapa metode *image enhancement*, membaca nomor ijazah menggunakan Optical Character Recognition (OCR), serta mendeteksi keberadaan tanda tangan menggunakan teknik thresholding dan operasi morfologi.

Tahapan pengolahan citra yang digunakan meliputi:

* Konversi citra ke grayscale
* Brightness Adjustment
* Contrast Stretching
* Histogram Equalization
* Pembesaran citra dan Gaussian Blur sebelum OCR
* Pengenalan nomor ijazah menggunakan Tesseract OCR
* Evaluasi hasil OCR menggunakan Character Error Rate (CER)
* Otsu Thresholding untuk pemrosesan area tanda tangan
* Operasi morfologi Opening
* Analisis komponen dan perhitungan foreground pixel
* Penentuan keberadaan tanda tangan
* Visualisasi dan perbandingan hasil pengolahan citra

Pada project ini, pengujian dilakukan menggunakan citra potongan area nomor ijazah dan area tanda tangan dari dokumen ijazah.

## Teknologi yang Digunakan

* Python
* OpenCV
* NumPy
* Pandas
* Matplotlib
* Tesseract OCR

---

## How to Run

### 1. Clone Repository

Buka Command Prompt atau PowerShell, kemudian jalankan:

```bash
git clone https://github.com/chyarmdhnni/T7_ProjectIntegrasiPCD.git
```

Ganti `USERNAME` dengan username GitHub dan sesuaikan nama repository jika berbeda.

Kemudian masuk ke folder project:

```bash
cd T7_ProjectIntegrasiPCD
```

### 2. Install Library

Install library yang diperlukan dengan perintah:

```bash
pip install opencv-python numpy pandas matplotlib pytesseract
```

### 3. Install Tesseract OCR

Program menggunakan Tesseract OCR untuk membaca nomor ijazah.

Unduh dan instal Tesseract OCR terlebih dahulu. Pastikan lokasi instalasinya sesuai dengan konfigurasi pada `main.py`.

Contoh lokasi instalasi:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Jika Tesseract terinstal di lokasi berbeda, sesuaikan path pada program.

### 4. Siapkan Dataset

Pastikan folder dataset tersedia dengan struktur berikut:

```text
T7_ProjectIntegrasiPCD/
├── main.py
├── README.md
├── citra ijazah/
│   ├── Nomor Ijazah/
│   └── Tanda Tangan/
└── hasil/
```

Folder `Nomor Ijazah` berisi sembilan citra pengujian nomor ijazah, sedangkan folder `Tanda Tangan` berisi sembilan citra pengujian tanda tangan.

Pastikan nama folder dan lokasi dataset sesuai dengan konfigurasi pada `main.py`.

### 5. Jalankan Program

Jalankan program dengan perintah:

```bash
python main.py
```

Program akan memproses citra, menampilkan hasil OCR dan deteksi tanda tangan, serta menyimpan hasil pengolahan pada folder `hasil/`.

---

## Hasil Pengolahan

Program melakukan beberapa tahapan pengolahan citra:

* Grayscale
* Brightness Adjustment
* Contrast Stretching
* Histogram Equalization
* OCR menggunakan Tesseract
* Perhitungan Character Error Rate (CER)
* Otsu Thresholding
* Operasi morfologi Opening
* Deteksi keberadaan tanda tangan

Hasil pengolahan disimpan pada folder:

`hasil/`

---

## Metode yang Digunakan

* **Grayscale**

  Mengubah citra berwarna menjadi citra skala keabuan untuk mempermudah proses pengolahan berikutnya.

* **Brightness Adjustment**

  Menyesuaikan tingkat kecerahan citra agar karakter pada nomor ijazah lebih mudah dikenali oleh OCR.

* **Contrast Stretching**

  Memperluas rentang intensitas piksel untuk meningkatkan perbedaan antara karakter dan latar belakang.

* **Histogram Equalization**

  Mendistribusikan intensitas piksel untuk meningkatkan kontras citra berdasarkan histogram.

* **Optical Character Recognition (OCR)**

  Menggunakan Tesseract OCR untuk mengenali karakter angka pada citra nomor ijazah.

* **Character Error Rate (CER)**

  Digunakan untuk mengevaluasi hasil OCR dengan membandingkan teks hasil pengenalan dan nomor ijazah acuan. Semakin rendah nilai CER, semakin baik hasil pengenalan karakter.

* **Otsu Thresholding**

  Menentukan nilai ambang secara otomatis berdasarkan distribusi intensitas piksel untuk memisahkan tanda tangan dari latar belakang.

* **Morfologi Opening**

  Membantu mengurangi noise kecil pada hasil thresholding.

* **Analisis Foreground Pixel**

  Menganalisis piksel tinta dan komponen citra sebagai salah satu dasar penentuan keberadaan tanda tangan.

---

## Output

Output program berupa:

* Citra hasil grayscale
* Citra hasil Brightness Adjustment
* Citra hasil Contrast Stretching
* Citra hasil Histogram Equalization
* Hasil pembacaan nomor ijazah menggunakan OCR
* Nilai CER untuk setiap metode enhancement
* Citra hasil thresholding tanda tangan
* Citra hasil operasi morfologi
* Visualisasi verifikasi nomor ijazah dan tanda tangan
* Status deteksi (`SIGNATURE PRESENT` / `SIGNATURE ABSENT`)
* File `perbandingan_enhancement_ocr.csv`
* File `pengujian_9_citra_kosong.csv`

---

## Hasil Evaluasi OCR

Berdasarkan pengujian terhadap sembilan citra nomor ijazah, diperoleh rata-rata CER sebagai berikut:

| Metode Enhancement | Rata-rata CER |
|---|---:|
| Brightness Adjustment | 11,85% |
| Contrast Stretching | 21,48% |
| Histogram Equalization | 100,00% |

Berdasarkan hasil tersebut, **Brightness Adjustment merupakan metode terbaik pada dataset pengujian ini**, karena menghasilkan rata-rata CER paling rendah, yaitu 11,85%.

Hasil evaluasi ini berlaku untuk dataset yang digunakan dan tidak secara langsung mewakili kinerja OCR pada seluruh jenis dokumen ijazah.

## Pengujian Deteksi Tanda Tangan

Pengujian dilakukan terhadap sembilan citra area tanda tangan dan sembilan citra putih kosong yang dibuat oleh program sebagai pengujian dasar.

Hasil pengujian:

* Sembilan citra area tanda tangan terdeteksi sebagai `SIGNATURE PRESENT`.
* Sembilan citra putih kosong terdeteksi sebagai `SIGNATURE ABSENT`.

Pengujian citra putih kosong merupakan pengujian dasar. Pengujian tambahan menggunakan citra ijazah nyata tanpa tanda tangan diperlukan untuk mengevaluasi kemampuan deteksi pada kondisi sebenarnya.

---

## Dataset

Dataset terdiri dari beberapa citra potongan area nomor ijazah dan area tanda tangan dengan kondisi kualitas citra yang berbeda.

Contoh variasi kualitas citra yang diuji meliputi:

* High Quality
* Low Contrast
* Blurred
* High Noise
* Low Resolution
* Faded / Underexposed
* Color Shift
* JPEG Compression
* Combined Degradation

---

## Author

* **Nama:** Cahaya Ramadhani
* **NIM:** F1G124059
* **Mata Kuliah:** Pengolahan Citra Digital
* **Universitas:** Universitas Halu Oleo
