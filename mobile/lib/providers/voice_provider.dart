// lib/providers/voice_provider.dart

import 'dart:async';
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

  // ==========================================================
  // ===== INICIO DE NUEVOS ESTADOS PARA CONTROLAR EL PANEL =====
  // ==========================================================
  bool _isVoiceModeActive = false; // Controla si el panel es visible
  bool _isProcessing = false;      // Muestra el loader de "Procesando"
  String _feedbackMessage = '';    // Mensaje de éxito/error post-procesamiento

  bool get isListening => _isListening;
  String get lastText => _lastText;

  // Getters para los nuevos estados
  bool get isVoiceModeActive => _isVoiceModeActive;
  bool get isProcessing => _isProcessing;
  bool get hasFeedbackMessage => _feedbackMessage.isNotEmpty;
  String get feedbackMessage => _feedbackMessage;
  // ========================================================
  // ===== FIN DE NUEVOS ESTADOS PARA CONTROLAR EL PANEL =====
  // ========================================================


  /// Inicia el modo voz, muestra el panel y comienza a escuchar.
  /// Reemplaza al antiguo `startListening`.
  Future<void> activateAndStartListening(
      CartProvider cart,
      List<Product> products,
      ) async {
    // 1. Resetea estados y activa el panel
    _isVoiceModeActive = true;
    _isListening = true;
    _isProcessing = false;
    _lastText = '';
    _feedbackMessage = '';
    notifyListeners();

    // 2. Inicializa el servicio de voz
    final available = await _speech.initialize();
    if (!available) {
      _feedbackMessage = 'El servicio de voz no está disponible en este dispositivo.';
      _isListening = false;
      notifyListeners();
      // Oculta el panel después de un momento
      deactivateVoiceMode(delay: const Duration(seconds: 3));
      return;
    }

    // 3. Comienza a escuchar
    _speech.listen(
      localeId: 'es-ES',
      onResult: (result) {
        // Actualiza el texto reconocido en tiempo real
        _lastText = result.recognizedWords.toLowerCase();
        notifyListeners();

        // Cuando el usuario termina de hablar...
        if (result.finalResult && _lastText.isNotEmpty) {
          _isListening = false;
          _isProcessing = true; // Muestra el loader
          notifyListeners();

          // Llama al backend para procesar el comando
          _processCommand(_lastText, cart, products);
        }
      },
    );
  }

  /// Apaga y oculta el panel de voz.
  /// Reemplaza al antiguo `stop`.
  void deactivateVoiceMode({Duration delay = Duration.zero}) {
    // El retraso es para que el usuario pueda leer el mensaje de feedback
    Timer(delay, () {
      if (_speech.isListening) {
        _speech.stop();
      }
      _isListening = false;
      _isProcessing = false;
      _isVoiceModeActive = false;
      _lastText = '';
      _feedbackMessage = '';
      notifyListeners();
    });
  }

  /// Llama al backend, actualiza el carrito y prepara el mensaje de feedback.
  Future<void> _processCommand(
      String text,
      CartProvider cart,
      List<Product> products,
      ) async {
    text = text.toLowerCase().trim();
    if (text.isEmpty) {
      // Si el resultado final está vacío, simplemente cierra el panel
      deactivateVoiceMode();
      return;
    }

    try {
      final res = await voiceService.interpret(text);

      switch (res.action) {
        case 'clear':
          cart.clear();
          _feedbackMessage = 'Se ha vaciado el carrito.';
          break;

        case 'add':
        case 'remove':
          if (res.productId == null) {
            _feedbackMessage = 'No entendí qué producto mencionaste. Intenta de nuevo.';
            break;
          }

          // Busca el producto por ID. Es más fiable que por nombre.
          final product = products.firstWhere((p) => p.id == res.productId);
          final qty = res.quantity <= 0 ? 1 : res.quantity;

          if (res.action == 'add') {
            cart.add(product, quantity: qty);
            _feedbackMessage = '✅ ${product.name} añadido.';
          } else {
            for (var i = 0; i < qty; i++) {
              cart.removeOne(product);
            }
            _feedbackMessage = '✅ ${product.name} quitado.';
          }
          break;

        case 'checkout':
          if (cart.items.isEmpty) {
            _feedbackMessage = 'No puedes finalizar una compra con el carrito vacío.';
          } else {
            // No navegamos desde aquí, solo ejecutamos la lógica de negocio
            await salesService.createPendingSaleFromCart(cart);
            cart.clear();
            _feedbackMessage = '✅ Compra finalizada. El carrito está listo para un nuevo pedido.';
          }
          break;

        default:
          _feedbackMessage = 'No pude entender el comando. ¿Puedes repetirlo?';
          break;
      }
    } catch (e) {
      _feedbackMessage = 'Hubo un error al procesar tu voz. Por favor, intenta de nuevo.';
    } finally {
      // 4. Finaliza el procesamiento y muestra el feedback
      _isProcessing = false;
      notifyListeners();
      // Ocultamos el panel después de 2.5 segundos para dar tiempo a leer
      deactivateVoiceMode(delay: const Duration(milliseconds: 2500));
    }
  }
}
