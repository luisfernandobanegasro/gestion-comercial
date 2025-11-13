// lib/screens/home/cart_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/cart_provider.dart';
import '../../services/sales_service.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/primary_button.dart';
import 'payment_methods_screen.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  bool _submitting = false;

  Future<void> _finalizarCompra(BuildContext context) async {
    final cart = context.read<CartProvider>();
    if (cart.isEmpty || _submitting) return;

    setState(() {
      _submitting = true;
    });

    try {
      // 1️⃣ Crear venta pendiente
      final sale = await salesService.createPendingSaleFromCart(cart);

      // 2️⃣ Limpiar carrito
      cart.clear();

      if (!mounted) return;

      // 3️⃣ Ir a pantalla de métodos de pago
      await Navigator.of(context).push(
        MaterialPageRoute(builder: (_) => PaymentMethodsScreen(sale: sale)),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error al crear la venta: $e')));
    } finally {
      if (!mounted) return;
      setState(() {
        _submitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartProvider>();

    return Column(
      children: [
        const SizedBox(height: 16),
        const Text(
          'Carrito de compras',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Expanded(
          child:
              cart.isEmpty
                  ? const EmptyState(
                    icon: Icons.shopping_cart_outlined,
                    title: 'Tu carrito está vacío',
                    message:
                        'Agrega productos desde el catálogo para comenzar la venta.',
                  )
                  : ListView.separated(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    itemCount: cart.items.length,
                    separatorBuilder: (_, __) => const Divider(height: 16),
                    itemBuilder: (context, index) {
                      final item = cart.items[index];
                      return Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  item.product.name,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.w600,
                                    fontSize: 14,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'PU: Bs. ${item.product.displayPrice.toStringAsFixed(2)}',
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: Colors.black54,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(999),
                              border: Border.all(color: Colors.grey.shade300),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.remove, size: 18),
                                  onPressed:
                                      () => context
                                          .read<CartProvider>()
                                          .decrease(item),
                                ),
                                Text('${item.quantity}'),
                                IconButton(
                                  icon: const Icon(Icons.add, size: 18),
                                  onPressed:
                                      () => context
                                          .read<CartProvider>()
                                          .increase(item),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          SizedBox(
                            width: 80,
                            child: Text(
                              'Bs. ${item.subtotal.toStringAsFixed(2)}',
                              textAlign: TextAlign.right,
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete_outline),
                            onPressed:
                                () => context.read<CartProvider>().remove(
                                  item.product,
                                ),
                          ),
                        ],
                      );
                    },
                  ),
        ),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.04),
                offset: const Offset(0, -2),
                blurRadius: 8,
              ),
            ],
          ),
          child: SafeArea(
            top: false,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Items: ${cart.totalItems}',
                      style: const TextStyle(fontSize: 13),
                    ),
                    Text(
                      'Total: Bs. ${cart.total.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                PrimaryButton(
                  label: _submitting ? 'Creando venta...' : 'Finalizar compra',
                  onPressed:
                      cart.isEmpty || _submitting
                          ? null
                          : () => _finalizarCompra(context),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
