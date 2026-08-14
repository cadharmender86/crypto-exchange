import 'package:flutter/material.dart';

class MarketsScreen extends StatelessWidget {
  const MarketsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Markets')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          _MarketTile(symbol: 'BTC/USDT', name: 'Bitcoin', price: '--', change: '--'),
          SizedBox(height: 10),
          _MarketTile(symbol: 'ETH/USDT', name: 'Ethereum', price: '--', change: '--'),
          SizedBox(height: 10),
          _MarketTile(symbol: 'USDT/INR', name: 'Tether', price: '--', change: '--'),
          SizedBox(height: 24),
          Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('Live market prices and charts will be connected to the market/WebSocket APIs in the next phase.'),
            ),
          ),
        ],
      ),
    );
  }
}

class _MarketTile extends StatelessWidget {
  const _MarketTile({required this.symbol, required this.name, required this.price, required this.change});

  final String symbol;
  final String name;
  final String price;
  final String change;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: const CircleAvatar(child: Icon(Icons.currency_bitcoin)),
        title: Text(symbol, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(name),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [Text(price), Text(change)],
        ),
      ),
    );
  }
}
