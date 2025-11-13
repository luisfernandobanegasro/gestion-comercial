// lib/models/sale.dart

class SaleItem {
  final int id;
  final String productName;
  final int productId;
  final int quantity;
  final double unitPrice;
  final double subtotal;

  SaleItem({
    required this.id,
    required this.productName,
    required this.productId,
    required this.quantity,
    required this.unitPrice,
    required this.subtotal,
  });

  factory SaleItem.fromJson(Map<String, dynamic> json) {
    return SaleItem(
      id: json['id'] as int,
      productName: json['producto_nombre'] ?? '',
      productId: json['producto'] as int,
      quantity: json['cantidad'] as int,
      unitPrice: double.tryParse(json['precio_unit'].toString()) ?? 0.0,
      subtotal: double.tryParse(json['subtotal'].toString()) ?? 0.0,
    );
  }
}

class Sale {
  final int id;
  final String folio;
  final String estado;
  final double subtotal;
  final double descuento;
  final double impuestos;
  final double total;
  final String? clienteNombre;
  final DateTime createdAt;
  final List<SaleItem> items;

  Sale({
    required this.id,
    required this.folio,
    required this.estado,
    required this.subtotal,
    required this.descuento,
    required this.impuestos,
    required this.total,
    required this.createdAt,
    this.clienteNombre,
    this.items = const [],
  });

  factory Sale.fromJson(Map<String, dynamic> json) {
    final itemsJson = (json['items'] ?? []) as List;

    return Sale(
      id: json['id'] as int,
      folio: json['folio'] ?? '',
      estado: json['estado'] ?? '',
      subtotal: double.tryParse(json['subtotal'].toString()) ?? 0.0,
      descuento: double.tryParse(json['descuento'].toString()) ?? 0.0,
      impuestos: double.tryParse(json['impuestos'].toString()) ?? 0.0,
      total: double.tryParse(json['total'].toString()) ?? 0.0,
      clienteNombre: json['cliente_nombre'],
      createdAt: DateTime.tryParse(json['creado_en'] ?? '') ?? DateTime.now(),
      items: itemsJson.map((e) => SaleItem.fromJson(e)).toList(),
    );
  }
}
