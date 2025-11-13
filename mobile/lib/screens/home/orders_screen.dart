// lib/screens/home/orders_screen.dart

import 'package:flutter/material.dart';
import '../../models/sale.dart';
import '../../services/sales_service.dart';
import 'sale_detail_screen.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  bool _loading = true;
  String? _error;
  List<Sale> _sales = [];

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
      final list = await salesService.fetchMySales();
      if (!mounted) return;
      setState(() {
        _sales = list;
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

  Color _statusColor(String estado) {
    switch (estado) {
      case 'pagada':
        return Colors.green;
      case 'pendiente':
        return Colors.orange;
      case 'anulada':
      case 'reembolsada':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline),
            const SizedBox(height: 8),
            Text(_error!),
            TextButton(onPressed: _load, child: const Text('Reintentar')),
          ],
        ),
      );
    }

    if (_sales.isEmpty) {
      return const Center(
        child: Text('Todavía no tienes compras registradas.'),
      );
    }

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _sales.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final sale = _sales[index];
          return ListTile(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: Colors.grey.shade300),
            ),
            title: Text('Folio: ${sale.folio}'),
            subtitle: Text(
              'Fecha: ${sale.createdAt}\nTotal: Bs. ${sale.total.toStringAsFixed(2)}',
            ),
            isThreeLine: true,
            trailing: Chip(
              label: Text(sale.estado.toUpperCase()),
              backgroundColor: _statusColor(sale.estado).withOpacity(0.1),
              labelStyle: TextStyle(
                color: _statusColor(sale.estado),
                fontWeight: FontWeight.bold,
              ),
            ),
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => SaleDetailScreen(saleId: sale.id),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
