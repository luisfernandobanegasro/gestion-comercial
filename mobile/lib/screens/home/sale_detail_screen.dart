// lib/screens/home/sale_detail_screen.dart

import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../models/sale.dart';
import '../../services/sales_service.dart';
import '../../config/api_config.dart'; // ApiConfig.api

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

    // Construye la URL del comprobante
    final url = '${ApiConfig.api}/ventas/ventas/${_sale!.id}/comprobante/';

    final uri = Uri.parse(url);

    final ok = await launchUrl(uri, mode: LaunchMode.externalApplication);

    if (!ok) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudo abrir el comprobante PDF')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_error != null || _sale == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Detalle de venta')),
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline),
              const SizedBox(height: 8),
              Text(_error ?? 'No se pudo cargar la venta'),
              TextButton(onPressed: _load, child: const Text('Reintentar')),
            ],
          ),
        ),
      );
    }

    final sale = _sale!;

    return Scaffold(
      appBar: AppBar(title: Text('Venta ${sale.folio}')),
      body: Padding(
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
                      (it) => Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(child: Text(it.productName)),
                          Text('x${it.quantity}'),
                          const SizedBox(width: 8),
                          Text('Bs. ${it.subtotal.toStringAsFixed(2)}'),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
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
