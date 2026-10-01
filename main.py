import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse

from schemas import VerificationResponse, PhysicalMetrics
from validator import decode_barcode_data, verify_digital_certificate
import base64
from vision import extract_physical_metrics, draw_visual_bbox
from expert_system import evaluate_authenticity

app = FastAPI(title="Barcode Authenticity Expert System", version="1.0.0")


def encode_image_base64(img_bgr: np.ndarray) -> str:
    _, buffer = cv2.imencode(".jpg", img_bgr)
    return "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")

@app.post("/api/verify", response_model=VerificationResponse)

async def verify_barcode(file: UploadFile = File(...)):
    # Validasi tipe file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Format file harus berupa gambar")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image_bgr is None:
        raise HTTPException(status_code=400, detail="Gagal memproses file gambar")

    # 1. Dekode barcode & verifikasi sertifikat kriptografis
    barcode_payload = decode_barcode_data(image_bgr)
    cert_valid, _ = verify_digital_certificate(barcode_payload)

    # Rule 1 Shortcut: Jika sertifikat digital tidak valid, hentikan tanpa analisis fisik mendalam
    if not cert_valid:
        decision = evaluate_authenticity(cert_valid=False)
        annotated_bgr = draw_visual_bbox(image_bgr, is_original=False)
        return VerificationResponse(
            status=decision["status"],
            rule_triggered=decision["rule_triggered"],
            reason=decision["reason"],
            certificate_valid=False,
            physical_metrics=None,
            annotated_image_base64=encode_image_base64(annotated_bgr),
        )

    # 2. Jika sertifikat valid, ekstrak fitur fisik dan lanjutkan inferensi
    metrics_dict = extract_physical_metrics(image_bgr)
    decision = evaluate_authenticity(cert_valid=True, metrics=metrics_dict)

    is_original = (decision["status"] == "ORIGINAL")
    annotated_bgr = draw_visual_bbox(image_bgr, is_original=is_original)
    return VerificationResponse(
        status=decision["status"],
        rule_triggered=decision["rule_triggered"],
        reason=decision["reason"],
        certificate_valid=True,
        physical_metrics=PhysicalMetrics(**metrics_dict),
        annotated_image_base64=encode_image_base64(annotated_bgr),
    )

