import cv2
import numpy as np
from urllib.parse import urlparse, parse_qs
import jwt

# Whitelist domain resmi
WHITELISTED_DOMAINS = {"verify.brand-auth.com", "auth.official-factory.org", "api.authentic.local"}

# Public key untuk verifikasi stateless token (HMAC-SHA256 untuk simplicity/demo, bisa RS256 dengan RSA key)
PUBLIC_SECRET_KEY = "official-stateless-public-secret-key-2026"

def decode_barcode_data(image_bgr: np.ndarray) -> str | None:
    """Deteksi dan decode barcode/QR menggunakan OpenCV Barcode & QRCode Detector built-in."""
    # Coba deteksi QR Code
    qr_detector = cv2.QRCodeDetector()
    decoded_info, _, _ = qr_detector.detectAndDecode(image_bgr)
    if decoded_info:
        return decoded_info.strip()

    # Coba deteksi 1D Barcode jika OpenCV support
    try:
        barcode_detector = cv2.barcode.BarcodeDetector()
        ok, decoded_info, _, _ = barcode_detector.detectAndDecode(image_bgr)
        if ok and decoded_info:
            res = decoded_info[0] if isinstance(decoded_info, (list, tuple)) else decoded_info
            if res:
                return str(res).strip()
    except Exception:
        pass

    return None

def verify_digital_certificate(barcode_raw: str | None) -> tuple[bool, str]:
    """
    Validasi domain terhadap whitelist dan verifikasi digital signature stateless.
    Format URL yang didukung: https://<domain>/check?token=<jwt_signature>
    """
    if not barcode_raw:
        return False, "Barcode tidak dapat terbaca atau kosong"

    try:
        parsed = urlparse(barcode_raw)
        if not parsed.scheme or not parsed.netloc:
            return False, "Format payload barcode bukan URL valid"

        # 1. Cek Whitelist domain
        domain = parsed.netloc.lower().split(":")[0]
        if domain not in WHITELISTED_DOMAINS:
            return False, f"Domain '{domain}' bukan server resmi yang diotorisasi"

        # 2. Ambil token kriptografi dari query params
        params = parse_qs(parsed.query)
        token = params.get("token", [None])[0] or params.get("sig", [None])[0]
        if not token:
            return False, "Sertifikat digital atau token kriptografi tidak ditemukan pada URL"

        # 3. Verifikasi signature token secara stateless
        # ponytail: decoding HMAC token stateless; upgrade ke RS256/Ed25519 dengan asimetrik public key bila perlu rotasi cert
        jwt.decode(token, PUBLIC_SECRET_KEY, algorithms=["HS256"])
        return True, "Sertifikat digital dan signature kriptografi terverifikasi valid"

    except jwt.ExpiredSignatureError:
        return False, "Sertifikat digital sudah kadaluarsa (expired signature)"
    except jwt.InvalidTokenError as err:
        return False, f"Tanda tangan digital tidak valid: {str(err)}"
    except Exception as err:
        return False, f"Gagal memvalidasi sertifikat: {str(err)}"
