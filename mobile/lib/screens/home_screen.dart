import 'package:flutter/material.dart';

import '../config/api_config.dart';
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
  final _authService = AuthService();
  late Future<dynamic> _assetsFuture;

  @override
  void initState() {
    super.initState();
    _assetsFuture = _apiClient.get(ApiConfig.assetsPath);
  }

  Future<void> _logout() async {
    await _authService.logout();
    if (mounted) widget.onLogout();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('BitNova'),
        actions: [
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout)),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          setState(() => _assetsFuture = _apiClient.get(ApiConfig.assetsPath));
          await _assetsFuture;
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Portfolio', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Text('₹ 0.00', style: Theme.of(context).textTheme.headlineMedium),
                    const SizedBox(height: 4),
                    const Text('Connect this card to /accounts and /wallets in the next mobile phase.'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            Text('Markets', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            FutureBuilder<dynamic>(
              future: _assetsFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()));
                }
                if (snapshot.hasError) {
                  return Card(child: ListTile(leading: const Icon(Icons.error_outline), title: Text('Unable to load markets')));
                }

                final data = snapshot.data;
                final items = data is List ? data : (data is Map<String, dynamic> ? (data['items'] ?? data['assets'] ?? []) : []);
                if (items is! List || items.isEmpty) {
                  return const Card(child: ListTile(title: Text('No assets available')));
                }

                return Column(
                  children: items.take(10).map<Widget>((item) {
                    final map = item is Map ? item : <String, dynamic>{};
                    final symbol = map['symbol']?.toString() ?? map['code']?.toString() ?? 'ASSET';
                    final name = map['name']?.toString() ?? symbol;
                    return Card(
                      child: ListTile(
                        leading: const CircleAvatar(child: Icon(Icons.currency_exchange)),
                        title: Text(symbol),
                        subtitle: Text(name),
                      ),
                    );
                  }).toList(),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
