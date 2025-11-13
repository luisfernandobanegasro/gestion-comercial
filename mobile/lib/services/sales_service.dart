// lib/services/sales_service.dart

import 'package:flutter_stripe/flutter_stripe.dart' as stripe;

import '../models/sale.dart';
import '../providers/cart_provider.dart';
import 'api_client.dart';

class SalesService {
  // ================= CREAR VENTA DESDE CARRITO =================

  /// Crea una venta en estado 'pendiente' a partir del carrito,
  /// usando el endpoint estándar de ventas (NO desde-carrito).
  Future<Sale> createPendingSaleFromCart(
    CartProvider cart, {
    int? clientId,
  }) async {
    final items =
        cart.items
            .map(
              (item) => {
                'producto': int.parse(item.product.id),
                'cantidad': item.quantity,
                // usamos precio final (con oferta) como precio_unit
                'precio_unit': item.product.displayPrice,
              },
            )
            .toList();

    final body = <String, dynamic>{
      'items': items,
      if (clientId != null) 'cliente': clientId,
    };

    // Si en ventas/urls.py tienes router.register("ventas", ...)
    // entonces la URL final es '/ventas/ventas/'
    final data = await apiClient.post('/ventas/ventas/', body: body);
    return Sale.fromJson(data as Map<String, dynamic>);
  }

  // ================= HISTORIAL / DETALLE =================

  /// Historial de ventas del usuario actual (el backend ya filtra por cliente).
  Future<List<Sale>> fetchMySales() async {
    final data = await apiClient.get('/ventas/ventas/');
    final results =
        (data is Map && data['results'] != null) ? data['results'] : data;
    return (results as List).map((e) => Sale.fromJson(e)).toList();
  }

  /// Detalle de una venta
  Future<Sale> fetchSaleDetail(int id) async {
    final data = await apiClient.get('/ventas/ventas/$id/');
    return Sale.fromJson(data as Map<String, dynamic>);
  }

  // ================= PAGOS =================

  /// Registrar pago en efectivo (usa /ventas/{id}/confirmar_pago/)
  Future<void> confirmCashPayment(int saleId) async {
    await apiClient.post('/ventas/ventas/$saleId/confirmar_pago/');
  }

  /// Crea (o recupera) un PaymentIntent en Stripe desde tu backend
  /// y devuelve el clientSecret.
  Future<String> _createStripeIntent(
    Sale sale, {
    String? idempotencyKey,
  }) async {
    final body = <String, dynamic>{
      'venta_id': sale.id,
      if (idempotencyKey != null) 'idempotency_key': idempotencyKey,
    };

    final data =
        await apiClient.post('/pagos/stripe/intent/', body: body) as Map;
    final clientSecret = data['clientSecret'] as String?;
    if (clientSecret == null || clientSecret.isEmpty) {
      throw Exception('El backend no devolvió clientSecret de Stripe');
    }
    return clientSecret;
  }

  /// Confirma el pago en tu backend (marca la venta como pagada y actualiza Pago).
  Future<void> _confirmStripeInBackend(
    Sale sale, {
    String? idempotencyKey,
  }) async {
    final body = <String, dynamic>{
      'venta_id': sale.id,
      'monto': sale.total.toStringAsFixed(2),
      if (idempotencyKey != null) 'idempotency_key': idempotencyKey,
    };

    await apiClient.post('/pagos/stripe/confirmar/', body: body);
  }

  /// Flujo completo de pago con tarjeta usando Stripe Payment Sheet:
  /// 1) Crear PaymentIntent en backend → clientSecret
  /// 2) Mostrar PaymentSheet de Stripe en Flutter
  /// 3) Si el pago se completa → confirmar en backend
  Future<void> payWithCardStripe(Sale sale) async {
    // idempotency_key sencillo (puedes mejorarlo si quieres)
    final idemKey = DateTime.now().millisecondsSinceEpoch.toString();

    // 1) Crear / recuperar PaymentIntent en tu backend
    final clientSecret = await _createStripeIntent(
      sale,
      idempotencyKey: idemKey,
    );

    // 2) Inicializar Payment Sheet
    await stripe.Stripe.instance.initPaymentSheet(
      paymentSheetParameters: stripe.SetupPaymentSheetParameters(
        paymentIntentClientSecret: clientSecret,
        merchantDisplayName: 'SmartSales365',
      ),
    );

    // 3) Mostrar Payment Sheet
    try {
      await stripe.Stripe.instance.presentPaymentSheet();
    } on stripe.StripeException catch (e) {
      // Si el usuario cancela, no lanzamos error "feo"
      if (e.error.code == stripe.FailureCode.Canceled) {
        return;
      }
      rethrow;
    }

    // 4) Si llegamos aquí, el pago en Stripe fue OK → confirmar en backend
    await _confirmStripeInBackend(sale, idempotencyKey: idemKey);
  }

  /// Pago con QR: por ahora reutilizamos el mismo endpoint de confirmación
  /// (simulado). Más adelante puedes crear un endpoint específico para QR.
  Future<void> payWithQr(Sale sale) async {
    await _confirmStripeInBackend(sale);
  }
}

final salesService = SalesService();
