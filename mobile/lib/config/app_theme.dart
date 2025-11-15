// lib/config/app_theme.dart

import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData get light {
    // 🎨 Colores de marca
    const primary = Color(0xFF2563EB); // Azul (puedes cambiarlo)
    const background = Color(0xFFF5F5F7); // Fondo claro gris

    final baseColorScheme = ColorScheme.fromSeed(
      seedColor: primary,
      brightness: Brightness.light,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: baseColorScheme.copyWith(
        primary: primary,
        secondary: primary,
      ),
      scaffoldBackgroundColor: background,

      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        iconTheme: IconThemeData(color: Colors.black87),
        titleTextStyle: TextStyle(
          color: Colors.black87,
          fontWeight: FontWeight.w600,
          fontSize: 18,
        ),
      ),

      cardTheme: CardTheme(
        elevation: 2,
        color: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),

      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primary, width: 1.4),
        ),
      ),

      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        type: BottomNavigationBarType.fixed,
        selectedItemColor: primary,
        unselectedItemColor: Colors.black45,
        showUnselectedLabels: true,
      ),

      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: primary,
        foregroundColor: Colors.white,
      ),
    );
  }
}
