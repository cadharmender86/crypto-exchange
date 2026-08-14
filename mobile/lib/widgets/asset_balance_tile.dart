import 'package:flutter/material.dart';

class AssetBalanceTile extends StatelessWidget {
  const AssetBalanceTile({
    required this.symbol,
    required this.name,
    required this.available,
    required this.locked,
    required this.total,
    super.key,
  });

  final String symbol;
  final String name;
  final double available;
  final double locked;
  final double total;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            CircleAvatar(child: Text(symbol.isEmpty ? '?' : symbol.substring(0, 1))),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(symbol, style: const TextStyle(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 3),
                  Text(name, style: Theme.of(context).textTheme.bodySmall),
                  const SizedBox(height: 6),
                  Text('${available.toStringAsFixed(8)} available'),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(total.toStringAsFixed(8), style: const TextStyle(fontWeight: FontWeight.w700)),
                const SizedBox(height: 4),
                Text('${locked.toStringAsFixed(8)} locked', style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
