// lib/services/api_client.dart

import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../config/api_config.dart';

class ApiClient {
  final http.Client _client = http.Client();

  /// Construye la URL absoluta a partir de la base de la API + path
  Uri _uri(String path, [Map<String, dynamic>? query]) {
    return Uri.parse('${ApiConfig.baseUrl}$path').replace(
      queryParameters: query?.map(
        (key, value) => MapEntry(key, value.toString()),
      ),
    );
  }

  /// Headers comunes: JSON + Authorization si hay access_token
  Future<Map<String, String>> _headers() async {
    final prefs = await SharedPreferences.getInstance();
    final accessToken = prefs.getString('access_token'); // ← OJO AQUÍ

    return {
      'Content-Type': 'application/json',
      if (accessToken != null && accessToken.isNotEmpty)
        'Authorization': 'Bearer $accessToken',
    };
  }

  /// Procesa la respuesta: si es 2xx decodifica JSON, si no lanza Exception
  dynamic _process(http.Response res) {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      if (res.body.isEmpty) return null;
      return jsonDecode(utf8.decode(res.bodyBytes));
    }

    // Mensaje de error resumido
    throw Exception('Error API ${res.statusCode}: ${res.body}');
  }

  /// GET simple (con query opcional)
  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async {
    final res = await _client.get(_uri(path, query), headers: await _headers());
    return _process(res);
  }

  /// POST con body opcional (codificado en JSON)
  Future<dynamic> post(String path, {dynamic body}) async {
    final res = await _client.post(
      _uri(path),
      headers: await _headers(),
      body: body != null ? jsonEncode(body) : null,
    );
    return _process(res);
  }

  /// PUT
  Future<dynamic> put(String path, {dynamic body}) async {
    final res = await _client.put(
      _uri(path),
      headers: await _headers(),
      body: body != null ? jsonEncode(body) : null,
    );
    return _process(res);
  }

  /// DELETE
  Future<dynamic> delete(String path) async {
    final res = await _client.delete(_uri(path), headers: await _headers());
    return _process(res);
  }
}

/// Instancia global
final apiClient = ApiClient();
