class CertaintyFactorEngine {
  /// cfData is a list of (cfExpert * cfUser)
  static double calculateCF(List<double> cfData) {
    if (cfData.isEmpty) return 0.0;
    
    double cfCombine = cfData[0];
    for (int i = 1; i < cfData.length; i++) {
      cfCombine = cfCombine + (cfData[i] * (1 - cfCombine));
    }
    
    return double.parse((cfCombine * 100).toStringAsFixed(1)); // 0 - 100%
  }
}
