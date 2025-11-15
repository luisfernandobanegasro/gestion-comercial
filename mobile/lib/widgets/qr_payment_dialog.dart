// lib/widgets/qr_payment_dialog.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:mobile/widgets/primary_button.dart';
import 'package:qr_flutter/qr_flutter.dart';

class QrPaymentDialog extends StatelessWidget {
  final Map<String, dynamic> qrData;
  final Map<String, dynamic> bankInfo;
  final VoidCallback onConfirm;

  const QrPaymentDialog({
    super.key,
    required this.qrData,
    required this.bankInfo,
    required this.onConfirm,
  });

  @override
  Widget build(BuildContext context) {
    final qrString = jsonEncode(qrData);
    final monto = qrData['monto'] as num;

    return AlertDialog(
      title: Text('Pagar Bs. ${monto.toStringAsFixed(2)} con QR'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 220,
              height: 220,
              child: QrImageView(
                data: qrString,
                version: QrVersions.auto,
                size: 220,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Transferencia Alternativa',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text('Banco: ${bankInfo['nombre_banco'] ?? 'N/A'}'),
            Text('Cuenta: ${bankInfo['numero_cuenta'] ?? 'N/A'}'),
            Text('Titular: ${bankInfo['nombre_titular'] ?? 'N/A'}'),
            const SizedBox(height: 24),
            PrimaryButton(
              label: 'He realizado el pago',
              onPressed: onConfirm,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
      ],
    );
  }
}