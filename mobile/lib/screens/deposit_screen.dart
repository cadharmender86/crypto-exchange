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
    return _DepositData(
      addresses: results[0] as List<WalletAddress>,
      deposits: results[1] as List<Deposit>,
    );
  }

  Future<void> _refresh() async {
    setState(() => _dataFuture = _load());
    await _dataFuture;
  }

  Future<void> _copy(String value) async {
    await Clipboard.setData(ClipboardData(text: value));
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Deposit address copied')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Deposit')),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: FutureBuilder<_DepositData>(
          future: _dataFuture,
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
                  const Text('Unable to load deposit information.', textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(onPressed: _refresh, child: const Text('Retry')),
                ],
              );
            }

            final data = snapshot.data!;
            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text('Deposit to ${widget.wallet.walletType}', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                const Card(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                      'Send only the selected asset on the matching network to an address shown below. Sending an unsupported asset or network may result in permanent loss.',
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text('Deposit Addresses', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                if (data.addresses.isEmpty)
                  const Card(child: ListTile(title: Text('No deposit addresses available.')))
                else
                  ...data.addresses.map((address) => Card(
                        child: ListTile(
                          title: Text('${address.network} · ${address.addressType}'),
                          subtitle: SelectableText(address.address),
                          trailing: IconButton(
                            tooltip: 'Copy address',
                            onPressed: () => _copy(address.address),
                            icon: const Icon(Icons.copy),
                          ),
                        ),
                      )),
                const SizedBox(height: 20),
                Text('Deposit History', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                if (data.deposits.isEmpty)
                  const Card(child: ListTile(title: Text('No deposits yet.')))
                else
                  ...data.deposits.map((deposit) => Card(
                        child: ListTile(
                          leading: const CircleAvatar(child: Icon(Icons.south_west)),
                          title: Text('${deposit.amount} · ${deposit.network}'),
                          subtitle: Text('${deposit.status} · ${deposit.confirmations} confirmations\n${deposit.blockchainTxHash}'),
                          isThreeLine: true,
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

class _DepositData {
  const _DepositData({required this.addresses, required this.deposits});

  final List<WalletAddress> addresses;
  final List<Deposit> deposits;
}
