import 'package:flutter/material.dart';

class OrdersScreen extends StatelessWidget {
  const OrdersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Orders')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('Open and completed orders will appear here once the trading/order APIs are connected.'),
            ),
          ),
          SizedBox(height: 16),
          _EmptyOrderCard(title: 'Open Orders', icon: Icons.pending_actions),
          SizedBox(height: 10),
          _EmptyOrderCard(title: 'Order History', icon: Icons.history),
        ],
      ),
    );
  }
}

class _EmptyOrderCard extends StatelessWidget {
  const _EmptyOrderCard({required this.title, required this.icon});

  final String title;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(child: Icon(icon)),
        title: Text(title),
        subtitle: const Text('No orders yet'),
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}
