// lib/services/sales_service.dart
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:mobile/widgets/qr_payment_dialog.dart';
import '../models/sale.dart';
import '../providers/cart_provider.dart';
import 'api_client.dart';

class SalesService {
  /// Historial de ventas del usuario autenticado
  Future<List<Sale>> fetchMySales() async {
    final data = await apiClient.get('/ventas/ventas/');

    // Soporta lista simple o respuesta paginada { results: [...] }
    final List rawList;
    if (data is List) {
      rawList = data;
    } else if (data is Map && data['results'] is List) {
      rawList = data['results'] as List;
    } else {
      throw Exception('Formato inesperado al leer /ventas/ventas/');
    }

    return rawList
        .map((item) => Sale.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Detalle de una venta
  Future<Sale> fetchSaleDetail(int saleId) async {
    final data = await apiClient.get('/ventas/ventas/$saleId/');
    return Sale.fromJson(data as Map<String, dynamic>);
  }

  /// Crea una venta pendiente desde el carrito actual
  Future<Sale> createPendingSaleFromCart(CartProvider cart) async {
    final items =
        cart.items
            .map(
              (item) => {
                'producto': int.parse(item.product.id),
                'cantidad': item.quantity,
                'precio_unit': item.product.displayPrice,
              },
            )
            .toList();

    final body = <String, dynamic>{'items': items};
    final data = await apiClient.post('/ventas/ventas/', body: body);
    return Sale.fromJson(data as Map<String, dynamic>);
  }

  /// Confirma el pago de una venta (efectivo / QR ya pagado)
  Future<void> confirmSalePayment(int saleId) async {
    await apiClient.post('/ventas/ventas/$saleId/confirmar_pago/');
  }

  /// Pago con tarjeta usando Stripe PaymentSheet
  Future<void> payWithCardStripe(BuildContext context, Sale sale) async {
    if (kIsWeb) {
      throw Exception(
        'El pago con tarjeta solo está disponible en la app móvil (Android/iOS).',
      );
    }

    // 👇 Aquí tu backend debe crear el PaymentIntent usando el total de la venta
    // (sale.total). Desde Flutter solo enviamos el ID de la venta.
    final response = await apiClient.post(
      '/pagos/stripe/intent/',
      body: {'venta_id': sale.id},
    );

    final clientSecret = response['clientSecret'] as String?;
    if (clientSecret == null || clientSecret.isEmpty) {
      throw Exception(
        'El servidor no proporcionó un clientSecret válido para el pago.',
      );
    }

    if (!context.mounted) return;

    await Stripe.instance.initPaymentSheet(
      paymentSheetParameters: SetupPaymentSheetParameters(
        paymentIntentClientSecret: clientSecret,
        merchantDisplayName: 'SmartSales365',
        style:
            Theme.of(context).brightness == Brightness.dark
                ? ThemeMode.dark
                : ThemeMode.light,
      ),
    );

    await Stripe.instance.presentPaymentSheet();

    // Confirmar en el backend que el pago de esa venta se completó
    await apiClient.post(
      '/pagos/stripe/confirmar/',
      body: {'venta_id': sale.id},
    );
  }

  /// Pago con QR
  Future<void> payWithQr(BuildContext context, Sale sale) async {
    // Puede venir como Map o como {results:[...]} / lista
    final cfg = await apiClient.get('/configuracion/');

    Map<String, dynamic> config;
    if (cfg is Map<String, dynamic>) {
      config = cfg;
    } else if (cfg is Map &&
        cfg['results'] is List &&
        cfg['results'].isNotEmpty) {
      config = cfg['results'][0] as Map<String, dynamic>;
    } else if (cfg is List && cfg.isNotEmpty) {
      config = cfg[0] as Map<String, dynamic>;
    } else {
      throw Exception('Formato inesperado de /configuracion/');
    }

    final qrPayload = {
      'folio': sale.folio,
      'monto': sale.total,
      'moneda': 'BOB',
      'concepto': config['glosa_qr'] ?? 'Pago de productos',
    };

    if (!context.mounted) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (ctx) => QrPaymentDialog(
            qrData: qrPayload,
            bankInfo: config,
            onConfirm: () => Navigator.of(ctx).pop(true),
          ),
    );

    if (confirmed == true) {
      await confirmSalePayment(sale.id);
    }
  }
}

final salesService = SalesService();
