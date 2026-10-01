import cv2
import numpy as np

def get_barcode_bounding_box(image: np.ndarray) -> tuple[int, int, int, int]:
    """Mendeteksi kontur utama barcode dan mengembalikan koordinat bounding box (x, y, w, h)."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h_img, w_img = image.shape[:2]
    if not contours:
        return 0, 0, w_img, h_img

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    pad = 8
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(w_img, x + w + pad)
    y2 = min(h_img, y + h + pad)
    return x1, y1, x2 - x1, y2 - y1

def crop_barcode_area(image: np.ndarray) -> np.ndarray:
    """Mendeteksi kontur utama barcode dan memotong otomatis areanya."""
    x, y, w, h = get_barcode_bounding_box(image)
    cropped = image[y:y+h, x:x+w]
    return cropped if cropped.size > 0 else image

def draw_visual_bbox(image: np.ndarray, is_original: bool) -> np.ndarray:
    """Menggambar highlight bounding box hijau (Original) atau merah (Palsu) di area deteksi barcode."""
    annotated = image.copy()
    x, y, w, h = get_barcode_bounding_box(image)
    # Hijau BGR = (16, 185, 129), Merah BGR = (68, 68, 239)
    color = (129, 185, 16) if is_original else (68, 68, 239)
    cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 3)
    label = "VALID" if is_original else "DETEKSI"
    cv2.putText(annotated, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
    return annotated

def extract_physical_metrics(image: np.ndarray) -> dict[str, float]:
    """
    Mengekstrak metrik fisik kualitas cetakan:
    1. edge_sharpness: Variansi gradien menggunakan Canny & Sobel.
    2. ink_bleeding: Bar-to-space ratio (rasio piksel hitam vs celah putih).
    3. contrast: Perbedaan intensitas luminansi (Michelson contrast).
    4. noise_level: Bintik noise pada margin putih (quiet zone).
    """
    cropped = crop_barcode_area(image)
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    # 1. Ketajaman tepi (Edge Sharpness via Canny + Sobel variance)
    edges = cv2.Canny(gray, 100, 200)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    # Rata-rata kekuatan gradien pada titik tepi (edge pixels)
    edge_sharpness = float(np.mean(gradient_magnitude[edges > 0])) if np.any(edges > 0) else float(np.var(gray))

    # 2. Ink Bleeding: Bar-to-space ratio (Otsu thresholding)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    black_pixels = np.count_nonzero(binary == 0)
    white_pixels = np.count_nonzero(binary == 255)
    # Jika tinta meluber (bleeding), porsi black_pixels melonjak drastis vs white_pixels
    ink_bleeding = float(black_pixels / max(white_pixels, 1))

    # 3. Kontras (Michelson Contrast)
    p_high = np.percentile(gray, 95)
    p_low = np.percentile(gray, 5)
    contrast = float((p_high - p_low) / max(p_high + p_low, 1e-5))

    # 4. Noise level pada margin putih (Quiet Zone / border area)
    # Mengambil strip perimeter 5% terluar dari citra
    h, w = gray.shape
    border_mask = np.zeros((h, w), dtype=bool)
    bw, bh = max(2, int(w * 0.05)), max(2, int(h * 0.05))
    border_mask[:bh, :] = True
    border_mask[-bh:, :] = True
    border_mask[:, :bw] = True
    border_mask[:, -bw:] = True

    border_pixels = gray[border_mask]
    # Noise diukur dari standar deviasi area quiet zone (semestinya mulus seragam)
    noise_level = float(np.std(border_pixels))

    return {
        "edge_sharpness": round(edge_sharpness, 2),
        "ink_bleeding": round(ink_bleeding, 2),
        "contrast": round(contrast, 3),
        "noise_level": round(noise_level, 2),
    }
