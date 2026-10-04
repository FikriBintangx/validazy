import 'package:flutter/material.dart';

class AppTheme {
  static const Color bg = Color(0xFFF7F8FA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color primary = Color(0xFF111111);
  static const Color textSec = Color(0xFF6B7280);
  static const Color border = Color(0xFFE5E7EB);
  
  static const Color verified = Color(0xFF16A34A);
  static const Color verifiedLight = Color(0xFFDCFCE7);
  static const Color suspicious = Color(0xFFF59E0B);
  static const Color suspiciousLight = Color(0xFFFEF3C7);
  static const Color fake = Color(0xFFDC2626);
  static const Color fakeLight = Color(0xFFFEE2E2);
  static const Color scanRed = Color(0xFFE31B23);

  static BoxDecoration card({double radius = 16}) {
    return BoxDecoration(
      color: surface,
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(color: border, width: 1),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.03),
          blurRadius: 10,
          offset: const Offset(0, 4),
        )
      ],
    );
  }
}
