import 'package:flutter/material.dart';

import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'services/auth_service.dart';
import 'services/token_storage.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const BitNovaApp());
}

class BitNovaApp extends StatelessWidget {
  const BitNovaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BitNova',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1565C0)),
        useMaterial3: true,
        inputDecorationTheme: const InputDecorationTheme(border: OutlineInputBorder()),
      ),
      home: const SessionGate(),
    );
  }
}

class SessionGate extends StatefulWidget {
  const SessionGate({super.key});

  @override
  State<SessionGate> createState() => _SessionGateState();
}

class _SessionGateState extends State<SessionGate> {
  late Future<bool> _sessionFuture;
  bool _showRegister = false;

  @override
  void initState() {
    super.initState();
    _sessionFuture = TokenStorage().accessToken().then((token) => token != null && token.isNotEmpty);
  }

  void _showLogin() => setState(() {
        _showRegister = false;
        _sessionFuture = Future.value(false);
      });

  void _showRegisterScreen() => setState(() {
        _showRegister = true;
        _sessionFuture = Future.value(false);
      });

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
      future: _sessionFuture,
      builder: (context, snapshot) {
        if (!snapshot.hasData) return const Scaffold(body: Center(child: CircularProgressIndicator()));
        if (snapshot.data == true) return HomeScreen(onLogout: _showLogin);
        if (_showRegister) {
          return RegisterScreen(onRegistered: _showLogin, onLogin: _showLogin);
        }
        return LoginScreen(onLoggedIn: () => setState(() => _sessionFuture = Future.value(true)), onRegister: _showRegisterScreen);
      },
    );
  }
}
