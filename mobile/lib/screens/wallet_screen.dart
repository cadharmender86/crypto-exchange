import 'package:flutter/material.dart';

import '../models/wallet.dart';
import '../services/account_service.dart';
import 'deposit_screen.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  final _service = AccountService();
  late Future<List<Wallet>> _walletsFuture;

  @override
  void initState() {
    super.initState();
    _walletsFuture = _service.getWallets();
  }

  Future<void> _refresh() async {
    setState(() => _walletsFuture = _service.getWallets());
    await _walletsFuture;
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Wallet')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: FutureBuilder<List<Wallet>>(
          future: _walletsFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  const Icon(Icons.error_outline, size: 48),
                  const SizedBox(height: 12),
                  const Text('Unable to load your wallets.', textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(onPressed: _refresh, child: const Text('Retry')),
                ],
              );
            }

            final wallets = snapshot.data ?? const <Wallet>[];
            return ListView(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              children: [
                Text('Your wallets', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 6),
                Text('Manage your digital-asset wallets and deposit addresses.', style: Theme.of(context).textTheme.bodyMedium),
                const SizedBox(height: 20),
                if (wallets.isEmpty)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(28),
                      child: Column(
                        children: [
                          CircleAvatar(radius: 30, child: Icon(Icons.account_balance_wallet_outlined, color: scheme.primary, size: 30)),
                          const SizedBox(height: 14),
                          const Text('No wallets found', style: TextStyle(fontWeight: FontWeight.w700)),
                          const SizedBox(height: 6),
                          const Text('Your wallet will appear here when it is available.', textAlign: TextAlign.center),
                        ],
                      ),
                    ),
                  )
                else
                  ...wallets.map((wallet) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    CircleAvatar(child: Icon(Icons.account_balance_wallet, color: scheme.primary)),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(wallet.walletType, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                                          const SizedBox(height: 4),
                                          Text('ID: ${wallet.id}', maxLines: 1, overflow: TextOverflow.ellipsis, style: Theme.of(context).textTheme.bodySmall),
                                        ],
                                      ),
                                    ),
                                    Chip(label: Text(wallet.status)),
                                  ],
                                ),
                                const SizedBox(height: 16),
                                SizedBox(
                                  width: double.infinity,
                                  child: OutlinedButton.icon(
                                    onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => DepositScreen(wallet: wallet))),
                                    icon: const Icon(Icons.south_west),
                                    label: const Text('Deposit'),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      )),
              ],
            );
          },
        ),
      ),
    );
  }
}
