import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/app_theme.dart';
import 'screens/patient_selection_screen.dart';

void main() {
  runApp(const ProviderScope(child: FamCareApp()));
}

class FamCareApp extends StatelessWidget {
  const FamCareApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FamCare Booking',
      theme: AppTheme.lightTheme(),
      home: const PatientSelectionScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
