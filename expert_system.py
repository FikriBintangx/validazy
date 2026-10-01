# Threshold ambang batas fisik cetakan standar pabrik
MIN_EDGE_SHARPNESS = 65.0   # Tepi di bawah ini terindikasi blur / cetak ulang
MAX_INK_BLEEDING = 1.65     # Rasio hitam vs putih di atas ini menandakan tinta meluber
MAX_QUIET_ZONE_NOISE = 38.0 # Noise standar deviasi pada margin putih

# Bobot Keyakinan Pakar (Measure of Belief / MB) untuk tiap indikator
WEIGHT_CERTIFICATE = 0.95   # Validitas kriptografi memegang bobot kepastian tertinggi
WEIGHT_SHARPNESS = 0.85     # Ketajaman tepi garis
WEIGHT_BLEEDING = 0.75      # Tinta meluber / bar-to-space ratio
WEIGHT_NOISE = 0.70         # Bintik kotor pada quiet zone

def calculate_cf_combination(cf_list: list[float]) -> float:
    """
    Rumus Standar Kombinasi Certainty Factor:
    CF_combine(CF1, CF2) = CF1 + CF2 * (1 - CF1)
    """
    if not cf_list:
        return 0.0
    cf_current = cf_list[0]
    for cf_next in cf_list[1:]:
        cf_current = cf_current + (cf_next * (1.0 - cf_current))
    return round(cf_current, 4)

def evaluate_authenticity(cert_valid: bool, metrics: dict[str, float] | None = None) -> dict[str, Any]:
    """
    Mesin Inferensi Hybrid: Forward Chaining + Certainty Factor (CF).
    Menghitung derajat keyakinan matematis terhadap keaslian atau kepalsuan barcode.
    """
    # Rule 1: Sertifikat digital invalid / tidak terdaftar
    if not cert_valid:
        cf_val = WEIGHT_CERTIFICATE
        return {
            "status": "PALSU",
            "rule_triggered": "RULE_1 (CF)",
            "reason": "Sertifikat digital tidak valid, domain tidak terdaftar, atau signature kriptografi palsu/kadaluarsa.",
            "certainty_factor": cf_val,
            "confidence_percentage": round(cf_val * 100, 1)
        }

    # Jika metrik fisik tidak tersedia
    if not metrics:
        return {
            "status": "PALSU",
            "rule_triggered": "RULE_E",
            "reason": "Metrik fisik tidak dapat diekstraksi dari citra.",
            "certainty_factor": 0.5,
            "confidence_percentage": 50.0
        }

    sharpness = metrics.get("edge_sharpness", 0.0)
    bleeding = metrics.get("ink_bleeding", 0.0)
    noise = metrics.get("noise_level", 0.0)

    evidence_counterfeit = []
    evidence_original = []

    # 1. Evaluasi Ketajaman Tepi (Sharpness)
    if sharpness < MIN_EDGE_SHARPNESS:
        # Semakin jauh di bawah batas, semakin yakin palsu
        ratio = max(0.2, (MIN_EDGE_SHARPNESS - sharpness) / MIN_EDGE_SHARPNESS)
        evidence_counterfeit.append(round(WEIGHT_SHARPNESS * min(1.0, ratio + 0.3), 3))
    else:
        evidence_original.append(round(WEIGHT_SHARPNESS * min(1.0, sharpness / 100.0), 3))

    # 2. Evaluasi Ink Bleeding
    if bleeding > MAX_INK_BLEEDING:
        ratio = min(1.0, (bleeding - MAX_INK_BLEEDING) / MAX_INK_BLEEDING)
        evidence_counterfeit.append(round(WEIGHT_BLEEDING * (ratio + 0.2), 3))
    else:
        evidence_original.append(round(WEIGHT_BLEEDING * 0.9, 3))

    # 3. Evaluasi Noise Margin
    if noise > MAX_QUIET_ZONE_NOISE:
        ratio = min(1.0, (noise - MAX_QUIET_ZONE_NOISE) / MAX_QUIET_ZONE_NOISE)
        evidence_counterfeit.append(round(WEIGHT_NOISE * (ratio + 0.2), 3))
    else:
        evidence_original.append(round(WEIGHT_NOISE * 0.85, 3))

    # Forward Chaining Decision Logic
    # Rule 2: Ketajaman buruk terindikasi cetak ulang
    if sharpness < MIN_EDGE_SHARPNESS:
        final_cf = calculate_cf_combination(evidence_counterfeit)
        return {
            "status": "PALSU",
            "rule_triggered": "RULE_2 (CF)",
            "reason": f"Ketajaman tepi garis buruk ({sharpness} < {MIN_EDGE_SHARPNESS}). Terdapat anomali duplikasi cetak ulang.",
            "certainty_factor": final_cf,
            "confidence_percentage": round(final_cf * 100, 1)
        }

    # Rule 3: Anomali pelebaran tinta atau noise margin
    if bleeding > MAX_INK_BLEEDING or noise > MAX_QUIET_ZONE_NOISE:
        final_cf = calculate_cf_combination(evidence_counterfeit)
        alasan = []
        if bleeding > MAX_INK_BLEEDING:
            alasan.append(f"Ink bleeding ({bleeding} > {MAX_INK_BLEEDING})")
        if noise > MAX_QUIET_ZONE_NOISE:
            alasan.append(f"Noise margin ({noise} > {MAX_QUIET_ZONE_NOISE})")

        return {
            "status": "PALSU",
            "rule_triggered": "RULE_3 (CF)",
            "reason": f"Cetakan tidak standar pabrik: {', '.join(alasan)}.",
            "certainty_factor": final_cf,
            "confidence_percentage": round(final_cf * 100, 1)
        }

    # Rule 4: Sertifikat valid & seluruh metrik fisik memenuhi toleransi pabrik
    evidence_original.append(WEIGHT_CERTIFICATE)
    final_cf = calculate_cf_combination(evidence_original)
    return {
        "status": "ORIGINAL",
        "rule_triggered": "RULE_4 (CF)",
        "reason": "Sertifikat digital terotentikasi resmi dan kualitas cetakan fisik terverifikasi presisi standar pabrik.",
        "certainty_factor": final_cf,
        "confidence_percentage": round(final_cf * 100, 1)
    }
