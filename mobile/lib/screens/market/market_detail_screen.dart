import 'package:flutter/material.dart';

import '../../models/market.dart';

class MarketDetailScreen extends StatelessWidget {
  const MarketDetailScreen({required this.market, super.key});

  final Market market;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(market.symbol)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(market.symbol, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 8),
                Text(market.price == 0 ? 'Live price pending' : market.price.toStringAsFixed(8), style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 4),
                Text(market.change24h == 0 ? '24h change --' : '24h ${market.change24h.toStringAsFixed(2)}%'),
              ]),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: SizedBox(
              height: 260,
              child: Center(child: Text('Price chart\nWill be connected to market data', textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyLarge)),
            ),
          ),
          const SizedBox(height: 16),
          Row(children: [
            Expanded(child: FilledButton.icon(onPressed: null, icon: const Icon(Icons.add), label: const Text('Buy'))),
            const SizedBox(width: 12),
            Expanded(child: OutlinedButton.icon(onPressed: null, icon: const Icon(Icons.remove), label: const Text('Sell'))),
          ]),
          const SizedBox(height: 20),
          Text('Market statistics', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
          const SizedBox(height: 10),
          Card(child: Column(children: [
            ListTile(title: const Text('24h Change'), trailing: Text(market.change24h == 0 ? '--' : '${market.change24h}%')),
            const Divider(height: 1),
            ListTile(title: const Text('24h Volume'), trailing: Text(market.volume24h == 0 ? '--' : market.volume24h.toStringAsFixed(2))),
          ])),
        ],
      ),
    );
  }
}
