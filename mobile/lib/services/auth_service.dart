import '../config/api_config.dart';
import 'api_client.dart';
import 'token_storage.dart';

class AuthService {
  AuthService({ApiClient? apiClient, TokenStorage? tokenStorage})
      : _apiClient = apiClient ?? ApiClient(tokenStorage: tokenStorage),
        _tokenStorage = tokenStorage ?? TokenStorage();

  final ApiClient _apiClient;
  final TokenStorage _tokenStorage;

  Future<void> login({required String email, required String password}) async {
    final response = await _apiClient.postForm(
      ApiConfig.loginPath,
      {
        'username': email,
        'password': password,
      },
    );

    final accessToken = response['access_token']?.toString();
    if (accessToken == null || accessToken.isEmpty) {
      throw ApiException(200, 'Login succeeded but no access token was returned.');
    }

    await _tokenStorage.saveTokens(
      accessToken: accessToken,
      refreshToken: response['refresh_token']?.toString(),
    );
  }

  Future<void> logout() => _tokenStorage.clear();
}
