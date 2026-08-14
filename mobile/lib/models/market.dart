class Market {
  const Market({required this.symbol, required this.baseAsset, required this.quoteAsset, required this.price, required this.change24h, required this.volume24h});

  final String symbol;
  final String baseAsset;
  final String quoteAsset;
  final double price;
  final double change24h;
  final double volume24h;

  factory Market.fromJson(Map<String, dynamic> json) => Market(
        symbol: json['symbol']?.toString() ?? '',
        baseAsset: json['base_asset']?.toString() ?? '',
        quoteAsset: json['quote_asset']?.toString() ?? '',
        price: double.tryParse(json['price']?.toString() ?? '') ?? 0,
        change24h: double.tryParse(json['change_24h']?.toString() ?? '') ?? 0,
        volume24h: double.tryParse(json['volume_24h']?.toString() ?? '') ?? 0,
      );
}
