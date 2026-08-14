class Deposit {
  const Deposit({
    required this.id,
    required this.walletAddressId,
    required this.assetId,
    required this.network,
    required this.blockchainTxHash,
    required this.amount,
    required this.confirmations,
    required this.status,
  });

  final String id;
  final String walletAddressId;
  final String assetId;
  final String network;
  final String blockchainTxHash;
  final double amount;
  final int confirmations;
  final String status;

  factory Deposit.fromJson(Map<String, dynamic> json) => Deposit(
        id: json['id'].toString(),
        walletAddressId: json['wallet_address_id'].toString(),
        assetId: json['asset_id'].toString(),
        network: json['network']?.toString() ?? '',
        blockchainTxHash: json['blockchain_tx_hash']?.toString() ?? '',
        amount: double.tryParse(json['amount']?.toString() ?? '') ?? 0,
        confirmations: int.tryParse(json['confirmations']?.toString() ?? '') ?? 0,
        status: json['status']?.toString() ?? '',
      );
}
