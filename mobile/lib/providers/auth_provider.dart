import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../services/api_client.dart';

class AuthProvider extends ChangeNotifier {
  User? user;
  bool _loading = false;
  bool get loading => _loading;
  bool get isLoggedIn => user != null;

  Future<void> login(String username, String password) async {
    _loading = true;
    notifyListeners();
    try {
      final data = await apiClient.post(
        '/cuentas/token/', // Ruta corregida para el login.
        body: {'username': username, 'password': password},
      );

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', data['access']);
      await prefs.setString('refresh_token', data['refresh']);

      user = User(username: username, role: data['role'] ?? 'Vendedor');
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    user = null;
    notifyListeners();
  }

  Future<void> restoreSession() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    if (token != null) {
      // Podrías llamar a /auth/me/ para traer datos reales
      user = User(username: 'usuario', role: 'Vendedor');
      notifyListeners();
    }
  }
}
