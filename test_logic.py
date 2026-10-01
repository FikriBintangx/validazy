import jwt
import time
from expert_system import evaluate_authenticity
from validator import verify_digital_certificate, PUBLIC_SECRET_KEY

def run_tests():
    # 1. Test Rule 1: Tanpa token / domain tidak whitelist
    res1 = evaluate_authenticity(cert_valid=False)
    assert res1["status"] == "PALSU"
    assert res1["rule_triggered"] == "RULE_1"

    # 2. Test Rule 2: Cert valid tapi sharpness rendah (cetak ulang/fotokopi)
    metrics_blurry = {"edge_sharpness": 40.0, "ink_bleeding": 1.1, "contrast": 0.8, "noise_level": 15.0}
    res2 = evaluate_authenticity(cert_valid=True, metrics=metrics_blurry)
    assert res2["status"] == "PALSU"
    assert res2["rule_triggered"] == "RULE_2"

    # 3. Test Rule 3: Cert valid tapi ink bleeding luber
    metrics_bleeding = {"edge_sharpness": 85.0, "ink_bleeding": 2.2, "contrast": 0.9, "noise_level": 15.0}
    res3 = evaluate_authenticity(cert_valid=True, metrics=metrics_bleeding)
    assert res3["status"] == "PALSU"
    assert res3["rule_triggered"] == "RULE_3"

    # 4. Test Rule 4: Cert valid dan metrik fisik standar pabrik
    metrics_clean = {"edge_sharpness": 90.0, "ink_bleeding": 1.1, "contrast": 0.88, "noise_level": 12.0}
    res4 = evaluate_authenticity(cert_valid=True, metrics=metrics_clean)
    assert res4["status"] == "ORIGINAL"
    assert res4["rule_triggered"] == "RULE_4"

    # 5. Test Validator Token Signature
    token = jwt.encode({"sub": "prod_123", "iat": int(time.time())}, PUBLIC_SECRET_KEY, algorithm="HS256")
    valid_url = f"https://verify.brand-auth.com/check?token={token}"
    ok, _ = verify_digital_certificate(valid_url)
    assert ok is True

    invalid_domain_url = f"https://fake-phishing.com/check?token={token}"
    bad, _ = verify_digital_certificate(invalid_domain_url)
    assert bad is False

    print("Semua pengujian logika expert system & validator lolos 100%!")

if __name__ == "__main__":
    run_tests()
