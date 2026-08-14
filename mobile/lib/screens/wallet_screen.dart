import 'package:flutter/material.dart';

import '../models/wallet.dart';
import '../services/account_service.dart';

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
    return Scaffold(
      appBar: AppBar(title: const Text('Wallets')),
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
                  const Text('Unable to load wallets.', textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(onPressed: _refresh, child: const Text('Retry')),
                ],
              );
            }

            final wallets = snapshot.data ?? const <Wallet>[];
            if (wallets.isEmpty) {
              return ListView(
                padding: const EdgeInsets.all(24),
                children: const [
                  Icon(Icons.account_balance_wallet_outlined, size: 56),
                  SizedBox(height: 12),
                  Text('No wallets found.', textAlign: TextAlign.center),
                ],
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: wallets.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                final wallet = wallets[index];
                return Card(
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    leading: const CircleAvatar(child: Icon(Icons.wallet)),
                    title: Text(wallet.walletType),
                    subtitle: Text('Wallet ID: ${wallet.id}\nStatus: ${wallet.status}'),
                    isThreeLine: true,
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
