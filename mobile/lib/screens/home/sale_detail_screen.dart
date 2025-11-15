// lib/screens/home/sale_detail_screen.dart

import 'package:flutter/material.dart';
import 'package:mobile/widgets/empty_state.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../models/sale.dart';
import '../../services/sales_service.dart';
import '../../config/api_config.dart';

class SaleDetailScreen extends StatefulWidget {
  final int saleId;
  const SaleDetailScreen({super.key, required this.saleId});

  @override
  State<SaleDetailScreen> createState() => _SaleDetailScreenState();
}

class _SaleDetailScreenState extends State<SaleDetailScreen> {
  bool _loading = true;
  String? _error;
  Sale? _sale;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      // CORRECCIÓN: Llamada a la nueva función del servicio
      final sale = await salesService.fetchSaleDetail(widget.saleId);
      if (!mounted) return;
      setState(() {
        _sale = sale;
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

  Future<void> _openPdf() async {
    if (_sale == null) return;
    final url = '${ApiConfig.api}/ventas/ventas/${_sale!.id}/comprobante/';
    final uri = Uri.parse(url);

    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No se pudo abrir el comprobante PDF')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null || _sale == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Detalle de Venta')),
        body: EmptyState(
          icon: Icons.error_outline,
          title: 'Error al cargar la venta',
          message: _error ?? 'No se pudo encontrar la venta especificada.',
          actionLabel: 'Reintentar',
          onAction: _load,
        ),
      );
    }

    final sale = _sale!;
    return Scaffold(
      appBar: AppBar(title: Text('Venta ${sale.folio}')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Folio: ${sale.folio}',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    if (sale.clienteNombre != null)
                      Text('Cliente: ${sale.clienteNombre}'),
                    const SizedBox(height: 4),
                    Text('Estado: ${sale.estado.toUpperCase()}'),
                    const SizedBox(height: 4),
                    Text('Fecha: ${sale.createdAt}'),
                    const Divider(height: 24),
                    const Text(
                      'Items de la venta',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...sale.items.map(
                      (it) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2.0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                it.productName,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Text('x${it.quantity}'),
                            SizedBox(
                              width: 20,
                              child: Text(
                                'Bs.',
                                textAlign: TextAlign.right,
                                style: TextStyle(color: Colors.grey.shade600),
                              ),
                            ),
                            SizedBox(
                              width: 70,
                              child: Text(
                                it.subtotal.toStringAsFixed(2),
                                textAlign: TextAlign.right,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const Divider(height: 24),
                    Align(
                      alignment: Alignment.centerRight,
                      child: Text(
                        'Total: Bs. ${sale.total.toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _openPdf,
              icon: const Icon(Icons.picture_as_pdf),
              label: const Text('Ver comprobante PDF'),
            ),
          ],
        ),
      ),
    );
  }
}
