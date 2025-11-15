// lib/main.dart

import 'package:flutter/foundation.dart'; // Para detectar Web
import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:provider/provider.dart';

import 'config/app_theme.dart';
import 'providers/auth_provider.dart';
import 'providers/cart_provider.dart';
import 'providers/voice_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/home/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ======================================
  // 🔵 CONFIGURACIÓN STRIPE (solo Android/iOS)
  // ======================================
  if (!kIsWeb) {
    Stripe.publishableKey =
        'pk_test_51SMNuqALw8Dff5KWhKFLmwBejETY51GWez3LriWG8PfuthhQvghYwA472KLTZG57JDtSbq7SUEkbwVdfTZX0Mtcz00ABWGf0o6';
    // Opcional, si quieres ApplePay en iOS:
    // Stripe.merchantIdentifier = 'merchant.com.smartsales';

    await Stripe.instance.applySettings();
  }

  runApp(const SmartSalesApp());
}

class SmartSalesApp extends StatelessWidget {
  const SmartSalesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()..restoreSession()),
        ChangeNotifierProvider(create: (_) => CartProvider()),
        ChangeNotifierProvider(create: (_) => VoiceProvider()),
      ],
      child: Consumer<AuthProvider>(
        builder: (context, auth, _) {
          return MaterialApp(
            debugShowCheckedModeBanner: false,
            title: 'SmartSales365',
            theme: AppTheme.light,
            home: auth.isLoggedIn ? const HomeScreen() : const LoginScreen(),
          );
        },
      ),
    );
  }
}
