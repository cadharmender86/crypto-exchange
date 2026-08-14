import '../config/api_config.dart';
import '../models/account.dart';
import '../models/wallet.dart';
import 'api_client.dart';

class AccountService {
  AccountService({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();

  final ApiClient _apiClient;

  Future<List<Account>> getAccounts() async {
    final response = await _apiClient.get(ApiConfig.accountsPath);
    final list = response is List ? response : <dynamic>[];
    return list.whereType<Map<String, dynamic>>().map(Account.fromJson).toList();
  }

  Future<List<Wallet>> getWallets() async {
    final response = await _apiClient.get(ApiConfig.walletsPath);
    final list = response is List ? response : <dynamic>[];
    return list.whereType<Map<String, dynamic>>().map(Wallet.fromJson).toList();
  }
}
