// lib/services/voice_service.dart

import 'package:mobile/services/api_client.dart';

class VoiceIntentResult {
  final String action; // add | remove | clear | unknown
  final int quantity;
  final String? productId;
  final String? productName;

  VoiceIntentResult({
    required this.action,
    required this.quantity,
    this.productId,
    this.productName,
  });
}

class VoiceService {
  Future<VoiceIntentResult> interpret(String text) async {
    final data = await apiClient.post(
      '/analitica/voz/intencion/',
      body: {'text': text},
    );

    final action = (data['action'] ?? 'unknown') as String;
    final quantity = (data['quantity'] ?? 1) as int;

    String? productId;
    String? productName;

    if (data['product'] != null) {
      final p = data['product'] as Map<String, dynamic>;
      productId = p['id']?.toString();
      productName = p['nombre']?.toString();
    } else {
      productName = data['product_name']?.toString();
    }

    return VoiceIntentResult(
      action: action,
      quantity: quantity,
      productId: productId,
      productName: productName,
    );
  }
}

final voiceService = VoiceService();
