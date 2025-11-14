// lib/config/api_config.dart

class ApiConfig {
  /// URL del backend en PRODUCCIÓN (pasando por CloudFront)
  /// Incluye /api al final
  static const String _defaultBaseUrl =
      'https://d1098mxiq3rtlj.cloudfront.net/api';

  /// Permite sobreescribir por --dart-define si quisieras
  static String get _envBaseUrl => const String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: _defaultBaseUrl,
  );

  static String get baseUrl => _envBaseUrl;

  static String get api => baseUrl;
}
