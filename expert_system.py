from typing import Any

# Threshold ambang batas fisik cetakan standar pabrik
MIN_EDGE_SHARPNESS = 65.0   # Tepi di bawah ini terindikasi blur / scan cetak ulang
MAX_INK_BLEEDING = 1.65     # Rasio hitam vs putih di atas ini menandakan tinta meluber
MAX_QUIET_ZONE_NOISE = 38.0 # Noise standar deviasi pada margin putih

def evaluate_authenticity(cert_valid: bool, metrics: dict[str, float] | None = None) -> dict[str, Any]:
    """
    Mesin Inferensi Forward Chaining dengan 4 Rules:
    - Rule 1: Jika sertifikat digital False -> PALSU (Hentikan inferensi).
    - Rule 2: Jika sertifikat valid & ketajaman buruk -> PALSU (Indikasi cetak ulang).
    - Rule 3: Jika sertifikat valid & ink bleeding/noise tinggi -> PALSU (Cetakan non-standar).
    - Rule 4: Jika sertifikat valid & seluruh metrik fisik baik -> ORIGINAL.
    """
    # Rule 1: Sertifikat digital invalid / tidak ada
    if not cert_valid:
        return {
            "status": "PALSU",
            "rule_triggered": "RULE_1",
            "reason": "Sertifikat digital tidak valid, domain tidak terdaftar, atau tanda tangan kriptografi palsu/kadaluarsa."
        }

    # Jika metrik fisik tidak tersedia setelah cert valid (fail-safe)
    if not metrics:
        return {
            "status": "PALSU",
            "rule_triggered": "RULE_E",
            "reason": "Metrik fisik tidak dapat diekstraksi dari citra."
        }

    sharpness = metrics.get("edge_sharpness", 0.0)
    bleeding = metrics.get("ink_bleeding", 0.0)
    noise = metrics.get("noise_level", 0.0)

    # Rule 2: Ketajaman tepi buruk (Indikasi hasil scan/fotokopi/cetak ulang kualitas rendah)
    if sharpness < MIN_EDGE_SHARPNESS:
        return {
            "status": "PALSU",
            "rule_triggered": "RULE_2",
            "reason": f"Ketajaman tepi garis buruk ({sharpness} < {MIN_EDGE_SHARPNESS}). Terdapat indikasi cetak ulang atau duplikasi fotokopi."
        }

    # Rule 3: Ink bleeding tinggi atau noise quiet zone tinggi
    if bleeding > MAX_INK_BLEEDING or noise > MAX_QUIET_ZONE_NOISE:
        alasan = []
        if bleeding > MAX_INK_BLEEDING:
            alasan.append(f"Ink bleeding tinggi ({bleeding} > {MAX_INK_BLEEDING}) menyempitkan celah putih")
        if noise > MAX_QUIET_ZONE_NOISE:
            alasan.append(f"Bintik noise margin putih tinggi ({noise} > {MAX_QUIET_ZONE_NOISE})")

        return {
            "status": "PALSU",
            "rule_triggered": "RULE_3",
            "reason": f"Kualitas cetakan tidak standar pabrik: {', '.join(alasan)}."
        }

    # Rule 4: Sertifikat valid dan seluruh kualitas fisik memenuhi standar
    return {
        "status": "ORIGINAL",
        "rule_triggered": "RULE_4",
        "reason": "Sertifikat digital terotentikasi resmi dan metrik fisik cetakan memenuhi standar presisi pabrik."
    }
