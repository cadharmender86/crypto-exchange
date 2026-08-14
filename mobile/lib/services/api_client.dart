import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import 'token_storage.dart';

class ApiException implements Exception {
  ApiException(this.statusCode, this.message);

  final int statusCode;
  final String message;

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiClient {
  ApiClient({http.Client? client, TokenStorage? tokenStorage})
      : _client = client ?? http.Client(),
        _tokenStorage = tokenStorage ?? TokenStorage();

  final http.Client _client;
  final TokenStorage _tokenStorage;

  Future<Map<String, dynamic>> postForm(
    String path,
    Map<String, String> fields, {
    bool authenticated = false,
  }) async {
    final headers = <String, String>{
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
    };
    if (authenticated) {
      final token = await _tokenStorage.accessToken();
      if (token != null) headers['Authorization'] = 'Bearer $token';
    }

    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}$path'),
      headers: headers,
      body: fields,
    );
    return _decode(response);
  }

  Future<dynamic> get(String path, {bool authenticated = true}) async {
    final headers = <String, String>{'Accept': 'application/json'};
    if (authenticated) {
      final token = await _tokenStorage.accessToken();
      if (token != null) headers['Authorization'] = 'Bearer $token';
    }

    final response = await _client.get(
      Uri.parse('${ApiConfig.baseUrl}$path'),
      headers: headers,
    );
    return _decodeAny(response);
  }

  dynamic _decodeAny(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      String message = response.body;
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map<String, dynamic>) {
          message = decoded['detail']?.toString() ?? decoded['message']?.toString() ?? message;
        }
      } catch (_) {}
      throw ApiException(response.statusCode, message);
    }
    if (response.body.isEmpty) return null;
    return jsonDecode(response.body);
  }

  Map<String, dynamic> _decode(http.Response response) {
    final value = _decodeAny(response);
    if (value is Map<String, dynamic>) return value;
    throw ApiException(response.statusCode, 'Unexpected API response');
  }
}
