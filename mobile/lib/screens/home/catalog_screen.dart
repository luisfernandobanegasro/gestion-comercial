// lib/screens/home/catalog_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../models/product.dart';
import '../../providers/cart_provider.dart';
import '../../providers/voice_provider.dart';
import '../../services/product_service.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/product_card.dart';
import '../../widgets/primary_button.dart';

class CatalogScreen extends StatefulWidget {
  const CatalogScreen({super.key});

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  List<Product> _products = [];
  bool _loading = true;
  String? _error;

  // 🔎 Búsqueda & filtros
  String _searchText = '';
  String? _selectedBrand;
  String? _selectedCategory;
  List<String> _brands = [];
  List<String> _categories = [];

  /// Muestra el SnackBar con el último comando de voz,
  /// verificando que el widget siga montado para evitar errores.
  void _showVoiceSnack(VoiceProvider voice) {
    if (!mounted) return;
    final txt = voice.lastText.trim();
    if (txt.isEmpty) return;

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('Comando procesado: "$txt"')));
  }

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

        // Construimos listas de marcas y categorías para los dropdowns
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

  /// Aplica búsqueda por nombre y filtros de marca/categoría
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

  Widget _buildFilters() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      child: Column(
        children: [
          // Buscador por nombre
          TextField(
            decoration: const InputDecoration(
              prefixIcon: Icon(Icons.search),
              labelText: 'Buscar producto',
              border: OutlineInputBorder(),
              isDense: true,
            ),
            onChanged: (value) {
              setState(() {
                _searchText = value;
              });
            },
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedBrand,
                  isDense: true,
                  decoration: const InputDecoration(
                    labelText: 'Marca',
                    border: OutlineInputBorder(),
                  ),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('Todas')),
                    ..._brands.map(
                      (b) => DropdownMenuItem(value: b, child: Text(b)),
                    ),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _selectedBrand = value;
                    });
                  },
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedCategory,
                  isDense: true,
                  decoration: const InputDecoration(
                    labelText: 'Categoría',
                    border: OutlineInputBorder(),
                  ),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('Todas')),
                    ..._categories.map(
                      (c) => DropdownMenuItem(value: c, child: Text(c)),
                    ),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _selectedCategory = value;
                    });
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final voice = context.watch<VoiceProvider>();

    return Column(
      children: [
        // Header
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
          child: Row(
            children: [
              const Expanded(
                child: Text(
                  'Catálogo',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                ),
              ),
              IconButton(
                iconSize: 32,
                icon: Icon(
                  voice.isListening ? Icons.mic : Icons.mic_none,
                  color: voice.isListening ? Colors.red : Colors.black54,
                ),
                onPressed:
                    _products.isEmpty
                        ? null
                        : () {
                          final cart = context.read<CartProvider>();
                          if (voice.isListening) {
                            voice.stop();
                          } else {
                            voice.startListening(
                              cart,
                              _products,
                              () => _showVoiceSnack(voice),
                            );
                          }
                        },
                tooltip: 'Comprar por voz',
              ),
            ],
          ),
        ),
        if (voice.lastText.isNotEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              'Último comando: ${voice.lastText}',
              style: const TextStyle(fontSize: 12, color: Colors.black54),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        const SizedBox(height: 8),

        // 🔎 Filtros
        _buildFilters(),

        // Body
        Expanded(child: _buildBody(context)),
      ],
    );
  }

  Widget _buildBody(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return EmptyState(
        icon: Icons.error_outline,
        title: 'Ocurrió un error al cargar los productos',
        message: _error,
        actionLabel: 'Reintentar',
        onAction: _load,
      );
    }

    if (_products.isEmpty) {
      return const EmptyState(
        icon: Icons.inventory_2_outlined,
        title: 'No hay productos disponibles',
        message:
            'Cuando se registren productos en el catálogo aparecerán aquí.',
      );
    }

    final cart = context.watch<CartProvider>();
    final filtered = _filteredProducts();

    if (filtered.isEmpty) {
      return const EmptyState(
        icon: Icons.search_off_outlined,
        title: 'Sin resultados',
        message: 'No se encontraron productos con esos filtros.',
      );
    }

    return RefreshIndicator(
      onRefresh: _load,
      child: LayoutBuilder(
        builder: (context, constraints) {
          // 2 columnas en móviles, 3 o 4 en pantallas más grandes
          final crossAxisCount =
              constraints.maxWidth > 900
                  ? 4
                  : constraints.maxWidth > 600
                  ? 3
                  : 2;

          return GridView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: filtered.length,
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 0.72,
            ),
            itemBuilder: (context, index) {
              final product = filtered[index];
              return ProductCard(
                product: product,
                onAddToCart: () {
                  cart.add(product);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('${product.name} agregado al carrito'),
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
    int quantity = 1;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 16,
            top: 16,
            bottom: MediaQuery.of(context).viewInsets.bottom + 16,
          ),
          child: StatefulBuilder(
            builder: (context, setModalState) {
              final hasDiscount = product.hasDiscount;

              return SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          product.name,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close),
                          onPressed: () => Navigator.of(context).pop(),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child:
                          product.imageUrl == null
                              ? Container(
                                height: 180,
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
                                height: 200,
                                fit: BoxFit.cover,
                                errorBuilder:
                                    (_, __, ___) => Container(
                                      height: 180,
                                      color: Colors.grey.shade100,
                                      child: const Center(
                                        child: Icon(
                                          Icons.inventory_2_outlined,
                                          size: 40,
                                          color: Colors.black26,
                                        ),
                                      ),
                                    ),
                              ),
                    ),
                    const SizedBox(height: 16),

                    if (hasDiscount) ...[
                      Text(
                        'Precio original: Bs. ${product.price.toStringAsFixed(2)}',
                        style: const TextStyle(
                          decoration: TextDecoration.lineThrough,
                          color: Colors.black45,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Precio oferta: Bs. ${product.displayPrice.toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          color: Colors.redAccent,
                        ),
                      ),
                    ] else
                      Text(
                        'Precio: Bs. ${product.displayPrice.toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),

                    const SizedBox(height: 4),
                    Text(
                      'Stock disponible: ${product.stock}',
                      style: const TextStyle(color: Colors.black54),
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Descripción',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      product.sku?.isNotEmpty == true
                          ? 'Código: ${product.sku}'
                          : 'Este producto aún no tiene una descripción detallada.',
                      style: const TextStyle(color: Colors.black87),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        const Text(
                          'Cantidad:',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(width: 12),
                        Container(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(999),
                            border: Border.all(color: Colors.grey.shade300),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.remove),
                                onPressed:
                                    quantity > 1
                                        ? () {
                                          setModalState(() {
                                            quantity--;
                                          });
                                        }
                                        : null,
                              ),
                              Text('$quantity'),
                              IconButton(
                                icon: const Icon(Icons.add),
                                onPressed: () {
                                  setModalState(() {
                                    quantity++;
                                  });
                                },
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    PrimaryButton(
                      label: 'Añadir al carrito',
                      onPressed: () {
                        cart.add(product, quantity: quantity);
                        Navigator.of(context).pop();
                        ScaffoldMessenger.of(this.context).showSnackBar(
                          SnackBar(
                            content: Text(
                              '$quantity x ${product.name} agregado(s) al carrito',
                            ),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              );
            },
          ),
        );
      },
    );
  }
}
