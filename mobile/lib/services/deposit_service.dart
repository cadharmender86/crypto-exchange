import '../config/api_config.dart';
import '../models/deposit.dart';
import '../models/wallet_address.dart';
import 'api_client.dart';

class DepositService {
  DepositService({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();

  final ApiClient _apiClient;

  Future<List<WalletAddress>> getAddresses(String walletId) async {
    final response = await _apiClient.get('/wallets/$walletId/addresses');
    final list = response is List ? response : <dynamic>[];
    return list.whereType<Map<String, dynamic>>().map(WalletAddress.fromJson).toList();
  }

  Future<List<Deposit>> getDeposits() async {
    final response = await _apiClient.get(ApiConfig.depositsPath);
    final list = response is List ? response : <dynamic>[];
    return list.whereType<Map<String, dynamic>>().map(Deposit.fromJson).toList();
  }

  Future<Deposit> createDeposit({
    required String walletAddressId,
    required String assetId,
    required String network,
    required String blockchainTxHash,
    required String amount,
  }) async {
    final response = await _apiClient.postJson(ApiConfig.depositsPath, {
      'wallet_address_id': walletAddressId,
      'asset_id': assetId,
      'network': network,
      'blockchain_tx_hash': blockchainTxHash,
      'amount': amount,
    });
    return Deposit.fromJson(response);
  }
}
