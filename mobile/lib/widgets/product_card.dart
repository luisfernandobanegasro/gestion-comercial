import 'package:flutter/material.dart';
import '../models/product.dart';

class ProductCard extends StatefulWidget {
  final Product product;
  final VoidCallback onAddToCart;
  final VoidCallback? onOpenDetail;

  const ProductCard({
    super.key,
    required this.product,
    required this.onAddToCart,
    this.onOpenDetail,
  });

  @override
  State<ProductCard> createState() => _ProductCardState();
}

class _ProductCardState extends State<ProductCard> {
  double _scale = 1.0;

  void _handleAdd() {
    // 1) Lógica de carrito
    widget.onAddToCart();

    // 2) Animación simple de escala
    setState(() => _scale = 0.85);
    Future.delayed(const Duration(milliseconds: 80), () {
      if (!mounted) return;
      setState(() => _scale = 1.0);
    });
  }

  @override
  Widget build(BuildContext context) {
    final hasDiscount = widget.product.hasDiscount;
    final primary = Theme.of(context).colorScheme.primary;

    return GestureDetector(
      onTap: widget.onOpenDetail ?? widget.onAddToCart,
      child: Card(
        elevation: 2,
        shadowColor: Colors.black.withOpacity(0.05),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Imagen + badge de oferta
            Expanded(
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(18),
                    ),
                    child: _buildImage(),
                  ),
                  if (hasDiscount && widget.product.activeOffer != null)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.redAccent,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          '-${widget.product.activeOffer!.discountPercent.toStringAsFixed(0)}%',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            // Info
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.product.name,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 4),

                  // Precios
                  if (hasDiscount) ...[
                    Text(
                      'Bs. ${widget.product.price.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.black45,
                        decoration: TextDecoration.lineThrough,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Bs. ${widget.product.displayPrice.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: Colors.redAccent,
                      ),
                    ),
                  ] else
                    Text(
                      'Bs. ${widget.product.displayPrice.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),

                  const SizedBox(height: 4),
                  Text(
                    'Stock: ${widget.product.stock}',
                    style: const TextStyle(fontSize: 11, color: Colors.black54),
                  ),
                  if (widget.product.brandName != null &&
                      widget.product.brandName!.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        widget.product.brandName!,
                        style: const TextStyle(
                          fontSize: 11,
                          color: Colors.black38,
                        ),
                      ),
                    ),
                  const SizedBox(height: 8),
                  Align(
                    alignment: Alignment.centerRight,
                    child: AnimatedScale(
                      scale: _scale,
                      duration: const Duration(milliseconds: 120),
                      curve: Curves.easeOut,
                      child: Container(
                        decoration: BoxDecoration(
                          color: primary.withOpacity(0.08),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: IconButton(
                          icon: Icon(Icons.add, color: primary),
                          onPressed: _handleAdd,
                          constraints: const BoxConstraints(
                            minWidth: 40,
                            minHeight: 40,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImage() {
    if (widget.product.imageUrl == null || widget.product.imageUrl!.isEmpty) {
      return Container(
        color: Colors.grey.shade100,
        child: const Center(
          child: Icon(
            Icons.inventory_2_outlined,
            size: 40,
            color: Colors.black26,
          ),
        ),
      );
    }

    return Image.network(
      widget.product.imageUrl!,
      fit: BoxFit.cover,
      errorBuilder: (_, __, ___) {
        return Container(
          color: Colors.grey.shade100,
          child: const Center(
            child: Icon(
              Icons.inventory_2_outlined,
              size: 40,
              color: Colors.black26,
            ),
          ),
        );
      },
    );
  }
}