# UI Bersih, Minimalis, dan Monokromatik (Tidak ramai / tidak norak warna-warni)
@app.get("/", response_class=HTMLResponse)
def index_ui():
    return """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VALIDAZYYYY &bull; Expert System</title>
  <style>
    :root, [data-theme="dark"], html[data-theme="dark"], body[data-theme="dark"] {
      --bg: #0A0A0C;
      --card-bg: rgba(18, 18, 24, 0.75);
      --card-border: rgba(255, 255, 255, 0.12);
      --card-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
      --text-main: #FAFAFA;
      --text-muted: #94A3B8;
      --stroke-solid: rgba(255, 255, 255, 0.85);
      --stroke-faded: rgba(255, 255, 255, 0.34);
      --item-bg: rgba(255, 255, 255, 0.03);
      --item-border: rgba(255, 255, 255, 0.06);
      --btn-bg: #FFFFFF;
      --btn-text: #0A0A0C;
      --btn-hover: #E2E8F0;
      --select-bg: #18181B;
      --select-text: #F4F4F5;
      --select-border: rgba(255, 255, 255, 0.15);
      --accent-hover: #34D399;
      --footer-text: rgba(255, 255, 255, 0.35);
      --nav-bg: rgba(10, 10, 12, 0.8);
      --theme-btn-bg: rgba(255, 255, 255, 0.08);
      --theme-btn-border: rgba(255, 255, 255, 0.15);
    }

    [data-theme="light"], html[data-theme="light"], body[data-theme="light"] {
      --bg: #F4F5F8;
      --card-bg: rgba(255, 255, 255, 0.75);
      --card-border: rgba(0, 0, 0, 0.08);
      --card-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.08);
      --text-main: #0F172A;
      --text-muted: #64748B;
      --stroke-solid: rgba(15, 23, 42, 0.75);
      --stroke-faded: rgba(15, 23, 42, 0.22);
      --item-bg: rgba(15, 23, 42, 0.03);
      --item-border: rgba(15, 23, 42, 0.06);
      --btn-bg: #0F172A;
      --btn-text: #FFFFFF;
      --btn-hover: #1E293B;
      --select-bg: #FFFFFF;
      --select-text: #0F172A;
      --select-border: #CBD5E1;
      --accent-hover: #059669;
      --footer-text: rgba(15, 23, 42, 0.4);
      --nav-bg: rgba(244, 245, 248, 0.85);
      --theme-btn-bg: rgba(0, 0, 0, 0.05);
      --theme-btn-border: rgba(0, 0, 0, 0.1);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    body {
      background-color: var(--bg);
      color: var(--text-main);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      min-height: 100vh;
      overflow-x: hidden;
      position: relative;
      padding-top: 80px;
      transition: background-color 0.3s ease, color 0.3s ease;
    }


    /* Motion Animations replicated in pure CSS */
    .icon-wrapper {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
    
    /* CloudMoon Icon Animations */
    .cloud-moon-icon svg {
      transition: transform 0.3s ease;
    }
    .cloud-moon-icon .moon-path {
      transform-origin: 16px 9px;
      transition: transform 0.8s ease-in-out;
    }
    .cloud-moon-icon .cloud-path {
      transition: transform 0.7s ease-in-out;
    }
    .theme-toggle:hover .cloud-moon-icon .moon-path {
      animation: moonWobble 0.8s ease-in-out;
    }
    .theme-toggle:hover .cloud-moon-icon .cloud-path {
      animation: cloudShift 0.7s ease-in-out;
    }
    @keyframes moonWobble {
      0% { transform: rotate(0deg); }
      25% { transform: rotate(-12deg); }
      50% { transform: rotate(10deg); }
      75% { transform: rotate(-4deg); }
      100% { transform: rotate(0deg); }
    }
    @keyframes cloudShift {
      0% { transform: translateX(0); }
      35% { transform: translateX(1px); }
      70% { transform: translateX(-0.5px); }
      100% { transform: translateX(0); }
    }

    /* BadgeCheck Icon Animations */
    .badge-check-icon svg {
      overflow: visible;
    }
    .badge-check-icon .badge-path {
      transform-origin: 12px 12px;
      transition: transform 0.6s ease-in-out;
    }
    .badge-check-icon .tick-path {
      stroke-dasharray: 9;
      stroke-dashoffset: 0;
      transition: stroke-dashoffset 0.45s ease-out, opacity 0.3s ease;
    }
    .nav-brand:hover .badge-check-icon .badge-path {
      animation: badgeScale 0.6s ease-in-out;
    }
    .nav-brand:hover .badge-check-icon .tick-path {
      animation: tickDraw 0.6s ease-out;
    }
    @keyframes badgeScale {
      0% { transform: scale(1); }
      35% { transform: scale(1.08); }
      70% { transform: scale(0.97); }
      100% { transform: scale(1); }
    }
    @keyframes tickDraw {
      0% { stroke-dashoffset: 9; opacity: 0; }
      20% { stroke-dashoffset: 9; opacity: 0; }
      100% { stroke-dashoffset: 0; opacity: 1; }
    }

    /* Top Navbar */
    .top-nav {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 60px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 32px;
      z-index: 9999; pointer-events: auto;
      background: var(--nav-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--card-border);
    }
    .nav-brand {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .brand-badge {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.1em;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(52, 211, 153, 0.15);
      border: 1px solid rgba(52, 211, 153, 0.3);
      color: var(--accent-hover);
    }
    .brand-title {
      font-size: 14px;
      font-weight: 800;
      letter-spacing: 0.15em;
      color: var(--text-main);
    }
    .theme-toggle {
      background: var(--theme-btn-bg);
      border: 1px solid var(--theme-btn-border);
      color: var(--text-main);
      padding: 7px 16px;
      border-radius: 20px;
      font-size: 12.5px;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
      position: relative;
      z-index: 10001;
      pointer-events: auto;
      user-select: none;
    }
    .theme-toggle * {
      pointer-events: none;
    }
    .theme-toggle:hover {
      background: rgba(255, 255, 255, 0.15);
      transform: translateY(-1px);
    }

    /* Infinite Background Marquee (3 Lines) */
    .marquee-container {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 100vw;
      overflow: hidden;
      white-space: nowrap;
      pointer-events: auto;
      z-index: 0;
      user-select: none;
      display: flex;
      flex-direction: column;
      line-height: 0.9;
      perspective: 1000px;
    }
    .marquee-track {
      display: inline-flex;
    }
    .line-top { animation: loopScrollLeft 24s linear infinite; margin-left: -5%; }
    .line-middle { animation: loopScrollRight 20s linear infinite; margin-left: -15%; }
    .line-bottom { animation: loopScrollLeft 24s linear infinite; margin-left: -10%; }
    
    .marquee-text {
      font-size: clamp(5rem, 14vw, 11rem);
      font-weight: 900;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: transparent;
      padding-right: 48px;
      display: inline-block;
      cursor: crosshair;
      transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1), -webkit-text-stroke 0.3s ease, filter 0.3s ease;
      transform-style: preserve-3d;
    }
    .marquee-text.solid {
      -webkit-text-stroke: 2px var(--stroke-solid);
    }
    .marquee-text.faded {
      -webkit-text-stroke: 1.5px var(--stroke-faded);
    }
    .marquee-text:hover {
      transform: rotateX(180deg) scale(1.05);
      -webkit-text-stroke: 2.5px var(--accent-hover) !important;
      filter: drop-shadow(0 0 25px rgba(52, 211, 153, 0.6));
    }

    @keyframes loopScrollLeft {
      0% { transform: translateX(0); }
      100% { transform: translateX(-50%); }
    }
    @keyframes loopScrollRight {
      0% { transform: translateX(-50%); }
      100% { transform: translateX(0); }
    }

    /* Main 2-Column Wrapper */
    .main-wrapper {
      position: relative;
      z-index: 2;
      width: 100%;
      max-width: 960px;
      display: flex;
      flex-direction: row;
      align-items: stretch;
      justify-content: center;
      gap: 24px;
      margin: auto 0;
      padding: 30px 16px;
    }

    @media (max-width: 820px) {
      .main-wrapper {
        flex-direction: column;
        align-items: center;
      }
    }

    /* Frosted Cards */
    .card, .sidebar-panel {
      flex: 1 1 0;
      width: 100%;
      max-width: 440px;
      min-height: 480px;
      background: var(--card-bg);
      backdrop-filter: blur(28px) saturate(160%);
      -webkit-backdrop-filter: blur(28px) saturate(160%);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 30px 26px;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .sidebar-header h2, .header h1 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-main);
      letter-spacing: -0.02em;
      margin-bottom: 4px;
    }
    .sidebar-header p, .header p {
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.4;
    }
    .workflow-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 6px;
      flex: 1;
    }
    .step-item {
      display: flex;
      gap: 12px;
      background: var(--item-bg);
      border: 1px solid var(--item-border);
      padding: 12px 14px;
      border-radius: 10px;
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.5;
    }
    .step-num {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-main);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 700;
      flex-shrink: 0;
    }
    .step-text strong {
      color: var(--text-main);
      font-weight: 600;
    }

    .dropzone {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      border: 1.5px dashed var(--card-border);
      border-radius: 10px;
      padding: 20px 16px;
      text-align: center;
      background: var(--item-bg);
      cursor: pointer;
      transition: all 0.25s ease;
      min-height: 120px;
      overflow: hidden;
    }
    .dropzone.dragover {
      border-color: #34D399;
      background: rgba(52, 211, 153, 0.08);
      transform: scale(1.02);
    }
    .scanner-line {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 2px;
      background: #34D399;
      box-shadow: 0 0 10px #34D399, 0 0 20px #34D399;
      display: none;
      z-index: 10;
      animation: scanAnim 1.5s linear infinite;
    }
    @keyframes scanAnim {
      0% { top: 0; opacity: 0; }
      10% { opacity: 1; }
      90% { opacity: 1; }
      100% { top: 100%; opacity: 0; }
    }
    .dropzone span {
      font-size: 13px;
      color: var(--text-muted);
      word-break: break-all;
    }
    #previewThumb {
      display: none;
      max-height: 90px;
      max-width: 100%;
      border-radius: 6px;
      margin-bottom: 8px;
      border: 1px solid var(--card-border);
    }
    input[type="file"] { display: none; }

    .btn {
      width: 100%;
      height: 42px;
      background: var(--btn-bg);
      color: var(--btn-text);
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    .btn:hover:not(:disabled) {
      background: var(--btn-hover);
    }

    .toggle-form-btn {
      font-size: 11.5px;
      color: var(--text-muted);
      text-decoration: underline;
      cursor: pointer;
      text-align: center;
      background: none;
      border: none;
      margin-top: -6px;
    }
    .question-form {
      display: none;
      flex-direction: column;
      gap: 12px;
      background: var(--item-bg);
      border: 1px solid var(--item-border);
      border-radius: 8px;
      padding: 14px;
    }
    .q-item {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }
    .q-item label {
      font-size: 12px;
      color: var(--text-muted);
    }
    .q-select {
      background-color: var(--select-bg);
      color: var(--select-text);
      border: 1px solid var(--select-border);
      padding: 9px 12px;
      border-radius: 8px;
      outline: none;
      font-size: 13px;
      font-family: inherit;
      cursor: pointer;
    }
    .q-select:focus {
      border-color: #34D399;
    }
    .q-select option {
      background-color: var(--select-bg);
      color: var(--select-text);
    }

    .result {
      border-top: 1px solid var(--card-border);
      padding-top: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .badge {
      align-self: flex-start;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.8px;
    }
    .badge-ORIGINAL {
      background: rgba(16, 185, 129, 0.15);
      color: #34D399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-PALSU {
      background: rgba(239, 68, 68, 0.15);
      color: #F87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .reason-text {
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.5;
    }
    #annotatedImg {
      display: none;
      width: 100%;
      max-height: 160px;
      object-fit: contain;
      background: #000;
      border-radius: 8px;
      border: 1px solid var(--card-border);
    }
    .details {
      display: flex;
      flex-direction: column;
      gap: 8px;
      background: var(--item-bg);
      border: 1px solid var(--item-border);
      border-radius: 8px;
      padding: 12px;
    }
    .info-row {
      display: flex;
      justify-content: space-between;
      font-size: 12.5px;
      color: var(--text-muted);
    }
    .info-row span:last-child {
      color: var(--text-main);
      font-weight: 600;
    }
    .actions-row {
      display: flex;
      gap: 8px;
      margin-top: 4px;
    }
    .btn-secondary {
      flex: 1;
      height: 34px;
      background: var(--item-bg);
      color: var(--text-main);
      border: 1px solid var(--card-border);
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.12);
    }

    .app-footer {
      position: relative;
      z-index: 2;
      margin-top: auto;
      padding: 24px 0 16px 0;
      text-align: center;
      font-size: 12px;
      color: var(--footer-text);
      letter-spacing: 0.05em;
    }
  </style>
</head>
<body>
  <!-- Fixed Top Navbar -->
  <header class="top-nav">
    <div class="nav-brand" title="Verified Expert System">
      <div class="icon-wrapper badge-check-icon" style="color: var(--accent-hover);">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path class="badge-path" d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z" />
          <path class="tick-path" d="m9 12 2 2 4-4" />
        </svg>
      </div>
    </div>
    
    <button id="themeToggle" class="theme-toggle" aria-label="Toggle Theme">
      <div class="icon-wrapper cloud-moon-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path class="cloud-path" d="M13 16a3 3 0 0 1 0 6H7a5 5 0 1 1 4.9-6z" />
          <path class="moon-path" d="M18.376 14.512a6 6 0 0 0 3.461-4.127c.148-.625-.659-.97-1.248-.714a4 4 0 0 1-5.259-5.26c.255-.589-.09-1.395-.716-1.248a6 6 0 0 0-4.594 5.36" />
        </svg>
      </div>
      <span id="themeLabel">Light Mode</span>
    </button>
  </header>

  <!-- Infinite Aesthetic Marquee Background (3 Lines) -->
  <div class="marquee-container" aria-hidden="true">
    <div class="marquee-track line-top">
      <span class="marquee-text faded">VALIDAZYYYY • VALIDAZYYYY • </span>
      <span class="marquee-text faded">VALIDAZYYYY • VALIDAZYYYY • </span>
    </div>
    <div class="marquee-track line-middle">
      <span class="marquee-text solid">VALIDAZYYYY • VALIDAZYYYY • </span>
      <span class="marquee-text solid">VALIDAZYYYY • VALIDAZYYYY • </span>
    </div>
    <div class="marquee-track line-bottom">
      <span class="marquee-text faded">VALIDAZYYYY • VALIDAZYYYY • </span>
      <span class="marquee-text faded">VALIDAZYYYY • VALIDAZYYYY • </span>
    </div>
  </div>

  <div class="main-wrapper">
    <!-- Panel Kiri: Alur Sistem Pakar -->
    <div class="sidebar-panel">
      <div class="sidebar-header">
        <h2>Alur Kerja Sistem Pakar</h2>
        <p>Proses inferensi forward chaining & analisis citra.</p>
      </div>
      <div class="workflow-list">
        <div class="step-item">
          <div class="step-num">1</div>
          <div class="step-text"><strong>Scan Barcode:</strong> Dekode data URL dari citra barcode.</div>
        </div>
        <div class="step-item">
          <div class="step-num">2</div>
          <div class="step-text"><strong>Validasi Kriptografi:</strong> Cek whitelist domain & verifikasi digital signature stateless. <em>(Gagal = PALSU Rule 1)</em>.</div>
        </div>
        <div class="step-item">
          <div class="step-num">3</div>
          <div class="step-text"><strong>Computer Vision:</strong> Hitung ketajaman garis Canny/Sobel, ink bleeding, dan noise margin.</div>
        </div>
        <div class="step-item">
          <div class="step-num">4</div>
          <div class="step-text"><strong>Forward Chaining:</strong> Evaluasi metrik fisik untuk menentukan status <em>ORIGINAL</em> atau <em>PALSU (Rule 2–4)</em>.</div>
        </div>
      </div>
    </div>

    <!-- Panel Kanan: Verifikasi Card -->
    <div class="card">
      <div class="header">
        <h1>Verifikasi Barcode</h1>
        <p>Sistem pakar pendeteksi keaslian fisik & sertifikat digital.</p>
      </div>
      
      <label class="dropzone" id="dropzone" for="fileInput">
        <div class="scanner-line" id="scannerLine"></div>
        <img id="previewThumb" alt="Preview Thumbnail" />
        <span id="labelTxt">Tarik & lepas gambar, atau klik pilih</span>
        <input type="file" id="fileInput" accept="image/*" />
      </label>

      <button id="submitBtn" class="btn" disabled>Periksa Keaslian</button>

      <button id="toggleFormBtn" class="toggle-form-btn">Verifikasi Manual (Kuisioner)</button>

      <div class="question-form" id="questionForm">
        <div class="q-item">
          <label>1. Apakah URL domain sesuai resmi?</label>
          <select class="q-select" id="qDomain">
            <option value="yes">Ya, sesuai whitelist</option>
            <option value="no">Tidak, domain mencurigakan</option>
          </select>
        </div>
        <div class="q-item">
          <label>2. Bagaimana kualitas cetakan garis barcode?</label>
          <select class="q-select" id="qSharpness">
            <option value="good">Tajam dan jelas</option>
            <option value="bad">Buram/bergerigi (seperti fotokopi)</option>
          </select>
        </div>
        <button id="submitFormBtn" class="btn" style="height: 36px; margin-top: 4px;">Proses Jawaban</button>
      </div>

      <div class="result" id="resultBox" style="display: none;">
        <div><span id="resBadge" class="badge"></span></div>
        <p id="resReason" class="reason-text"></p>
        
        <img id="annotatedImg" alt="Visual Bounding Box" />

        <div class="details">
          <div class="info-row"><span>Aturan Terpicu</span><span id="resRule">-</span></div>
          <div class="info-row"><span>Sertifikat Digital</span><span id="resCert">-</span></div>
          <div id="metricsBox" style="display: flex; flex-direction: column; gap: 8px;"></div>
        </div>

        <div class="actions-row">
          <button id="copyBtn" class="btn-secondary">Salin Ringkasan</button>
          <button id="downloadBtn" class="btn-secondary">Download JSON</button>
        </div>
      </div>
    </div>
  </div>

  <footer class="app-footer">
    <span>VALIDAZYYYY &bull; Sistem Pakar Verifikasi Barcode Digital &copy; 2026</span>
  </footer>

  <script>
    const fileInput = document.getElementById('fileInput');
    const labelTxt = document.getElementById('labelTxt');
    const previewThumb = document.getElementById('previewThumb');
    const submitBtn = document.getElementById('submitBtn');
    const resultBox = document.getElementById('resultBox');
    const annotatedImg = document.getElementById('annotatedImg');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const dropzone = document.getElementById('dropzone');
    const scannerLine = document.getElementById('scannerLine');
    const toggleFormBtn = document.getElementById('toggleFormBtn');
    const questionForm = document.getElementById('questionForm');
    const submitFormBtn = document.getElementById('submitFormBtn');

    let currentResultData = null;

    // Drag and Drop Logic
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, preventDefaults, false);
    });
    function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const file = dt.files[0];
      if (file && file.type.startsWith('image/')) {
        fileInput.files = dt.files;
        handleFileSelect(file);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files[0]) handleFileSelect(fileInput.files[0]);
    });

    function handleFileSelect(file) {
      labelTxt.textContent = file.name;
      submitBtn.disabled = false;
      const reader = new FileReader();
      reader.onload = (e) => {
        previewThumb.src = e.target.result;
        previewThumb.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }

    // Toggle Kuisioner
    let formOpen = false;
    toggleFormBtn.addEventListener('click', () => {
      formOpen = !formOpen;
      questionForm.style.display = formOpen ? 'flex' : 'none';
      toggleFormBtn.textContent = formOpen ? 'Tutup Verifikasi Manual' : 'Verifikasi Manual (Kuisioner)';
    });

    // Proses Manual Kuisioner
    submitFormBtn.addEventListener('click', () => {
      resultBox.style.display = 'none';
      annotatedImg.style.display = 'none';
      document.getElementById('metricsBox').innerHTML = '';
      
      const domain = document.getElementById('qDomain').value;
      const sharpness = document.getElementById('qSharpness').value;
      
      let status = "ORIGINAL";
      let rule = "RULE_MANUAL_4";
      let reason = "Evaluasi manual: Domain resmi dan cetakan tajam.";
      let badgeCls = "badge-ORIGINAL";
      
      if (domain === 'no') {
        status = "PALSU";
        rule = "RULE_MANUAL_1";
        reason = "Evaluasi manual: Domain tidak resmi/mencurigakan.";
        badgeCls = "badge-PALSU";
      } else if (sharpness === 'bad') {
        status = "PALSU";
        rule = "RULE_MANUAL_2";
        reason = "Evaluasi manual: Indikasi cetak ulang (garis buram).";
        badgeCls = "badge-PALSU";
      }

      const badge = document.getElementById('resBadge');
      badge.textContent = status;
      badge.className = 'badge ' + badgeCls;
      document.getElementById('resReason').textContent = reason;
      document.getElementById('resRule').textContent = rule;
      document.getElementById('resCert').textContent = "Evaluasi Manual";
      
      resultBox.style.display = 'flex';
    });

    // Submit API dengan Efek Scanning
    submitBtn.addEventListener('click', async () => {
      const file = fileInput.files[0];
      if (!file) return;

      submitBtn.disabled = true;
      submitBtn.textContent = 'Memindai...';
      scannerLine.style.display = 'block';
      resultBox.style.display = 'none';

      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch('/api/verify', { method: 'POST', body: formData });
        const data = await res.json();
        currentResultData = data;

        const badge = document.getElementById('resBadge');
        badge.textContent = data.status;
        badge.className = 'badge badge-' + data.status;

        document.getElementById('resReason').textContent = data.reason;
        document.getElementById('resRule').textContent = data.rule_triggered;
        document.getElementById('resCert').textContent = data.certificate_valid ? 'Valid (Resmi)' : 'Tidak Valid';

        if (data.annotated_image_base64) {
          annotatedImg.src = data.annotated_image_base64;
          annotatedImg.style.display = 'block';
        } else {
          annotatedImg.style.display = 'none';
        }

        const metricsBox = document.getElementById('metricsBox');
        if (data.physical_metrics) {
          metricsBox.innerHTML = `
            <div class="info-row"><span>Ketajaman Tepi</span><span>${data.physical_metrics.edge_sharpness}</span></div>
            <div class="info-row"><span>Ink Bleeding</span><span>${data.physical_metrics.ink_bleeding}</span></div>
            <div class="info-row"><span>Kontras</span><span>${data.physical_metrics.contrast}</span></div>
            <div class="info-row"><span>Noise Quiet Zone</span><span>${data.physical_metrics.noise_level}</span></div>
          `;
        } else {
          metricsBox.innerHTML = '';
        }

        resultBox.style.display = 'flex';
      } catch (err) {
        alert('Terjadi kesalahan saat memverifikasi gambar.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Periksa Keaslian';
        scannerLine.style.display = 'none';
      }
    });

    // Actions
    copyBtn.addEventListener('click', () => {
      if (!currentResultData) return;
      const text = `HASIL VERIFIKASI BARCODE:
Status: ${currentResultData.status}
Rule: ${currentResultData.rule_triggered}
Sertifikat: ${currentResultData.certificate_valid ? 'Valid' : 'Tidak Valid'}
Alasan: ${currentResultData.reason}`;
      navigator.clipboard.writeText(text).then(() => {
        const prev = copyBtn.textContent;
        copyBtn.textContent = 'Tersalin!';
        setTimeout(() => copyBtn.textContent = prev, 1500);
      });
    });

    downloadBtn.addEventListener('click', () => {
      if (!currentResultData) return;
      const blob = new Blob([JSON.stringify(currentResultData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `laporan-verifikasi-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });

    // Theme Switcher
    const themeToggle = document.getElementById('themeToggle');
    const themeLabel = document.getElementById('themeLabel');
    const rootEl = document.documentElement;

    function applyTheme(isLight) {
      if (isLight) {
        rootEl.setAttribute('data-theme', 'light');
        document.body.setAttribute('data-theme', 'light');
        if (themeLabel) themeLabel.textContent = 'Dark Mode';
        localStorage.setItem('val_theme', 'light');
      } else {
        rootEl.setAttribute('data-theme', 'dark');
        document.body.setAttribute('data-theme', 'dark');
        if (themeLabel) themeLabel.textContent = 'Light Mode';
        localStorage.setItem('val_theme', 'dark');
      }
    }

    // Init theme
    const savedTheme = localStorage.getItem('val_theme') || 'dark';
    applyTheme(savedTheme === 'light');

    if (themeToggle) {
      themeToggle.addEventListener('click', function(e) {
        e.preventDefault();
        const currentTheme = rootEl.getAttribute('data-theme');
        applyTheme(currentTheme !== 'light');
      });
    }
  </script>
</body>
</html>"""
