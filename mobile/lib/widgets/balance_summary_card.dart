import 'package:flutter/material.dart';

class BalanceSummaryCard extends StatelessWidget {
  const BalanceSummaryCard({required this.totalBalance, required this.assetCount, super.key});

  final double totalBalance;
  final int assetCount;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      color: scheme.primary,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.account_balance_wallet_outlined, color: scheme.onPrimary),
                const Spacer(),
                Icon(Icons.more_horiz, color: scheme.onPrimary),
              ],
            ),
            const SizedBox(height: 22),
            Text('Total portfolio', style: TextStyle(color: scheme.onPrimary.withValues(alpha: .78))),
            const SizedBox(height: 6),
            Text(
              totalBalance.toStringAsFixed(8),
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    color: scheme.onPrimary,
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 6),
            Text(
              '$assetCount asset account(s)',
              style: TextStyle(color: scheme.onPrimary.withValues(alpha: .78)),
            ),
          ],
        ),
      ),
    );
  }
}
