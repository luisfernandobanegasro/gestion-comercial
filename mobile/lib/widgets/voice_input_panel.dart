// lib/widgets/voice_input_panel.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/voice_provider.dart';

// Este widget se mostrará como un panel inferior
class VoiceInputPanel extends StatelessWidget {
  const VoiceInputPanel({super.key});

  @override
  Widget build(BuildContext context) {
    // Usamos 'watch' para que el widget se reconstruya con los cambios del provider
    final voice = context.watch<VoiceProvider>();

    // El panel solo se muestra si el modo de voz está activo
    if (!voice.isVoiceModeActive) {
      return const SizedBox.shrink(); // No muestra nada si no está activo
    }

    return Container(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, -5),
          )
        ],
      ),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildContent(context, voice),
            const SizedBox(height: 16),
            // Botón para cancelar y cerrar el panel
            if (!voice.isProcessing)
              TextButton(
                onPressed: () =>
                    context.read<VoiceProvider>().deactivateVoiceMode(),
                child: const Text('Cancelar'),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context, VoiceProvider voice) {
    // Muestra el estado del carrito después de procesar
    if (voice.hasFeedbackMessage) {
      return Text(
        voice.feedbackMessage,
        textAlign: TextAlign.center,
        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
      );
    }

    // Muestra el loader mientras se conecta con el backend
    if (voice.isProcessing) {
      return const Column(
        children: [
          Text(
            'Procesando comando...',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 12),
          CircularProgressIndicator(),
        ],
      );
    }

    // Muestra el indicador de "Escuchando"
    if (voice.isListening) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.mic, color: Colors.red, size: 28),
              SizedBox(width: 12),
              Text('Escuchando...',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            ],
          ),
          // Muestra el texto reconocido en tiempo real
          if (voice.lastText.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              '"${voice.lastText}"',
              style: const TextStyle(
                  color: Colors.grey, fontStyle: FontStyle.italic),
            ),
          ]
        ],
      );
    }

    // Estado por defecto o si hay un error de inicialización
    return const Text('Di un comando, como "añadir dos coca-colas"',
        style: TextStyle(fontSize: 16));
  }
}