// lib/config/api_config.dart

import 'package:flutter/foundation.dart';

/// Configuración centralizada de la API.
/// Solo cambia [productionBaseUrl] cuando generes el APK.
class ApiConfig {
  /// 🔵 URL del backend en PRODUCCIÓN
  /// Ejemplo:
  ///   https://smart-sales-365.com/api
  ///   https://api.miapp.com
  static const String productionBaseUrl =
      'https://MISERVIDOR.PRODUCCION.com/api'; // <-- CAMBIA SOLO ESTO

  /// 🔵 URL del backend en LOCAL (desarrollo)
  static const String localWebUrl = 'http://localhost:8000/api';
  static const String localEmulatorUrl = 'http://10.0.2.2:8000/api';

  /// 🔵 Obtiene automáticamente la URL correcta según plataforma.
  static String get baseUrl {
    if (kIsWeb) {
      // Flutter Web
      return localWebUrl;
    } else {
      // Android (emulador o dispositivo real)
      return localEmulatorUrl;
    }
  }

  /// 🔵 Usar esta para llamar en ambiente de PRODUCCIÓN al generar el APK.
  /// Ejemplo de uso:
  /// const apiUrl = ApiConfig.api;
  static String get api => kReleaseMode ? productionBaseUrl : baseUrl;
}
