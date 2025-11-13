// lib/services/product_service.dart

import '../models/product.dart';
import 'api_client.dart';

class ProductService {
  Future<List<Product>> fetchProducts() async {
    final data = await apiClient.get('/catalogo/productos/');
    final results =
        (data is Map && data['results'] != null) ? data['results'] : data;
    return (results as List).map((e) => Product.fromJson(e)).toList();
  }
}

final productService = ProductService();
