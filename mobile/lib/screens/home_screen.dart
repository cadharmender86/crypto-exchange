import 'package:flutter/material.dart';

import '../config/api_config.dart';
import '../models/account.dart';
import '../models/asset.dart';
import '../models/wallet.dart';
import '../services/account_service.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({required this.onLogout, super.key});

  final VoidCallback onLogout;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _apiClient = ApiClient();
  final _accountService = AccountService();
  final _authService = AuthService();
  late Future<_DashboardData> _dashboardFuture;

  @override
  void initState() {
    super.initState();
    _dashboardFuture = _loadDashboard();
  }

  Future<_DashboardData> _loadDashboard() async {
    final results = await Future.wait<dynamic>([
      _accountService.getAccounts(),
      _accountService.getWallets(),
      _apiClient.get(ApiConfig.assetsPath),
    ]);

    final rawAssets = results[2] is List ? results[2] as List : <dynamic>[];
    final assets = rawAssets
        .whereType<Map<String, dynamic>>()
        .map(Asset.fromJson)
        .toList();

    return _DashboardData(
      accounts: results[0] as List<Account>,
      wallets: results[1] as List<Wallet>,
      assets: assets,
    );
  }

  Future<void> _logout() async {
    await _authService.logout();
    if (mounted) widget.onLogout();
  }

  Future<void> _refresh() async {
    setState(() => _dashboardFuture = _loadDashboard());
    await _dashboardFuture;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('BitNova'),
        actions: [IconButton(onPressed: _logout, icon: const Icon(Icons.logout))],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: FutureBuilder<_DashboardData>(
          future: _dashboardFuture,
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
                  const Text('Unable to load your account data.', textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(onPressed: _refresh, child: const Text('Retry')),
                ],
              );
            }

            final data = snapshot.data!;
            final total = data.accounts.fold<double>(0, (sum, account) => sum + account.totalBalance);

            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Total Assets', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 8),
                        Text(total.toStringAsFixed(8), style: Theme.of(context).textTheme.headlineMedium),
                        const SizedBox(height: 4),
                        Text('${data.accounts.length} account(s) · ${data.wallets.length} wallet(s)'),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                Text('Balances', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                if (data.accounts.isEmpty)
                  const Card(child: ListTile(title: Text('No account balances yet')))
                else
                  ...data.accounts.map((account) {
                    final asset = data.assets.cast<Asset?>().firstWhere(
                          (item) => item?.id == account.assetId,
                          orElse: () => null,
                        );
                    final symbol = asset?.symbol ?? account.assetId;
                    return Card(
                      child: ListTile(
                        leading: const CircleAvatar(child: Icon(Icons.account_balance_wallet_outlined)),
                        title: Text(symbol),
                        subtitle: Text('${account.availableBalance.toStringAsFixed(8)} available · ${account.lockedBalance.toStringAsFixed(8)} locked'),
                        trailing: Text(account.totalBalance.toStringAsFixed(8)),
                      ),
                    );
                  }),
                const SizedBox(height: 20),
                Text('Wallets', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                if (data.wallets.isEmpty)
                  const Card(child: ListTile(title: Text('No wallets available')))
                else
                  ...data.wallets.map((wallet) => Card(
                        child: ListTile(
                          leading: const CircleAvatar(child: Icon(Icons.wallet)),
                          title: Text(wallet.walletType),
                          subtitle: Text(wallet.status),
                        ),
                      )),
                const SizedBox(height: 20),
                Text('Markets', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                if (data.assets.isEmpty)
                  const Card(child: ListTile(title: Text('No assets available')))
                else
                  ...data.assets.take(10).map((asset) => Card(
                        child: ListTile(
                          leading: const CircleAvatar(child: Icon(Icons.currency_exchange)),
                          title: Text(asset.symbol),
                          subtitle: Text(asset.name),
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

class _DashboardData {
  const _DashboardData({required this.accounts, required this.wallets, required this.assets});

  final List<Account> accounts;
  final List<Wallet> wallets;
  final List<Asset> assets;
}
