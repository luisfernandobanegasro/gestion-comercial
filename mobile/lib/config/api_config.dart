// lib/config/api_config.dart

class ApiConfig {
  static const String api = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://d1098mxiq3rtlj.cloudfront.net/api',
  );
}
