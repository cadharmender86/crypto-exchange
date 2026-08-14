class WalletAddress {
  const WalletAddress({
    required this.id,
    required this.walletId,
    required this.assetId,
    required this.network,
    required this.address,
    required this.addressType,
    required this.status,
  });

  final String id;
  final String walletId;
  final String assetId;
  final String network;
  final String address;
  final String addressType;
  final String status;

  factory WalletAddress.fromJson(Map<String, dynamic> json) => WalletAddress(
        id: json['id'].toString(),
        walletId: json['wallet_id'].toString(),
        assetId: json['asset_id'].toString(),
        network: json['network']?.toString() ?? '',
        address: json['address']?.toString() ?? '',
        addressType: json['address_type']?.toString() ?? '',
        status: json['status']?.toString() ?? '',
      );
}
