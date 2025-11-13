// lib/screens/home/payment_methods_screen.dart

import 'package:flutter/material.dart';

import '../../models/sale.dart';
import '../../services/sales_service.dart';
import '../../widgets/primary_button.dart';

class PaymentMethodsScreen extends StatefulWidget {
  final Sale sale;

  const PaymentMethodsScreen({super.key, required this.sale});

  @override
  State<PaymentMethodsScreen> createState() => _PaymentMethodsScreenState();
}

class _PaymentMethodsScreenState extends State<PaymentMethodsScreen> {
  bool _processing = false;
  String? _error;

  Future<void> _handlePayment(
    Future<void> Function() action,
    String successMsg,
  ) async {
    if (_processing) return;
    setState(() {
      _processing = true;
      _error = null;
    });

    try {
      await action();
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(successMsg)));
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error al procesar pago: $e')));
    } finally {
      if (!mounted) return;
      setState(() {
        _processing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final sale = widget.sale;

    return Scaffold(
      appBar: AppBar(title: Text('Venta ${sale.folio}')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Resumen de la venta
            _buildSaleSummary(sale),
            const SizedBox(height: 16),

            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),

            // Métodos de pago
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Opciones de pago',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  PrimaryButton(
                    label:
                        _processing
                            ? 'Procesando...'
                            : 'Registrar pago en efectivo',
                    onPressed:
                        _processing
                            ? null
                            : () => _handlePayment(
                              () => salesService.confirmCashPayment(sale.id),
                              'Pago en efectivo registrado',
                            ),
                  ),
                  const SizedBox(height: 8),
                  PrimaryButton(
                    label: _processing ? 'Procesando...' : 'Pagar con tarjeta',
                    onPressed:
                        _processing
                            ? null
                            : () => _handlePayment(
                              () => salesService.payWithCardStripe(sale),
                              'Pago con tarjeta completado',
                            ),
                  ),
                  const SizedBox(height: 8),
                  PrimaryButton(
                    label: _processing ? 'Procesando...' : 'Pagar con QR',
                    onPressed:
                        _processing
                            ? null
                            : () => _handlePayment(
                              () => salesService.payWithQr(sale),
                              'Pago con QR registrado',
                            ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSaleSummary(Sale sale) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Folio: ${sale.folio}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            if (sale.clienteNombre != null)
              Text('Cliente: ${sale.clienteNombre}'),
            const SizedBox(height: 4),
            Text('Total: Bs. ${sale.total.toStringAsFixed(2)}'),
            const Divider(height: 24),
            const Text('Items', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            ...sale.items.map(
              (it) => Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(child: Text(it.productName)),
                  Text('x${it.quantity}'),
                  const SizedBox(width: 8),
                  Text('Bs. ${it.subtotal.toStringAsFixed(2)}'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
