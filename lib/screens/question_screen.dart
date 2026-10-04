import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../state/auth_provider.dart';
import 'result_screen.dart';

class QuestionScreen extends StatelessWidget {
  const QuestionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final prov = context.watch<ValidationProvider>();

    if (prov.isLoading) {
      return const Scaffold(
        backgroundColor: Colors.white,
        body: Center(child: CircularProgressIndicator(color: Color(0xFF18181B))),
      );
    }

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            // Shadcn Breadcrumb Component (Menggantikan AppBar)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: Color(0xFFE4E4E7), width: 1)),
              ),
              child: Row(
                children: [
                  GestureDetector(
                    onTap: () => Navigator.of(context).popUntil((route) => route.isFirst),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.home_outlined, size: 14, color: Color(0xFF71717A)),
                        SizedBox(width: 4),
                        Text('Home', style: TextStyle(fontSize: 13, color: Color(0xFF71717A), fontWeight: FontWeight.w500)),
                      ],
                    ),
                  ),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 8),
                    child: Icon(Icons.chevron_right_rounded, size: 14, color: Color(0xFFA1A1AA)),
                  ),
                  GestureDetector(
                    onTap: () => Navigator.pop(context),
                    child: const Text('Scan', style: TextStyle(fontSize: 13, color: Color(0xFF71717A), fontWeight: FontWeight.w500)),
                  ),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 8),
                    child: Icon(Icons.chevron_right_rounded, size: 14, color: Color(0xFFA1A1AA)),
                  ),
                  const Text(
                    'Pemeriksaan',
                    style: TextStyle(fontSize: 13, color: Color(0xFF18181B), fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),

            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
                children: [
                  // Target Scan Badge (Shadcn Badge)
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFAFAFA),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFE4E4E7)),
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(7),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: const Color(0xFFE4E4E7)),
                          ),
                          child: const Icon(Icons.qr_code_2, size: 18, color: Color(0xFF18181B)),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'TARGET SCAN',
                                style: TextStyle(fontSize: 9.5, fontWeight: FontWeight.w700, color: Color(0xFF71717A), letterSpacing: 0.8),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                prov.scannedBarcode ?? 'VF-00123',
                                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF18181B)),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3.5),
                          decoration: BoxDecoration(
                            color: prov.isLinkValid ? const Color(0xFFDCFCE7) : const Color(0xFFF4F4F5),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            prov.isLinkValid ? 'Active Link' : 'SKU Code',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: prov.isLinkValid ? const Color(0xFF16A34A) : const Color(0xFF71717A),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Questions (Shadcn Questionnaire Cards)
                  for (int i = 0; i < prov.questions.length; i++) ...[
                    Builder(
                      builder: (context) {
                        final q = prov.questions[i];
                        return Container(
                          margin: const EdgeInsets.only(bottom: 22),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    width: 20,
                                    height: 20,
                                    decoration: const BoxDecoration(
                                      color: Color(0xFF18181B),
                                      shape: BoxShape.circle,
                                    ),
                                    child: Center(
                                      child: Text(
                                        '${i + 1}',
                                        style: const TextStyle(color: Colors.white, fontSize: 10.5, fontWeight: FontWeight.w700),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      q.text,
                                      style: const TextStyle(
                                        fontSize: 14,
                                        fontWeight: FontWeight.w600,
                                        color: Color(0xFF18181B),
                                        letterSpacing: -0.2,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              for (final opt in prov.options)
                                GestureDetector(
                                  onTap: () => prov.answerQuestion(i, opt.weight),
                                  child: AnimatedContainer(
                                    duration: const Duration(milliseconds: 120),
                                    margin: const EdgeInsets.only(bottom: 8),
                                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
                                    decoration: BoxDecoration(
                                      color: q.selectedWeight == opt.weight ? const Color(0xFFFAFAFA) : Colors.white,
                                      borderRadius: BorderRadius.circular(8),
                                      border: Border.all(
                                        color: q.selectedWeight == opt.weight ? const Color(0xFF18181B) : const Color(0xFFE4E4E7),
                                        width: q.selectedWeight == opt.weight ? 1.5 : 1.0,
                                      ),
                                    ),
                                    child: Row(
                                      children: [
                                        Container(
                                          width: 16,
                                          height: 16,
                                          decoration: BoxDecoration(
                                            shape: BoxShape.circle,
                                            border: Border.all(
                                              color: q.selectedWeight == opt.weight ? const Color(0xFF18181B) : const Color(0xFFA1A1AA),
                                              width: q.selectedWeight == opt.weight ? 5.0 : 1.5,
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 12),
                                        Expanded(
                                          child: Text(
                                            opt.label,
                                            style: TextStyle(
                                              fontSize: 13,
                                              fontWeight: q.selectedWeight == opt.weight ? FontWeight.w600 : FontWeight.w400,
                                              color: q.selectedWeight == opt.weight ? const Color(0xFF18181B) : const Color(0xFF3F3F46),
                                            ),
                                          ),
                                        ),
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: const Color(0xFFF4F4F5),
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: Text(
                                            '${opt.weight >= 0 ? "+" : ""}${opt.weight.toStringAsFixed(1)}',
                                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Color(0xFF71717A)),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        );
                      },
                    ),
                  ],
                ],
              ),
            ),

            // Shadcn Bottom Action Button
            Container(
              padding: const EdgeInsets.all(18),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: Color(0xFFE4E4E7))),
              ),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF18181B),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    elevation: 0,
                  ),
                  onPressed: () {
                    prov.calculateResult();
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(builder: (_) => const ResultScreen()),
                    );
                  },
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Hitung Keaslian', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, letterSpacing: -0.2)),
                      SizedBox(width: 6),
                      Icon(Icons.arrow_forward_rounded, size: 16),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
