class Account {
  const Account({
    required this.id,
    required this.assetId,
    required this.accountType,
    required this.availableBalance,
    required this.lockedBalance,
    required this.totalBalance,
    required this.status,
  });

  final String id;
  final String assetId;
  final String accountType;
  final double availableBalance;
  final double lockedBalance;
  final double totalBalance;
  final String status;

  factory Account.fromJson(Map<String, dynamic> json) => Account(
        id: json['id'].toString(),
        assetId: json['asset_id'].toString(),
        accountType: json['account_type']?.toString() ?? '',
        availableBalance: _number(json['available_balance']),
        lockedBalance: _number(json['locked_balance']),
        totalBalance: _number(json['total_balance']),
        status: json['status']?.toString() ?? '',
      );

  static double _number(dynamic value) => double.tryParse(value?.toString() ?? '') ?? 0;
}
