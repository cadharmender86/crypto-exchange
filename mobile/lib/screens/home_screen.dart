import 'package:flutter/material.dart';

import '../config/api_config.dart';
import '../models/account.dart';
import '../models/asset.dart';
import '../models/wallet.dart';
import '../services/account_service.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../widgets/asset_balance_tile.dart';
import '../widgets/balance_summary_card.dart';
import '../widgets/quick_action_card.dart';
import '../widgets/section_header.dart';
import 'wallet_screen.dart';

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
    final assets = rawAssets.whereType<Map<String, dynamic>>().map(Asset.fromJson).toList();

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

  void _openWallets() {
    Navigator.of(context).push(MaterialPageRoute(builder: (_) => const WalletScreen()));
  }

  void _showComingSoon(String feature) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$feature will be connected when its backend API is ready.')));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        titleSpacing: 20,
        title: Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Icon(Icons.currency_bitcoin, color: Theme.of(context).colorScheme.primary),
            ),
            const SizedBox(width: 10),
            const Text('BitNova', style: TextStyle(fontWeight: FontWeight.w800)),
          ],
        ),
        actions: [
          IconButton(onPressed: () => _showComingSoon('Notifications'), icon: const Icon(Icons.notifications_none_rounded)),
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout_rounded)),
          const SizedBox(width: 8),
        ],
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
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(24),
                children: [
                  const SizedBox(height: 80),
                  const Icon(Icons.cloud_off_rounded, size: 56),
                  const SizedBox(height: 16),
                  Text('Unable to load your account data.', textAlign: TextAlign.center, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  const Text('Check the backend connection and try again.', textAlign: TextAlign.center),
                  const SizedBox(height: 20),
                  FilledButton.icon(onPressed: _refresh, icon: const Icon(Icons.refresh), label: const Text('Retry')),
                ],
              );
            }

            final data = snapshot.data!;
            final total = data.accounts.fold<double>(0, (sum, account) => sum + account.totalBalance);

            return ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
              children: [
                Text('Welcome back', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 4),
                Text('Manage your crypto portfolio', style: Theme.of(context).textTheme.bodyMedium),
                const SizedBox(height: 16),
                BalanceSummaryCard(totalBalance: total, assetCount: data.accounts.length),
                const SizedBox(height: 16),
                Row(
                  children: [
                    QuickActionCard(icon: Icons.south_west_rounded, label: 'Deposit', onTap: _openWallets),
                    const SizedBox(width: 12),
                    QuickActionCard(icon: Icons.north_east_rounded, label: 'Withdraw', onTap: () => _showComingSoon('Withdrawals')),
                    const SizedBox(width: 12),
                    QuickActionCard(icon: Icons.swap_horiz_rounded, label: 'Trade', onTap: () => _showComingSoon('Trading')),
                  ],
                ),
                const SizedBox(height: 24),
                SectionHeader(title: 'Your assets', actionLabel: 'View all', onAction: _openWallets),
                const SizedBox(height: 10),
                if (data.accounts.isEmpty)
                  const Card(child: Padding(padding: EdgeInsets.all(20), child: Text('No account balances yet.')))
                else
                  ...data.accounts.take(5).map((account) {
                    final asset = data.assets.cast<Asset?>().firstWhere((item) => item?.id == account.assetId, orElse: () => null);
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: AssetBalanceTile(
                        symbol: asset?.symbol ?? account.assetId,
                        name: asset?.name ?? 'Asset',
                        available: account.availableBalance,
                        locked: account.lockedBalance,
                        total: account.totalBalance,
                      ),
                    );
                  }),
                const SizedBox(height: 14),
                SectionHeader(title: 'Markets', actionLabel: 'Explore', onAction: () => _showComingSoon('Markets')),
                const SizedBox(height: 10),
                if (data.assets.isEmpty)
                  const Card(child: Padding(padding: EdgeInsets.all(20), child: Text('No markets available yet.')))
                else
                  ...data.assets.take(5).map((asset) => Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(child: Text(asset.symbol.isEmpty ? '?' : asset.symbol.substring(0, 1))),
                          title: Text(asset.symbol, style: const TextStyle(fontWeight: FontWeight.w700)),
                          subtitle: Text(asset.name),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () => _showComingSoon('${asset.symbol} market'),
                        ),
                      )),
                const SizedBox(height: 14),
                Card(
                  child: ListTile(
                    leading: const CircleAvatar(child: Icon(Icons.account_balance_wallet_outlined)),
                    title: const Text('Wallets', style: TextStyle(fontWeight: FontWeight.w700)),
                    subtitle: Text('${data.wallets.length} wallet(s) available'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: _openWallets,
                  ),
                ),
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
