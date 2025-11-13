// lib/models/product.dart

class Offer {
  final int id;
  final String name;
  final double discountPercent;

  Offer({required this.id, required this.name, required this.discountPercent});

  factory Offer.fromJson(Map<String, dynamic> json) {
    return Offer(
      id: json['id'] as int,
      name: json['nombre'] ?? '',
      discountPercent:
          double.tryParse(json['porcentaje_descuento'].toString()) ?? 0.0,
    );
  }
}

class Product {
  final String id;
  final String name;
  final String? sku; // si no lo usas, puedes quitarlo
  final double price; // precio original (precio)
  final double finalPrice; // precio_final (con oferta)
  final int stock;
  final String? imageUrl; // imagen_url
  final String? brandName; // marca_nombre
  final String? categoryName; // categoria_nombre
  final Offer? activeOffer; // oferta_activa

  Product({
    required this.id,
    required this.name,
    required this.price,
    required this.finalPrice,
    required this.stock,
    this.sku,
    this.imageUrl,
    this.brandName,
    this.categoryName,
    this.activeOffer,
  });

  /// Precio que se muestra en la app (ya con descuento si aplica)
  double get displayPrice => finalPrice;

  bool get hasDiscount => activeOffer != null && finalPrice < price;

  factory Product.fromJson(Map<String, dynamic> json) {
    final rawPrice = double.tryParse(json['precio'].toString()) ?? 0.0;
    final rawFinal =
        json['precio_final'] != null
            ? double.tryParse(json['precio_final'].toString()) ?? rawPrice
            : rawPrice;

    Offer? oferta;
    if (json['oferta_activa'] != null) {
      oferta = Offer.fromJson(json['oferta_activa']);
    }

    return Product(
      id: json['id'].toString(),
      name: json['nombre'] ?? '',
      sku: json['codigo'], // o 'modelo' según lo que quieras mostrar
      price: rawPrice,
      finalPrice: rawFinal,
      stock: json['stock'] ?? 0,
      imageUrl: json['imagen_url'],
      brandName: json['marca_nombre'],
      categoryName: json['categoria_nombre'],
      activeOffer: oferta,
    );
  }
}
