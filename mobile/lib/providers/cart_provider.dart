// lib/providers/cart_provider.dart

import 'package:flutter/foundation.dart';

import '../models/cart_item.dart';
import '../models/product.dart';

class CartProvider extends ChangeNotifier {
  final List<CartItem> _items = [];

  /// Lista inmodificable de ítems en el carrito.
  List<CartItem> get items => List.unmodifiable(_items);

  /// Monto total del carrito.
  double get total => _items.fold(0.0, (sum, item) => sum + item.subtotal);

  /// Cantidad total de unidades (para el badge del carrito).
  int get totalItems => _items.fold(0, (sum, item) => sum + item.quantity);

  /// Indica si el carrito está vacío.
  bool get isEmpty => _items.isEmpty;

  /// Agrega un producto al carrito. Si ya existe, aumenta la cantidad.
  void add(Product product, {int quantity = 1}) {
    final index = _items.indexWhere((e) => e.product.id == product.id);
    if (index >= 0) {
      _items[index].quantity += quantity;
    } else {
      _items.add(CartItem(product: product, quantity: quantity));
    }
    notifyListeners();
  }

  /// Elimina completamente un producto del carrito.
  void remove(Product product) {
    _items.removeWhere((e) => e.product.id == product.id);
    notifyListeners();
  }

  /// Disminuye la cantidad de un producto (usado también por voice_provider).
  /// Si la cantidad llega a 0, elimina el producto del carrito.
  void removeOne(Product product) {
    final index = _items.indexWhere((e) => e.product.id == product.id);
    if (index >= 0) {
      if (_items[index].quantity > 1) {
        _items[index].quantity--;
      } else {
        _items.removeAt(index);
      }
      notifyListeners();
    }
  }

  /// Aumenta la cantidad de un ítem específico.
  void increase(CartItem item) {
    final index = _items.indexWhere((e) => e.product.id == item.product.id);
    if (index >= 0) {
      _items[index].quantity++;
      notifyListeners();
    }
  }

  /// Disminuye la cantidad de un ítem. Si llega a 0, lo elimina.
  void decrease(CartItem item) {
    final index = _items.indexWhere((e) => e.product.id == item.product.id);
    if (index >= 0) {
      if (_items[index].quantity > 1) {
        _items[index].quantity--;
      } else {
        _items.removeAt(index);
      }
      notifyListeners();
    }
  }

  /// Limpia completamente el carrito.
  void clear() {
    _items.clear();
    notifyListeners();
  }
}
