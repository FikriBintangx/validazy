import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../state/auth_provider.dart';
import '../theme/app_theme.dart';
import 'home_screen.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final prov = context.read<ValidationProvider>();
    final score = prov.finalScore;
    final breakdown = prov.breakdown;

    String verdict = 'FAKE / PALSU';
    Color badgeColor = AppTheme.fake;
    Color lightBg = AppTheme.fakeLight;
    IconData icon = Icons.cancel_outlined;
    String summary = 'Produk tidak memenuhi indikator keaslian utama. Sangat berisiko barang tiruan.';

    if (score >= 80) {
      verdict = 'VERIFIED / ASLI';
      badgeColor = AppTheme.verified;
      lightBg = AppTheme.verifiedLight;
      icon = Icons.check_circle_outline;
      summary = 'Produk terindikasi ASLI berdasarkan pengujian multi-layer sistem pakar (Certainty Factor).';
    } else if (score >= 50) {
      verdict = 'SUSPICIOUS / MERAGUKAN';
      badgeColor = AppTheme.suspicious;
      lightBg = AppTheme.suspiciousLight;
      icon = Icons.warning_amber_rounded;
      summary = 'Terdapat anomali pada salah satu parameter keaslian. Perlu pemeriksaan fisik lebih lanjut.';
    }

    return Scaffold(
      backgroundColor: AppTheme.bg,
      appBar: AppBar(
        backgroundColor: AppTheme.bg,
        elevation: 0,
        scrolledUnderElevation: 0,
        automaticallyImplyLeading: false,
        title: const Text('Hasil Verifikasi', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppTheme.primary)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(24, 12, 24, 40),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Hero Score Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 20),
              decoration: AppTheme.card(radius: 24),
              child: Column(
                children: [
                  Icon(icon, size: 64, color: badgeColor),
                  const SizedBox(height: 12),
                  Text(
                    '${score.toStringAsFixed(1)}%',
                    style: const TextStyle(fontSize: 44, fontWeight: FontWeight.w900, color: AppTheme.primary, letterSpacing: -1.5),
                  ),
                  const Text(
                    'CONFIDENCE SCORE',
                    style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppTheme.textSec, letterSpacing: 1),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                    decoration: BoxDecoration(color: badgeColor, borderRadius: BorderRadius.circular(20)),
                    child: Text(
                      verdict,
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 12, letterSpacing: 0.5),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(color: lightBg, borderRadius: BorderRadius.circular(12)),
                    child: Text(
                      summary,
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600, color: badgeColor, height: 1.4),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // 2. Detail Evidence Breakdown
            const Text(
              'Detail Evidence Analysis',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.primary),
            ),
            const SizedBox(height: 12),

            ...breakdown.map((item) {
              final isPos = item.isPositive;
              final Color itemColor = isPos ? AppTheme.verified : AppTheme.fake;
              final Color itemBg = isPos ? AppTheme.verifiedLight : AppTheme.fakeLight;

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(16),
                decoration: AppTheme.card(radius: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            item.title,
                            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppTheme.primary),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(color: itemBg, borderRadius: BorderRadius.circular(8)),
                          child: Text(
                            '${item.cfEvidence >= 0 ? "+" : ""}${item.cfEvidence.toStringAsFixed(2)} CF',
                            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: itemColor),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      item.reason,
                      style: const TextStyle(fontSize: 12, color: AppTheme.textSec, height: 1.35),
                    ),
                    const Divider(height: 20, color: AppTheme.border),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Bobot Pakar: ${item.cfExpert.toStringAsFixed(2)}', style: const TextStyle(fontSize: 11, color: AppTheme.textSec)),
                        Text('Keyakinan User: ${item.cfUser.toStringAsFixed(2)}', style: const TextStyle(fontSize: 11, color: AppTheme.textSec)),
                      ],
                    )
                  ],
                ),
              );
            }),

            const SizedBox(height: 20),

            // 3. Save / Back Action
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 0,
                ),
                onPressed: () {
                  prov.saveCurrentToHistory();
                  prov.reset();
                  Navigator.pushAndRemoveUntil(context, MaterialPageRoute(builder: (_) => const HomeScreen()), (route) => false);
                },
                child: const Text('Simpan ke Riwayat & Selesai', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
