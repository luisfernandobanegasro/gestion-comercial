// lib/services/sales_service.dart

import 'package:flutter/foundation.dart'; // Para kIsWeb
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:mobile/widgets/qr_payment_dialog.dart';
import '../models/sale.dart';
import '../providers/cart_provider.dart';
import 'api_client.dart';

/// Servicio para gestionar todas las operaciones relacionadas con ventas y pagos.
class SalesService {
  /// Obtiene el historial de ventas del usuario autenticado desde el backend.
  Future<List<Sale>> fetchMySales() async {
    final data = await apiClient.get('/ventas/ventas/');
    final list = data as List;
    return list
        .map((item) => Sale.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Obtiene el detalle completo de una venta específica, incluyendo sus items.
  Future<Sale> fetchSaleDetail(int saleId) async {
    final data = await apiClient.get('/ventas/ventas/$saleId/');
    return Sale.fromJson(data as Map<String, dynamic>);
  }

  /// Crea una venta en estado 'pendiente' en el backend a partir del carrito actual.
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

  /// Confirma una venta en el backend. Se usa para pagos en efectivo o QR.
  /// El backend se encarga de cambiar el estado de la venta y actualizar el stock.
  Future<void> confirmSalePayment(int saleId) async {
    // Coincide con el @action confirmar_pago del VentaViewSet
    await apiClient.post('/ventas/ventas/$saleId/confirmar_pago/');
  }

  /// Ejecuta el flujo completo para pagar con tarjeta de crédito/débito usando Stripe.
  ///
  /// IMPORTANTE:
  /// - En Android/iOS usa Stripe PaymentSheet.
  /// - En Web lanza una excepción explicando que no está disponible.
  /// - La confirmación final se hace contra /pagos/stripe/confirmar/ en tu backend.
  Future<void> payWithCardStripe(BuildContext context, Sale sale) async {
    // 🔒 Protección: Stripe PaymentSheet NO funciona en Web.
    if (kIsWeb) {
      throw Exception(
        'El pago con tarjeta solo está disponible en la app móvil (Android/iOS).',
      );
    }

    // 1. Crear el PaymentIntent en nuestro backend.
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

    // 2. Inicializar el formulario de pago de Stripe con el clientSecret.
    await Stripe.instance.initPaymentSheet(
      paymentSheetParameters: SetupPaymentSheetParameters(
        paymentIntentClientSecret: clientSecret,
        merchantDisplayName: 'SmartSales365', // Nombre de tu negocio
        style:
            Theme.of(context).brightness == Brightness.dark
                ? ThemeMode.dark
                : ThemeMode.light,
      ),
    );

    // 3. Mostrar el formulario al usuario. Stripe maneja la confirmación con sus servidores.
    await Stripe.instance.presentPaymentSheet();

    // 4. Si `presentPaymentSheet` no lanzó una excepción, el pago fue exitoso
    //    en Stripe. Ahora confirmamos el pago en nuestro backend de pagos,
    //    que a su vez marcará la venta como pagada, etc.
    await apiClient.post(
      '/pagos/stripe/confirmar/',
      body: {'venta_id': sale.id},
    );
  }

  /// Ejecuta el flujo completo para pagar con un código QR.
  Future<void> payWithQr(BuildContext context, Sale sale) async {
    // 1. Obtener datos de configuración del backend (datos del banco, etc.).
    final config = await apiClient.get('/configuracion/');

    // 2. Preparar el contenido (payload) para el código QR.
    final qrPayload = {
      'folio': sale.folio,
      'monto': sale.total,
      'moneda': "BOB",
      'concepto': config['glosa_qr'] ?? "Pago de productos",
    };

    if (!context.mounted) return;

    // 3. Mostrar un diálogo que contiene el widget del QR.
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (ctx) => QrPaymentDialog(
            qrData: qrPayload,
            bankInfo: config,
            onConfirm: () => Navigator.of(ctx).pop(true),
          ),
    );

    // 4. Si el usuario presionó "He realizado el pago", confirmamos la venta.
    if (confirmed == true) {
      await confirmSalePayment(sale.id);
    }
  }
}

/// Instancia global del servicio para un acceso fácil desde cualquier parte de la app.
final salesService = SalesService();
