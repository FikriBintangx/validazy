import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/cf_engine.dart';

class HistoryRecord {
  final String title;
  final String barcode;
  final String date;
  final double score;
  final String verdict;

  HistoryRecord({
    required this.title,
    required this.barcode,
    required this.date,
    required this.score,
    required this.verdict,
  });
}

class EvidenceDetail {
  final String title;
  final double cfExpert;
  final double cfUser;
  final double cfEvidence;
  final String reason;
  final bool isPositive;

  EvidenceDetail({
    required this.title,
    required this.cfExpert,
    required this.cfUser,
    required this.cfEvidence,
    required this.reason,
    required this.isPositive,
  });
}

class QuestionItem {
  final String id;
  final String text;
  final double cfExpert;
  double selectedWeight = 0.0;

  QuestionItem({required this.id, required this.text, required this.cfExpert});
}

class OptionItem {
  final String label;
  final double weight;

  OptionItem({required this.label, required this.weight});
}

class ValidationProvider extends ChangeNotifier {
  List<QuestionItem> _questions = [];
  List<OptionItem> _options = [];
  final List<HistoryRecord> _history = [];
  List<EvidenceDetail> _breakdown = [];
  String? _scannedBarcode;
  String? _barcodeFormat;
  bool _isLinkValid = false;
  double _finalScore = 0.0;
  bool _isLoading = true;

  String _mascot = 'fox'; // Default Mascot
  final List<String> mascotList = [
    'bear', 'bunny', 'cat', 'deer', 'dino', 'fox', 'frog', 'hamster', 'hedgehog', 'koala', 
    'mouse', 'otter', 'owl', 'panda', 'penguin', 'pug', 'raccoon', 'redpanda', 'sheep', 
    'sloth', 'tiger', 'afro', 'astronaut', 'bald', 'ballerina', 'beard', 'builder', 'cap', 
    'chef', 'glasses', 'grandpa', 'granny', 'hijabi', 'kamran', 'nurse', 'pirate', 'scientist', 
    'sikh', 'skater', 'wizard', 'clockwork', 'crt', 'cube', 'drone', 'gearbot', 'knight', 
    'lantern', 'postbot', 'radio', 'rocket', 'scout', 'toaster', 'tv'
  ];

  List<QuestionItem> get questions => _questions;
  List<OptionItem> get options => _options;
  List<HistoryRecord> get history => _history;
  List<EvidenceDetail> get breakdown => _breakdown;
  String? get scannedBarcode => _scannedBarcode;
  String? get barcodeFormat => _barcodeFormat;
  bool get isLinkValid => _isLinkValid;
  double get finalScore => _finalScore;
  bool get isLoading => _isLoading;
  String get mascot => _mascot;

  ValidationProvider() {
    _initMascot();
  }

  Future<void> _initMascot() async {
    final prefs = await SharedPreferences.getInstance();
    _mascot = prefs.getString('mascot') ?? 'fox';
    notifyListeners();
  }

  Future<void> setMascot(String newMascot) async {
    _mascot = newMascot;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('mascot', newMascot);
    notifyListeners();
  }

  Future<void> loadKnowledgeBase() async {
    try {
      final jsonString = await rootBundle.loadString('assets/data/knowledge_base.json');
      final data = json.decode(jsonString);

      _questions = (data['symptoms'] as List).map((s) {
        return QuestionItem(
          id: s['id'],
          text: s['text'],
          cfExpert: (s['cf_expert'] as num).toDouble(),
        );
      }).toList();

      _options = (data['options'] as List).map((o) {
        return OptionItem(
          label: o['label'],
          weight: (o['weight'] as num).toDouble(),
        );
      }).toList();

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading JSON: $e');
    }
  }

  Future<bool> processBarcode(String rawValue, String formatName) async {
    final cleanValue = rawValue.trim();
    if (cleanValue.isEmpty) return false;

    _scannedBarcode = cleanValue;
    _barcodeFormat = formatName;
    _isLinkValid = false;

    for (var q in _questions) {
      q.selectedWeight = 0.0;
    }

    if (cleanValue.startsWith('http://') || cleanValue.startsWith('https://')) {
      try {
        final client = HttpClient();
        client.connectionTimeout = const Duration(seconds: 3);
        final uri = Uri.parse(cleanValue);
        final request = await client.getUrl(uri);
        final response = await request.close();
        
        if (response.statusCode >= 200 && response.statusCode < 400) {
          _isLinkValid = true;
          for (var q in _questions) {
            if (q.id == 'S01') {
              q.selectedWeight = 1.0;
            }
          }
        }
      } catch (e) {
        debugPrint('Direct Link Ping Failed / Offline: $e');
        _isLinkValid = false;
      }
    } else {
      _isLinkValid = true;
      for (var q in _questions) {
        if (q.id == 'S01') {
          q.selectedWeight = 1.0;
        }
      }
    }

    notifyListeners();
    return true;
  }

  void answerQuestion(int index, double weight) {
    _questions[index].selectedWeight = weight;
    notifyListeners();
  }

  void calculateResult() {
    List<double> cfValues = [];
    _breakdown = [];

    for (var q in _questions) {
      final cfVal = q.cfExpert * q.selectedWeight;
      if (q.selectedWeight > 0) {
        cfValues.add(cfVal);
      }

      String reason = 'Ciri tidak teridentifikasi';
      bool isPos = q.selectedWeight > 0;

      if (q.id == 'S01') {
        reason = isPos 
          ? 'Barcode/QR terdaftar dan link direct verifikasi aktif.'
          : 'Barcode tidak terdaftar di database resmi atau link tidak merespon.';
      } else if (q.id == 'S02') {
        reason = isPos 
          ? 'Hologram 3D memiliki efek optik dinamis dan microtext presisi sesuai standar pabrikan.'
          : 'Hologram 3D buram, stiker flat tanpa efek multi-sudut, atau tidak ada.';
      }

      _breakdown.add(EvidenceDetail(
        title: q.id == 'S01' ? 'Validasi Digital (Barcode/QR)' : 'Keamanan Fisik (Hologram 3D)',
        cfExpert: q.cfExpert,
        cfUser: q.selectedWeight,
        cfEvidence: cfVal,
        reason: reason,
        isPositive: isPos,
      ));
    }

    _finalScore = CertaintyFactorEngine.calculateCF(cfValues);
    notifyListeners();
  }

  void saveCurrentToHistory() {
    String verdict = 'Fake';
    if (_finalScore >= 80) {
      verdict = 'Verified';
    } else if (_finalScore >= 50) {
      verdict = 'Suspicious';
    }

    final now = DateTime.now();
    final dateStr = '${now.day}/${now.month}/${now.year}, ${now.hour}:${now.minute.toString().padLeft(2, '0')}';

    _history.insert(
      0,
      HistoryRecord(
        title: 'Produk Dipindai',
        barcode: _scannedBarcode ?? 'VF-00123',
        date: dateStr,
        score: _finalScore,
        verdict: verdict,
      ),
    );
    notifyListeners();
  }

  void reset() {
    _scannedBarcode = null;
    _barcodeFormat = null;
    _isLinkValid = false;
    _finalScore = 0.0;
    _breakdown = [];
    for (var q in _questions) {
      q.selectedWeight = 0.0;
    }
    notifyListeners();
  }
}
