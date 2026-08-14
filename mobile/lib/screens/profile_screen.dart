import 'package:flutter/material.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({required this.onLogout, super.key});

  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Card(
            child: ListTile(
              leading: CircleAvatar(radius: 28, child: Icon(Icons.person)),
              title: Text('My Account'),
              subtitle: Text('Account details and verification'),
            ),
          ),
          const SizedBox(height: 12),
          const Card(
            child: Column(
              children: [
                ListTile(leading: Icon(Icons.verified_user_outlined), title: Text('KYC & Verification'), trailing: Icon(Icons.chevron_right)),
                Divider(height: 1),
                ListTile(leading: Icon(Icons.security_outlined), title: Text('Security'), trailing: Icon(Icons.chevron_right)),
                Divider(height: 1),
                ListTile(leading: Icon(Icons.notifications_outlined), title: Text('Notifications'), trailing: Icon(Icons.chevron_right)),
              ],
            ),
          ),
          const SizedBox(height: 24),
          OutlinedButton.icon(
            onPressed: onLogout,
            icon: const Icon(Icons.logout),
            label: const Text('Log out'),
          ),
        ],
      ),
    );
  }
}
