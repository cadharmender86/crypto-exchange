import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/deposit.dart';
import '../models/wallet.dart';
import '../models/wallet_address.dart';
import '../services/deposit_service.dart';

class DepositScreen extends StatefulWidget {
  const DepositScreen({required this.wallet, super.key});

  final Wallet wallet;

  @override
  State<DepositScreen> createState() => _DepositScreenState();
}

class _DepositScreenState extends State<DepositScreen> {
  final _service = DepositService();
  late Future<_DepositData> _dataFuture;

  @override
  void initState() {
    super.initState();
    _dataFuture = _load();
  }

  Future<_DepositData> _load() async {
    final results = await Future.wait<dynamic>([
      _service.getAddresses(widget.wallet.id),
      _service.getDeposits(),
    ]);
    return _DepositData(addresses: results[0] as List<WalletAddress>, deposits: results[1] as List<Deposit>);
  }

  Future<void> _refresh() async {
    setState(() => _dataFuture = _load());
    await _dataFuture;
  }

  Future<void> _copy(String value) async {
    await Clipboard.setData(ClipboardData(text: value));
    if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Deposit address copied')));
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Deposit')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: FutureBuilder<_DepositData>(
          future: _dataFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
            if (snapshot.hasError) {
              return ListView(padding: const EdgeInsets.all(24), children: [
                const Icon(Icons.error_outline, size: 48),
                const SizedBox(height: 12),
                const Text('Unable to load deposit information.', textAlign: TextAlign.center),
                const SizedBox(height: 12),
                FilledButton(onPressed: _refresh, child: const Text('Retry')),
              ]);
            }

            final data = snapshot.data!;
            return ListView(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              children: [
                Text('Deposit crypto', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 6),
                Text('Wallet: ${widget.wallet.walletType}', style: Theme.of(context).textTheme.bodyMedium),
                const SizedBox(height: 18),
                Card(
                  color: scheme.errorContainer,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.warning_amber_rounded, color: scheme.onErrorContainer),
                        const SizedBox(width: 12),
                        Expanded(child: Text('Only send the supported asset on the matching network. Sending an unsupported asset or network may result in permanent loss.', style: TextStyle(color: scheme.onErrorContainer))),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 22),
                Text('Deposit addresses', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
                const SizedBox(height: 10),
                if (data.addresses.isEmpty)
                  const Card(child: ListTile(leading: Icon(Icons.info_outline), title: Text('No deposit addresses available.')))
                else
                  ...data.addresses.map((address) => _AddressCard(address: address, onCopy: () => _copy(address.address))),
                const SizedBox(height: 24),
                Text('Deposit history', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
                const SizedBox(height: 10),
                if (data.deposits.isEmpty)
                  const Card(child: ListTile(leading: Icon(Icons.history), title: Text('No deposits yet.')))
                else
                  ...data.deposits.map((deposit) => Card(
                        child: ListTile(
                          leading: const CircleAvatar(child: Icon(Icons.south_west)),
                          title: Text('${deposit.amount} · ${deposit.network}', style: const TextStyle(fontWeight: FontWeight.w700)),
                          subtitle: Text('${deposit.status} · ${deposit.confirmations} confirmations\n${deposit.blockchainTxHash}', maxLines: 2, overflow: TextOverflow.ellipsis),
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

class _AddressCard extends StatelessWidget {
  const _AddressCard({required this.address, required this.onCopy});
  final WalletAddress address;
  final VoidCallback onCopy;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              const Icon(Icons.account_balance_wallet_outlined),
              const SizedBox(width: 8),
              Expanded(child: Text(address.network, style: const TextStyle(fontWeight: FontWeight.w700))),
              Chip(label: Text(address.addressType)),
            ]),
            const SizedBox(height: 12),
            SelectableText(address.address, style: const TextStyle(fontFamily: 'monospace', fontSize: 13)),
            const SizedBox(height: 10),
            SizedBox(width: double.infinity, child: OutlinedButton.icon(onPressed: onCopy, icon: const Icon(Icons.copy), label: const Text('Copy address'))),
          ],
        ),
      ),
    );
  }
}

class _DepositData {
  const _DepositData({required this.addresses, required this.deposits});
  final List<WalletAddress> addresses;
  final List<Deposit> deposits;
}
