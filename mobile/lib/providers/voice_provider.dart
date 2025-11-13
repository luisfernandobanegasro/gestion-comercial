// lib/providers/voice_provider.dart

import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

import '../models/product.dart';
import 'cart_provider.dart';
import '../services/voice_service.dart';
import '../services/sales_service.dart';

class VoiceProvider extends ChangeNotifier {
  final stt.SpeechToText _speech = stt.SpeechToText();

  bool _isListening = false;
  String _lastText = '';

  bool get isListening => _isListening;
  String get lastText => _lastText;

  Future<void> startListening(
    CartProvider cart,
    List<Product> products,
    VoidCallback onCartChanged,
  ) async {
    final available = await _speech.initialize(
      onStatus: (status) {},
      onError: (error) {},
    );

    if (!available) return;

    _isListening = true;
    _lastText = '';
    notifyListeners();

    _speech.listen(
      localeId: 'es-ES',
      onResult: (result) async {
        _lastText = result.recognizedWords.toLowerCase();

        if (result.finalResult) {
          _isListening = false;
          notifyListeners();

          await _processCommand(_lastText, cart, products);
          onCartChanged();
        }
      },
    );
  }

  void stop() {
    _speech.stop();
    _isListening = false;
    notifyListeners();
  }

  // ============================================================
  // Interpretación delegada al backend (Django)
  // ============================================================
  Future<void> _processCommand(
    String text,
    CartProvider cart,
    List<Product> products,
  ) async {
    text = text.toLowerCase().trim();
    if (text.isEmpty) return;

    try {
      final res = await voiceService.interpret(text);

      switch (res.action) {
        case 'clear':
          cart.clear();
          break;

        case 'add':
        case 'remove':
          if (res.productId == null) return;

          final product = products.firstWhere(
            (p) => p.id == res.productId,
            orElse:
                () => products.firstWhere(
                  (p) =>
                      p.name.toLowerCase() ==
                      (res.productName ?? '').toLowerCase(),
                  orElse: () => products.first,
                ),
          );

          final qty = res.quantity <= 0 ? 1 : res.quantity;

          if (res.action == 'add') {
            cart.add(product, quantity: qty);
          } else {
            for (var i = 0; i < qty; i++) {
              cart.removeOne(product);
            }
          }
          break;

        case 'checkout':
          // Finalizar compra por voz: crea la venta pendiente y limpia carrito
          if (cart.items.isEmpty) {
            return;
          }
          await salesService.createPendingSaleFromCart(cart);
          cart.clear();
          break;

        default:
          // unknown → no hacemos nada por ahora
          break;
      }
    } catch (e) {
      // Si falla el endpoint, no tocamos el carrito.
    }
  }
}
