import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:mobile/models/sale.dart';
import 'package:mobile/services/sales_service.dart';

class PaymentMethodsScreen extends StatefulWidget {
  final Sale sale;
  const PaymentMethodsScreen({super.key, required this.sale});

  @override
  State<PaymentMethodsScreen> createState() => _PaymentMethodsScreenState();
}

class _PaymentMethodsScreenState extends State<PaymentMethodsScreen> {
  bool _processing = false;

  Future<void> _handlePayment(
    Future<void> Function(BuildContext) paymentAction,
  ) async {
    if (_processing) return;

    setState(() => _processing = true);

    try {
      await paymentAction(context);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('¡Pago completado con éxito!'),
          backgroundColor: Colors.green,
        ),
      );

      Navigator.of(context).popUntil((route) => route.isFirst);
    } catch (e) {
      if (!mounted) return;

      if (!e.toString().contains('canceled')) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error en el pago: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (!mounted) return;
      setState(() => _processing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final sale = widget.sale;

    return Scaffold(
      appBar: AppBar(title: Text('Pagar Venta ${sale.folio}')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildSaleSummary(sale),
            const SizedBox(height: 24),
            const Text(
              'Selecciona una opción de pago',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            // 💵 EFECTIVO
            _PaymentOptionTile(
              icon: Icons.payments_rounded,
              iconColor: Colors.green,
              title: 'Registrar pago en efectivo',
              subtitle: 'Marca la venta como pagada en caja.',
              enabled: !_processing,
              onTap:
                  () => _handlePayment(
                    (_) => salesService.confirmSalePayment(sale.id),
                  ),
            ),
            const SizedBox(height: 12),

            // 💳 TARJETA (solo móvil)
            _PaymentOptionTile(
              icon: Icons.credit_card_rounded,
              iconColor: Colors.indigo,
              title: 'Pagar con tarjeta',
              subtitle:
                  kIsWeb
                      ? 'Disponible solo en la app móvil (Android/iOS).'
                      : 'Paga con tarjeta de crédito o débito.',
              enabled: !_processing,
              onTap: () {
                if (kIsWeb) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'El pago con tarjeta solo está disponible en Android/iOS.',
                      ),
                      backgroundColor: Colors.orange,
                    ),
                  );
                  return;
                }

                _handlePayment(
                  (ctx) => salesService.payWithCardStripe(ctx, sale),
                );
              },
            ),
            const SizedBox(height: 12),

            // 🔳 QR
            _PaymentOptionTile(
              icon: Icons.qr_code_rounded,
              iconColor: Colors.deepPurple,
              title: 'Pagar con QR',
              subtitle: 'Genera un código QR para transferencia bancaria.',
              enabled: !_processing,
              onTap:
                  () => _handlePayment(
                    (ctx) => salesService.payWithQr(ctx, sale),
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
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Resumen de la venta',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Folio: ${sale.folio}'),
                      if (sale.clienteNombre != null)
                        Text(
                          'Cliente: ${sale.clienteNombre}',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 12),
                        ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text(
                      'Total',
                      style: TextStyle(fontSize: 12, color: Colors.black54),
                    ),
                    Text(
                      'Bs. ${sale.total.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _PaymentOptionTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;
  final bool enabled;
  final VoidCallback onTap;

  const _PaymentOptionTile({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    required this.enabled,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final bg = enabled ? Colors.white : Colors.grey.shade100;

    return InkWell(
      onTap: enabled ? onTap : null,
      borderRadius: BorderRadius.circular(18),
      child: Ink(
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(18),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: iconColor.withOpacity(0.08),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: iconColor, size: 22),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right_rounded, color: Colors.black26),
          ],
        ),
      ),
    );
  }
}
