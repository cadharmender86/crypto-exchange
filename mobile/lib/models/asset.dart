class Asset {
  const Asset({required this.id, required this.symbol, required this.name});

  final String id;
  final String symbol;
  final String name;

  factory Asset.fromJson(Map<String, dynamic> json) => Asset(
        id: json['id'].toString(),
        symbol: json['symbol']?.toString() ?? '',
        name: json['name']?.toString() ?? '',
      );
}
