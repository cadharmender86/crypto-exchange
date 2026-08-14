import '../config/api_config.dart';
import 'api_client.dart';
import 'token_storage.dart';

class AuthService {
  AuthService({ApiClient? apiClient, TokenStorage? tokenStorage})
      : _tokenStorage = tokenStorage ?? TokenStorage(),
        _apiClient = apiClient ?? ApiClient(tokenStorage: tokenStorage);

  final ApiClient _apiClient;
  final TokenStorage _tokenStorage;

  Future<void> login({required String email, required String password}) async {
    final response = await _apiClient.postForm(
      ApiConfig.loginPath,
      {'username': email, 'password': password},
    );
    await _saveAccessToken(response);
  }

  Future<void> register({required String email, required String password}) async {
    await _apiClient.postForm(
      ApiConfig.registerPath,
      {'email': email, 'password': password},
    );
  }

  Future<void> _saveAccessToken(Map<String, dynamic> response) async {
    final accessToken = response['access_token']?.toString();
    if (accessToken == null || accessToken.isEmpty) {
      throw ApiException(200, 'Authentication succeeded but no access token was returned.');
    }
    await _tokenStorage.saveTokens(
      accessToken: accessToken,
      refreshToken: response['refresh_token']?.toString(),
    );
  }

  Future<void> logout() => _tokenStorage.clear();
}
