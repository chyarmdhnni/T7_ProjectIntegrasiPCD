from pathlib import Path
import argparse
import csv
import re
import sys
import cv2
import numpy as np
import pandas as pd
import pytesseract
import matplotlib.pyplot as plt

from pathlib import Path

# Lokasi Tesseract di laptop kamu

pytesseract.pytesseract.tesseract_cmd = (
r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
print("Lokasi Tesseract:", pytesseract.pytesseract.tesseract_cmd)
print("Versi Tesseract:", pytesseract.get_tesseract_version())

# =========================================================
# 1. KONFIGURASI FOLDER
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

NOMOR_DIR = BASE_DIR / "Nomor Ijazah"
TANDA_TANGAN_DIR = BASE_DIR / "Tanda Tangan"
KOSONG_DIR = BASE_DIR / "Tanda Tangan Kosong"
OUTPUT_DIR = BASE_DIR / "Hasil"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GROUND_TRUTH_NUMBER = "571012022000056"

EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def natural_key(path):
    return [int(x) if x.isdigit() else x.lower()
            for x in re.split(r"(\d+)", path.name)]


def get_images(folder):
    if not folder.exists():
        raise FileNotFoundError(f"Folder tidak ditemukan: {folder}")
    return sorted(
        [p for p in folder.iterdir()
         if p.is_file() and p.suffix.lower() in EXTENSIONS],
        key=natural_key
    )


def read_gray(path):
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Citra gagal dibaca: {path}")
    return image, cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# =========================================================
# 2. TIGA METODE IMAGE ENHANCEMENT
# =========================================================
def brightness_adjustment(gray, beta=25):
    # beta positif membuat citra lebih terang
    return cv2.convertScaleAbs(gray, alpha=1.0, beta=beta)


def contrast_stretching(gray):
    low, high = np.percentile(gray, (2, 98))
    if high <= low:
        return gray.copy()
    stretched = (gray.astype(np.float32) - low) * (255.0 / (high - low))
    return np.clip(stretched, 0, 255).astype(np.uint8)


def histogram_equalization(gray):
    return cv2.equalizeHist(gray)


def perform_ocr(gray):
    # Memperbesar citra agar karakter lebih mudah dibaca OCR.
    enlarged = cv2.resize(
        gray,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    # Mengurangi noise tanpa menghilangkan terlalu banyak detail.
    denoised = cv2.GaussianBlur(enlarged, (3, 3), 0)

    # OCR hanya membaca angka karena nomor ijazah berupa digit.
    config = (
        "--oem 3 --psm 7 "
        "-c tessedit_char_whitelist=0123456789"
    )

    text = pytesseract.image_to_string(
        denoised,
        config=config
    )

    return re.sub(r"\D", "", text)


def edit_distance(reference, prediction):
    previous_row = list(range(len(prediction) + 1))
    for row_index, reference_char in enumerate(reference, start=1):
        current_row = [row_index]
        for column_index, prediction_char in enumerate(prediction, start=1):
            insertion = current_row[column_index - 1] + 1
            deletion = previous_row[column_index] + 1
            substitution = previous_row[column_index - 1] + (
                reference_char != prediction_char
            )
            current_row.append(min(insertion, deletion, substitution))
        previous_row = current_row
    return previous_row[-1]


def character_error_rate(reference, prediction):
    if not reference:
        raise ValueError("Ground truth tidak boleh kosong untuk menghitung CER.")
    return edit_distance(reference, prediction) / len(reference)


# =========================================================
# 3. SIGNATURE DETECTION
# =========================================================
def detect_signature(gray, min_ink_pixels=80, min_ink_ratio=0.001):
    """
    Deteksi heuristik sederhana berdasarkan tinta.
    Pastikan crop gambar tanda tangan hanya berisi area tanda tangan.
    Ambang perlu disesuaikan dengan ukuran/kualitas citra.
    """
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        cleaned, connectivity=8
    )
    filtered = np.zeros_like(cleaned)
    for i in range(1, count):
        if stats[i, cv2.CC_STAT_AREA] >= 8:
            filtered[labels == i] = 255

    ink_pixels = cv2.countNonZero(filtered)
    total_pixels = filtered.shape[0] * filtered.shape[1]
    ink_ratio = ink_pixels / max(total_pixels, 1)

    present = (
        ink_pixels >= min_ink_pixels
        and ink_ratio >= min_ink_ratio
    )
    status = "SIGNATURE PRESENT" if present else "SIGNATURE ABSENT"
    return status, binary, filtered, ink_pixels, ink_ratio


# =========================================================
# 4. MEMBUAT 9 CITRA KOSONG SEBAGAI DATA PEMBANDING
# =========================================================
def create_blank_examples(reference_images):
    KOSONG_DIR.mkdir(exist_ok=True)

    if not reference_images:
        print("Tidak ada citra referensi untuk menentukan ukuran citra kosong.")
        return []

    blank_paths = []
    for i, path in enumerate(reference_images[:9], start=1):
        _, gray = read_gray(path)
        blank = np.full(gray.shape, 255, dtype=np.uint8)
        blank_path = KOSONG_DIR / f"kosong_{i:02d}.png"
        cv2.imwrite(str(blank_path), blank)
        blank_paths.append(blank_path)

    return blank_paths


# =========================================================
# 5. VISUALISASI SETIAP IJAZAH
# =========================================================
def visualize_one(index, number_path, signature_path):
    original, gray = read_gray(number_path)
    methods = {
        "Brightness Adjustment": brightness_adjustment(gray),
        "Contrast Stretching": contrast_stretching(gray),
        "Histogram Equalization": histogram_equalization(gray),
    }

    ocr_results = {
        name: perform_ocr(enhanced)
        for name, enhanced in methods.items()
    }
    cer_results = {
        name: character_error_rate(GROUND_TRUTH_NUMBER, text)
        for name, text in ocr_results.items()
    }

    chosen_method = min(cer_results, key=cer_results.get)
    chosen_text = ocr_results[chosen_method]
    chosen_cer = cer_results[chosen_method]

    _, signature_gray = read_gray(signature_path)
    sig_status, sig_binary, sig_cleaned, ink_pixels, ink_ratio = (
        detect_signature(signature_gray)
    )

    # Simpan hasil enhancement dan hasil deteksi.
    for name, enhanced in methods.items():
        safe_name = name.lower().replace(" ", "_")
        cv2.imwrite(
            str(OUTPUT_DIR / f"{number_path.stem}_{safe_name}.png"),
            enhanced
        )

    cv2.imwrite(
        str(OUTPUT_DIR / f"{signature_path.stem}_signature_threshold.png"),
        sig_binary
    )
    cv2.imwrite(
        str(OUTPUT_DIR / f"{signature_path.stem}_signature_morphology.png"),
        sig_cleaned
    )

    # Panel gambar: asli, grayscale, tiga enhancement, tanda tangan.
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle(
        f"Verifikasi Ijazah {index} — {number_path.name}",
        fontsize=15, fontweight="bold"
    )

    panels = [
        ("Citra Asli (Nomor)", cv2.cvtColor(original, cv2.COLOR_BGR2RGB)),
        ("Grayscale (Nomor)", gray),
        ("Brightness Adjustment", methods["Brightness Adjustment"]),
        ("Contrast Stretching", methods["Contrast Stretching"]),
        ("Histogram Equalization", methods["Histogram Equalization"]),
        ("Signature Detection", sig_cleaned),
    ]

    for ax, (title, image) in zip(axes.flat, panels):
        ax.imshow(image, cmap="gray" if image.ndim == 2 else None)
        ax.set_title(title)
        ax.axis("off")

    fig.text(
        0.03, 0.015,
        f"OCR ({chosen_method}): {chosen_text or 'TIDAK TERBACA'} "
        f"| CER: {chosen_cer:.2%}\n"
        f"Tanda tangan: {sig_status} | "
        f"Piksel tinta: {ink_pixels} | Rasio tinta: {ink_ratio:.5f}",
        fontsize=11, va="bottom"
    )
    plt.tight_layout(rect=[0, 0.08, 1, 0.93])
    fig.savefig(
        OUTPUT_DIR / f"visualisasi_verifikasi_{index:02d}.png",
        dpi=160, bbox_inches="tight"
    )
    plt.show()
    plt.close(fig)

    rows = []
    for name, text in ocr_results.items():
        rows.append({
            "No": index,
            "Citra Nomor": number_path.name,
            "Metode Enhancement": name,
            "Hasil OCR": text,
            "Ground Truth": GROUND_TRUTH_NUMBER,
            "CER": cer_results[name],
            "Tanda Tangan": sig_status,
            "Piksel Tinta": ink_pixels,
            "Rasio Tinta": ink_ratio,
        })

    print(f"\n===== VERIFIKASI IJAZAH {index} =====")
    print(f"Nomor Ijazah : {chosen_text or 'TIDAK TERBACA'}")
    print(f"CER metode terpilih : {chosen_cer:.2%}")
    for name, cer in cer_results.items():
        print(f"CER {name}: {cer:.2%}")
    print(f"Tanda Tangan : {sig_status}")
    print(f"Metode OCR yang ditampilkan: {chosen_method}")

    return rows


# =========================================================
# 6. UJI SEMBILAN CITRA KOSONG
# =========================================================
def test_blank_signatures(blank_paths):
    results = []
    for i, path in enumerate(blank_paths, start=1):
        _, gray = read_gray(path)
        status, _, _, ink_pixels, ink_ratio = detect_signature(gray)
        results.append({
            "Citra Kosong": path.name,
            "Hasil Deteksi": status,
            "Piksel Tinta": ink_pixels,
            "Rasio Tinta": ink_ratio,
            "Sesuai Harapan": status == "SIGNATURE ABSENT"
        })

    if results:
        pd.DataFrame(results).to_csv(
            OUTPUT_DIR / "pengujian_9_citra_kosong.csv", index=False
        )

        print("\n===== UJI 9 CITRA KOSONG =====")
        for row in results:
            print(f"{row['Citra Kosong']}: {row['Hasil Deteksi']}")
        print(
            "Jumlah citra kosong yang terdeteksi ABSENT:",
            sum(row["Sesuai Harapan"] for row in results),
            "dari", len(results)
        )
    return results


# =========================================================
# 7. MAIN
# =========================================================
def main():
    number_images = get_images(NOMOR_DIR)
    signature_images = get_images(TANDA_TANGAN_DIR)

    if len(number_images) != 9 or len(signature_images) != 9:
        print("PERINGATAN: idealnya masing-masing folder berisi 9 citra.")
        print(f"Nomor ijazah: {len(number_images)}")
        print(f"Tanda tangan: {len(signature_images)}")

    if len(number_images) != len(signature_images):
        raise ValueError(
            "Jumlah citra kedua folder harus sama. "
            "Pastikan urutan file sesuai pasangan ijazah."
        )

    all_rows = []
    for index, (number_path, signature_path) in enumerate(
        zip(number_images, signature_images), start=1
    ):
        all_rows.extend(
            visualize_one(index, number_path, signature_path)
        )

    pd.DataFrame(all_rows).to_csv(
        OUTPUT_DIR / "perbandingan_enhancement_ocr.csv", index=False
    )

    print("\n===== CER AGREGAT PER METODE =====")
    total_reference_characters = len(GROUND_TRUTH_NUMBER) * len(number_images)
    for method in (
        "Brightness Adjustment",
        "Contrast Stretching",
        "Histogram Equalization",
    ):
        method_rows = [
            row for row in all_rows
            if row["Metode Enhancement"] == method
        ]
        total_errors = sum(
            edit_distance(row["Ground Truth"], row["Hasil OCR"])
            for row in method_rows
        )
        aggregate_cer = total_errors / total_reference_characters
        print(f"{method}: {aggregate_cer:.2%}")

    blank_paths = create_blank_examples(signature_images)
    blank_results = test_blank_signatures(blank_paths)

    print("\nSemua hasil disimpan di:", OUTPUT_DIR)
    print("Citra kosong dibuat di:", KOSONG_DIR)
    print(
        "Catatan: citra kosong hanya contoh negatif sintetis. "
        "Untuk evaluasi ilmiah, uji juga citra asli tanpa tanda tangan."
    )


if __name__ == "__main__":
    main()