import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../state/auth_provider.dart';
import '../theme/app_theme.dart';
import 'scanner_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  Future<void> _openGitHub() async {
    final Uri url = Uri.parse('https://github.com/FikriBintangx/validazy');
    try {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    } catch (e) {
      debugPrint('Could not launch $url: $e');
    }
  }

  Widget _buildMascotImage(String mascotName, {double size = 44}) {
    return SizedBox(
      width: size,
      height: size,
      child: ClipRect(
        child: Transform.scale(
          scale: 3.0, // Memperbesar 3x karena sprite sheet berukuran 3x3 grid
          alignment: Alignment.center, // Ambil frame tengah (baris 2, kolom 2) yang madep depan
          child: Image.network(
            'https://koboyo.com/page-mascot/mascots/$mascotName-directions.webp',
            fit: BoxFit.contain,
            errorBuilder: (c, e, s) => Icon(Icons.pets, size: size * 0.5, color: const Color(0xFF9CA3AF)),
          ),
        ),
      ),
    );
  }

  void _showMascotPicker(BuildContext context, ValidationProvider prov) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Container(
          height: MediaQuery.of(context).size.height * 0.75,
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Pilih Page Mascot',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF111827)),
                      ),
                      SizedBox(height: 2),
                      Text(
                        'Pilih salah satu dari 53 maskot (tersimpan otomatis)',
                        style: TextStyle(fontSize: 12, color: Color(0xFF6B7280)),
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 20, color: Color(0xFF6B7280)),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const Divider(height: 24, color: Color(0xFFE5E7EB)),
              Expanded(
                child: GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 4,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    childAspectRatio: 0.85,
                  ),
                  itemCount: prov.mascotList.length,
                  itemBuilder: (context, idx) {
                    final mascotName = prov.mascotList[idx];
                    final isSelected = prov.mascot == mascotName;

                    return GestureDetector(
                      onTap: () {
                        prov.setMascot(mascotName);
                        Navigator.pop(ctx);
                      },
                      child: Container(
                        decoration: BoxDecoration(
                          color: isSelected ? const Color(0xFFF3F4F6) : Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isSelected ? const Color(0xFF111827) : const Color(0xFFE5E7EB),
                            width: isSelected ? 2 : 1,
                          ),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: _buildMascotImage(mascotName, size: 40),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              mascotName,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                                color: isSelected ? const Color(0xFF111827) : const Color(0xFF4B5563),
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      extendBody: true,
      body: _currentIndex == 0 ? _buildHomeBody() : _buildHistoryBody(),
      bottomNavigationBar: SafeArea(
        child: Container(
          margin: const EdgeInsets.only(left: 20, right: 20, bottom: 16),
          height: 64,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(32),
            border: Border.all(color: AppTheme.border, width: 1.2),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavTab(
                index: 0,
                icon: Icons.home_filled,
                label: 'Home',
                isActive: _currentIndex == 0,
              ),
              GestureDetector(
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const ScannerScreen()),
                ),
                child: Container(
                  width: 48,
                  height: 48,
                  decoration: const BoxDecoration(
                    color: AppTheme.scanRed,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.document_scanner_rounded, color: Colors.white, size: 24),
                ),
              ),
              _buildNavTab(
                index: 1,
                icon: Icons.history_rounded,
                label: 'History',
                isActive: _currentIndex == 1,
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Home Screen Layout with Exact Spacing from Reference
  Widget _buildHomeBody() {
    final prov = context.watch<ValidationProvider>();

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 28, 24, 100),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Page Mascot Interactive Display (Floating directly above title, no background)
            GestureDetector(
              onTap: () => _showMascotPicker(context, prov),
              child: _buildMascotImage(prov.mascot, size: 72),
            ),
            const SizedBox(height: 8),

            // 1. Title: /Validazy
            const Text(
              '/Validazy',
              style: TextStyle(
                fontSize: 38,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.03 * 38,
                color: Color(0xFF111827),
              ),
            ),
            const SizedBox(height: 16), // 16px to description

            // 2. Description (Bersih tanpa teks skill generator)
            const Text(
              'Expert System for Product Authenticity. Evaluasi keaslian produk fisik & digital menggunakan metode Certainty Factor murni offline.',
              style: TextStyle(
                fontSize: 16,
                height: 1.45,
                color: Color(0xFF4B5563),
                fontWeight: FontWeight.w400,
              ),
            ),
            const SizedBox(height: 28), // 28px to button row

            // 3. Button Row (Start Scan & GitHub Link saja, tombol Mascot dihapus)
            Wrap(
              spacing: 12,
              runSpacing: 10,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                // Primary: Start Scan
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF121316),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    elevation: 0,
                  ),
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const ScannerScreen()),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('Start Scan', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                      SizedBox(width: 6),
                      Icon(Icons.arrow_forward_rounded, size: 16),
                    ],
                  ),
                ),

                // Pure Raw GitHub Link / Button (No Card BG)
                InkWell(
                  onTap: _openGitHub,
                  borderRadius: BorderRadius.circular(8),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Image.network(
                          'https://cdn-icons-png.flaticon.com/512/25/25231.png',
                          width: 18,
                          height: 18,
                          color: const Color(0xFF1F2937),
                          errorBuilder: (c, e, s) => const Icon(Icons.code, size: 18, color: Color(0xFF1F2937)),
                        ),
                        const SizedBox(width: 6),
                        const Text(
                          'GitHub',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF1F2937),
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16), // 16px to helper text

            // 4. Helper Text
            const Text(
              'Pilih salah satu dari 53 maskot di atas, atau scan produk untuk mulai verifikasi.',
              style: TextStyle(fontSize: 13, color: Color(0xFF9CA3AF), fontWeight: FontWeight.w400),
            ),
            const SizedBox(height: 32),

            // 5. System Status Banner (Minimalist)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFF9FAFB),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFE5E7EB)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.check_circle_outline, color: Color(0xFF16A34A), size: 20),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('System Ready • Offline AI', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF111827))),
                        SizedBox(height: 2),
                        Text('Certainty Factor Engine aktif tanpa server eksternal.', style: TextStyle(fontSize: 11.5, color: Color(0xFF6B7280))),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // History Tab Screen
  Widget _buildHistoryBody() {
    final history = context.watch<ValidationProvider>().history;

    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 28, 24, 100),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Riwayat Verifikasi',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: Color(0xFF111827)),
            ),
            const SizedBox(height: 16),
            if (history.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.only(top: 40),
                  child: Text('Belum ada riwayat scan.', style: TextStyle(color: Color(0xFF6B7280))),
                ),
              )
            else
              ...history.map((h) {
                Color c = AppTheme.fake;
                Color bg = AppTheme.fakeLight;
                if (h.verdict == 'Verified') {
                  c = AppTheme.verified;
                  bg = AppTheme.verifiedLight;
                } else if (h.verdict == 'Suspicious') {
                  c = AppTheme.suspicious;
                  bg = AppTheme.suspiciousLight;
                }
                return _buildHistoryItem(h.title, h.barcode, h.date, '${h.score.toStringAsFixed(1)}%', h.verdict, c, bg);
              }),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryItem(String name, String id, String date, String score, String status, Color statusColor, Color statusBg) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE5E7EB)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.02),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFFF3F4F6),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.inventory_2_outlined, color: Color(0xFF111827), size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF111827))),
                const SizedBox(height: 2),
                Text('$id • $date', style: const TextStyle(fontSize: 11, color: Color(0xFF6B7280))),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: statusBg,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              '$score $status',
              style: TextStyle(color: statusColor, fontWeight: FontWeight.w700, fontSize: 11),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavTab({
    required int index,
    required IconData icon,
    required String label,
    required bool isActive,
  }) {
    return GestureDetector(
      onTap: () => setState(() => _currentIndex = index),
      behavior: HitTestBehavior.opaque,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: isActive ? AppTheme.scanRed : AppTheme.textSec, size: 22),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
                color: isActive ? AppTheme.scanRed : AppTheme.textSec,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
