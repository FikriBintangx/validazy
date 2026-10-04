import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:provider/provider.dart';
import '../state/auth_provider.dart';
import '../theme/app_theme.dart';
import 'question_screen.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final MobileScannerController _cameraCtrl = MobileScannerController(
    detectionSpeed: DetectionSpeed.normal,
    facing: CameraFacing.back,
    torchEnabled: false,
  );
  bool _isProcessing = false;
  String? _lastScannedValue;
  String? _lastFormatName;

  Future<void> _processScan(String rawValue, String formatName) async {
    if (_isProcessing) return;
    setState(() => _isProcessing = true);

    final prov = context.read<ValidationProvider>();
    final bool success = await prov.processBarcode(rawValue, formatName);

    if (!mounted) return;

    if (success) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const QuestionScreen()),
      );
    } else {
      setState(() => _isProcessing = false);
      _showErrorDialog('Barcode Kosong / Rusak!\n\nPastikan kamera tepat mengarah ke QR Code atau Barcode yang jelas.');
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: AppTheme.border, width: 1),
        ),
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: AppTheme.fake, size: 28),
            SizedBox(width: 8),
            Text(
              'Gagal Validasi',
              style: TextStyle(fontWeight: FontWeight.w800, color: AppTheme.primary, fontSize: 18),
            ),
          ],
        ),
        content: Text(
          message,
          style: const TextStyle(fontWeight: FontWeight.w500, color: AppTheme.primary, fontSize: 14),
        ),
        actions: [
          TextButton(
            style: TextButton.styleFrom(
              backgroundColor: AppTheme.primary,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            onPressed: () {
              Navigator.pop(ctx);
              setState(() => _isProcessing = false);
            },
            child: const Text('Coba Lagi', style: TextStyle(fontWeight: FontWeight.w700, color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _onDetect(BarcodeCapture capture) {
    if (capture.barcodes.isEmpty || _isProcessing) return;
    
    final barcode = capture.barcodes.first;
    if (barcode.rawValue != null && barcode.rawValue!.trim().isNotEmpty) {
      _lastScannedValue = barcode.rawValue;
      _lastFormatName = barcode.format.name;
      
      // Auto proses saat terdeteksi
      _processScan(barcode.rawValue!, barcode.format.name);
    }
  }

  void _manualCapture() {
    if (_lastScannedValue != null && _lastScannedValue!.trim().isNotEmpty) {
      _processScan(_lastScannedValue!, _lastFormatName ?? 'QR_CODE');
    } else {
      _showErrorDialog('Barcode Belum Terdeteksi!\n\nPosisikan QR Code tepat di dalam kotak merah lalu tahan selama 1 detik.');
    }
  }

  @override
  void dispose() {
    _cameraCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bg,
      appBar: AppBar(
        backgroundColor: AppTheme.bg,
        elevation: 0,
        scrolledUnderElevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppTheme.primary),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Scan QR / Barcode', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.primary)),
            Text('Arahkan kamera ke kode produk', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w400, color: AppTheme.textSec)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.bolt, color: AppTheme.primary),
            onPressed: () => _cameraCtrl.toggleTorch(),
          ),
        ],
      ),
      body: Column(
        children: [
          const SizedBox(height: 16),
          // Viewport Kamera
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(24),
                  color: Colors.black,
                  border: Border.all(color: AppTheme.border),
                ),
                clipBehavior: Clip.antiAlias,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    MobileScanner(
                      controller: _cameraCtrl,
                      onDetect: _onDetect,
                    ),
                    // Frame Pembidik
                    Container(
                      width: 240,
                      height: 240,
                      decoration: BoxDecoration(
                        border: Border.all(color: AppTheme.scanRed, width: 2.5),
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                    // Helper Bubble
                    Positioned(
                      bottom: 20,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.black.withValues(alpha: 0.6),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Text(
                          'Letakkan kode di dalam area pemindaian',
                          style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w500),
                        ),
                      ),
                    ),
                    if (_isProcessing)
                      Container(
                        color: Colors.black54,
                        child: const Center(
                          child: CircularProgressIndicator(color: AppTheme.scanRed),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),

          // Control Bar: Gallery on left - Shutter Cekerek in center
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 28),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildSecondaryAction(
                  icon: Icons.image_outlined,
                  label: 'Galeri',
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Pilih dari galeri dibuka...')),
                    );
                  },
                ),

                // Tombol CEKEREK (Camera Shutter Button)
                GestureDetector(
                  onTap: _isProcessing ? null : _manualCapture,
                  child: Container(
                    width: 76,
                    height: 76,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: AppTheme.scanRed, width: 4),
                      color: Colors.white,
                    ),
                    padding: const EdgeInsets.all(5),
                    child: Container(
                      decoration: const BoxDecoration(
                        color: AppTheme.scanRed,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.camera_alt_rounded, color: Colors.white, size: 30),
                    ),
                  ),
                ),

                const SizedBox(width: 50), // Balance spacing
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSecondaryAction({required IconData icon, required String label, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppTheme.surface,
              shape: BoxShape.circle,
              border: Border.all(color: AppTheme.border),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.03),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                )
              ],
            ),
            child: Icon(icon, size: 22, color: AppTheme.primary),
          ),
          const SizedBox(height: 6),
          Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textSec)),
        ],
      ),
    );
  }
}
