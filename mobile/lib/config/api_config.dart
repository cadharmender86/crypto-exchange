class ApiConfig {
  const ApiConfig._();

  // Android emulator reaches the host machine through 10.0.2.2.
  // Override with: flutter run --dart-define=API_BASE_URL=https://your-api.example.com/api/v1
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  static const String loginPath = '/auth/login';
  static const String registerPath = '/auth/register';
  static const String assetsPath = '/assets';
  static const String accountsPath = '/accounts';
  static const String walletsPath = '/wallets';
  static const String depositsPath = '/deposits';
}
