# /Validazy

<div align="center">
  <img src="https://koboyo.com/page-mascot/mascots/fox-directions.webp" width="100" height="100" alt="Validazy Mascot" style="border-radius: 50%;" />
  <h3>Offline Product Authenticity Expert System</h3>
  <p>Multi-layer physical & digital product verification powered by a native Certainty Factor (CF) engine and interactive Page Mascots.</p>
</div>

---

## ⚡ Overview

**/Validazy** is a cross-platform mobile application designed to evaluate the authenticity of physical and digital products (such as luxury items, electronics, cosmetics, and automotive spare parts) completely **offline** without relying on third-party verification servers.

It utilizes an academic **Certainty Factor (CF)** expert inference model to assess multiple layers of authentication evidence, including:
1. **Digital Evidence Layer:** Barcode / QR Code format integrity and background URI connectivity validation.
2. **Physical Security Layer:** Microtext readability, dynamic 3D holographic shifting, and package tamper-evident seals.

---

## ✨ Features

- **🛡️ 100% Offline-First Architecture:** The entire Certainty Factor engine runs locally in Dart (`cf_engine.dart` + `knowledge_base.json`). No external database, backend, or cloud dependency.
- **📷 High-Speed Barcode / QR Scanner:** Built with `mobile_scanner`, featuring real-time detection, shutter capture, and anti-false positive validation.
- **📊 Transparent Explainable AI:** In-depth diagnosis screen breaking down individual expert vs. user CF weights and explaining the verdict with detailed evidence reasoning.
- **🦊 Interactive Page Mascots:** Integrated mascot companion supporting all 53 character sprites from [koboyo.com/page-mascot](https://koboyo.com/page-mascot). User selection is persisted locally via `SharedPreferences`.
- **🎨 Minimalist Shadcn-Inspired UI:** Pure white/light grey aesthetic (`#F7F8FA` / `#FFFFFF`), high contrast typography, shadcn Breadcrumb navigation, and responsive floating bottom bar.

---

## 🛠️ Tech Stack & Requirements

- **Framework:** [Flutter](https://flutter.dev/) (Channel stable, SDK `>=3.3.0 <4.0.0`)
- **Language:** Dart 3 native
- **State Management:** `provider`
- **Scanner:** `mobile_scanner`
- **Storage:** `shared_preferences` (for mascot preferences & settings)
- **Target Platforms:** Android (tested on Android 16 / arm64) & iOS

---

## 🚀 Installation & Setup

### 1. Prerequisites
Make sure you have Flutter and the Android SDK installed:
```bash
flutter --version
adb devices
```

### 2. Clone the Repository
```bash
git clone https://github.com/FikriBintangx/validazy.git
cd validazy
```

### 3. Install Dependencies
Fetch all required packages:
```bash
flutter pub get
```

### 4. Run the Application
Connect your physical device via USB/Wi-Fi debugging or launch an emulator, then execute:
```bash
# Run on default connected device
flutter run

# Or target a specific device ID
flutter run -d <DEVICE_ID>
```

---

## 📦 Building Release APK

To generate an optimized, standalone release APK for Android:
```bash
flutter build apk --release
```
The compiled output will be located at:
```
build/app/outputs/flutter-apk/app-release.apk
```

---

## 📂 Project Structure

```text
lib/
├── core/
│   └── cf_engine.dart          # Native Certainty Factor computation engine
├── screens/
│   ├── home_screen.dart        # Hero layout, Page Mascot picker & verification history
│   ├── scanner_screen.dart     # Camera viewport, barcode analysis & capture controls
│   ├── question_screen.dart    # Shadcn questionnaire & breadcrumb evidence checklist
│   └── result_screen.dart      # Explainable AI results, score breakdown & evidence audit
├── state/
│   └── auth_provider.dart      # Reactive state, background HTTP checks & mascot storage
└── theme/
    └── app_theme.dart          # Clean minimalist palette & component decorations
```

---

## 📄 License & Credits

Developed with ❤️ by **[Fikri Bintang](https://github.com/FikriBintangx)**.  
Licensed under the [MIT License](LICENSE).
