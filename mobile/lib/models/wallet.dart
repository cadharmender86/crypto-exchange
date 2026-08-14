class Wallet {
  const Wallet({required this.id, required this.walletType, required this.status});

  final String id;
  final String walletType;
  final String status;

  factory Wallet.fromJson(Map<String, dynamic> json) => Wallet(
        id: json['id'].toString(),
        walletType: json['wallet_type']?.toString() ?? '',
        status: json['status']?.toString() ?? '',
      );
}
