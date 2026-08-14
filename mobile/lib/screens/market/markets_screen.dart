import 'package:flutter/material.dart';

import '../../models/market.dart';
import 'market_detail_screen.dart';

class MarketsScreen extends StatefulWidget {
  const MarketsScreen({super.key});

  @override
  State<MarketsScreen> createState() => _MarketsScreenState();
}

class _MarketsScreenState extends State<MarketsScreen> {
  final _searchController = TextEditingController();
  final _markets = const <Market>[
    Market(symbol: 'BTC/USDT', baseAsset: 'BTC', quoteAsset: 'USDT', price: 0, change24h: 0, volume24h: 0),
    Market(symbol: 'ETH/USDT', baseAsset: 'ETH', quoteAsset: 'USDT', price: 0, change24h: 0, volume24h: 0),
    Market(symbol: 'SOL/USDT', baseAsset: 'SOL', quoteAsset: 'USDT', price: 0, change24h: 0, volume24h: 0),
    Market(symbol: 'BTC/INR', baseAsset: 'BTC', quoteAsset: 'INR', price: 0, change24h: 0, volume24h: 0),
  ];
  String _query = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final markets = _markets.where((market) => market.symbol.toLowerCase().contains(_query.toLowerCase())).toList();
    return Scaffold(
      appBar: AppBar(title: const Text('Markets')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
        children: [
          Text('Markets', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
          const SizedBox(height: 6),
          const Text('Track trading pairs and open a market when live pricing is connected.'),
          const SizedBox(height: 18),
          TextField(
            controller: _searchController,
            onChanged: (value) => setState(() => _query = value),
            decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Search markets'),
          ),
          const SizedBox(height: 18),
          Row(children: [
            ChoiceChip(label: const Text('All'), selected: true, onSelected: (_) {}),
            const SizedBox(width: 8),
            ChoiceChip(label: const Text('USDT'), selected: false, onSelected: (_) {}),
            const SizedBox(width: 8),
            ChoiceChip(label: const Text('INR'), selected: false, onSelected: (_) {}),
          ]),
          const SizedBox(height: 18),
          if (markets.isEmpty)
            const Card(child: ListTile(title: Text('No markets found')))
          else
            ...markets.map((market) => Card(
                  margin: const EdgeInsets.only(bottom: 10),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    leading: CircleAvatar(child: Text(market.baseAsset.substring(0, 1))),
                    title: Text(market.symbol, style: const TextStyle(fontWeight: FontWeight.w700)),
                    subtitle: Text(market.price == 0 ? 'Live price pending' : market.price.toStringAsFixed(4)),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(market.change24h == 0 ? '--' : '${market.change24h.toStringAsFixed(2)}%'),
                        const SizedBox(height: 4),
                        const Icon(Icons.chevron_right, size: 18),
                      ],
                    ),
                    onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => MarketDetailScreen(market: market))),
                  ),
                )),
        ],
      ),
    );
  }
}
