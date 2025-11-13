// lib/screens/home/reports_screen.dart
import 'package:flutter/material.dart';

class ReportsScreen extends StatelessWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        'Aquí mostraremos el resumen de ventas, reportes rápidos\n(consumiendo el endpoint de IA del backend).',
        textAlign: TextAlign.center,
      ),
    );
  }
}
