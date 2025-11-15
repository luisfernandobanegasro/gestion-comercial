import 'package:flutter/material.dart';
import 'package:mobile/providers/cart_provider.dart';
import 'package:mobile/providers/voice_provider.dart';
import 'package:mobile/services/product_service.dart';
import 'package:mobile/widgets/empty_state.dart';
import 'package:mobile/widgets/product_card.dart';
import 'package:mobile/widgets/voice_input_panel.dart';
import 'package:provider/provider.dart';
import '../../models/product.dart';

class CatalogScreen extends StatefulWidget {
  const CatalogScreen({super.key});

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  List<Product> _products = [];
  bool _loading = true;
  String? _error;

  String _searchText = '';
  String? _selectedBrand;
  String? _selectedCategory;
  List<String> _brands = [];
  List<String> _categories = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final items = await productService.fetchProducts();
      if (!mounted) return;
      setState(() {
        _products = items;
        _brands =
            _products
                .where((p) => (p.brandName ?? '').isNotEmpty)
                .map((p) => p.brandName!)
                .toSet()
                .toList()
              ..sort();
        _categories =
            _products
                .where((p) => (p.categoryName ?? '').isNotEmpty)
                .map((p) => p.categoryName!)
                .toSet()
                .toList()
              ..sort();
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
      });
    } finally {
      if (!mounted) return;
      setState(() {
        _loading = false;
      });
    }
  }

  List<Product> _filteredProducts() {
    return _products.where((p) {
      final matchesSearch =
          _searchText.isEmpty ||
          p.name.toLowerCase().contains(_searchText.toLowerCase());
      final matchesBrand =
          _selectedBrand == null || p.brandName == _selectedBrand;
      final matchesCategory =
          _selectedCategory == null || p.categoryName == _selectedCategory;
      return matchesSearch && matchesBrand && matchesCategory;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomSheet: const VoiceInputPanel(),
      body: SafeArea(
        child: Column(
          children: [
            // Título
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      'Catálogo de Productos',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 4),
            _buildFilters(),
            Expanded(child: _buildGridContent()),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed:
            _products.isEmpty
                ? null
                : () {
                  final cart = context.read<CartProvider>();
                  final voice = context.read<VoiceProvider>();
                  voice.activateAndStartListening(cart, _products);
                },
        icon: const Icon(Icons.mic),
        label: const Text('Comprar por voz'),
      ),
    );
  }

  Widget _buildFilters() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      child: Card(
        elevation: 1,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
          child: Column(
            children: [
              // Buscador
              TextField(
                decoration: InputDecoration(
                  prefixIcon: const Icon(Icons.search),
                  hintText: 'Buscar producto',
                  isDense: true,
                  filled: true,
                  fillColor: Colors.grey.shade100,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: BorderSide.none,
                  ),
                ),
                onChanged: (value) => setState(() => _searchText = value),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String?>(
                      value: _selectedBrand,
                      isDense: true,
                      isExpanded: true,
                      decoration: InputDecoration(
                        labelText: 'Marca',
                        isDense: true,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      items: [
                        const DropdownMenuItem<String?>(
                          value: null,
                          child: Text('Todas'),
                        ),
                        ..._brands.map(
                          (b) => DropdownMenuItem<String?>(
                            value: b,
                            child: Text(b),
                          ),
                        ),
                      ],
                      onChanged:
                          (value) => setState(() => _selectedBrand = value),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: DropdownButtonFormField<String?>(
                      value: _selectedCategory,
                      isDense: true,
                      isExpanded: true,
                      decoration: InputDecoration(
                        labelText: 'Categoría',
                        isDense: true,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      items: [
                        const DropdownMenuItem<String?>(
                          value: null,
                          child: Text('Todas'),
                        ),
                        ..._categories.map(
                          (c) => DropdownMenuItem<String?>(
                            value: c,
                            child: Text(c),
                          ),
                        ),
                      ],
                      onChanged:
                          (value) => setState(() => _selectedCategory = value),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGridContent() {
    if (_loading) return const Center(child: CircularProgressIndicator());

    if (_error != null) {
      return EmptyState(
        icon: Icons.error_outline,
        title: 'Ocurrió un error',
        message: _error,
        actionLabel: 'Reintentar',
        onAction: _load,
      );
    }

    if (_products.isEmpty) {
      return const EmptyState(
        icon: Icons.inventory_2_outlined,
        title: 'No hay productos',
        message: 'Cuando se registren productos aparecerán aquí.',
      );
    }

    final filtered = _filteredProducts();
    if (filtered.isEmpty) {
      return const EmptyState(
        icon: Icons.search_off_outlined,
        title: 'Sin resultados',
        message: 'No hay productos que coincidan con los filtros.',
      );
    }

    return RefreshIndicator(
      onRefresh: _load,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final crossAxisCount =
              constraints.maxWidth > 900
                  ? 4
                  : (constraints.maxWidth > 600 ? 3 : 2);

          return GridView.builder(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 90),
            itemCount: filtered.length,
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 0.7,
            ),
            itemBuilder: (context, index) {
              final product = filtered[index];
              return ProductCard(
                product: product,
                onAddToCart: () {
                  context.read<CartProvider>().add(product);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('${product.name} agregado al carrito'),
                      duration: const Duration(seconds: 1),
                    ),
                  );
                },
                onOpenDetail: () => _showProductDetail(context, product),
              );
            },
          );
        },
      ),
    );
  }

  void _showProductDetail(BuildContext context, Product product) {
    final cart = context.read<CartProvider>();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (modalContext) {
        return Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 16,
            top: 16,
            bottom: MediaQuery.of(modalContext).viewInsets.bottom + 16,
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        product.name,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () => Navigator.of(modalContext).pop(),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child:
                      product.imageUrl == null
                          ? Container(
                            height: 200,
                            color: Colors.grey.shade100,
                            child: const Center(
                              child: Icon(
                                Icons.inventory_2_outlined,
                                size: 40,
                                color: Colors.black26,
                              ),
                            ),
                          )
                          : Image.network(
                            product.imageUrl!,
                            height: 220,
                            fit: BoxFit.cover,
                            errorBuilder:
                                (_, __, ___) => Container(
                                  height: 200,
                                  color: Colors.grey.shade100,
                                  child: const Center(
                                    child: Icon(
                                      Icons.warning_amber_rounded,
                                      size: 40,
                                      color: Colors.black26,
                                    ),
                                  ),
                                ),
                          ),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  icon: const Icon(Icons.add_shopping_cart),
                  label: const Text('Añadir al carrito'),
                  onPressed: () {
                    cart.add(product);
                    Navigator.of(modalContext).pop();
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('${product.name} añadido al carrito'),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
