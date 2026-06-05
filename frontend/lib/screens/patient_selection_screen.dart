import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../provider/api_provider.dart';
import '../provider/cart_provider.dart';
import '../provider/patient_provider.dart';
import '../provider/service_provider.dart';
import '../provider/caregiver_provider.dart';
import '../provider/availability_provider.dart';
import '../theme/app_theme.dart';
import 'service_selection_screen.dart';

class PatientSelectionScreen extends ConsumerStatefulWidget {
  const PatientSelectionScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<PatientSelectionScreen> createState() =>
      _PatientSelectionScreenState();
}

class _PatientSelectionScreenState extends ConsumerState<PatientSelectionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _contactController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _contactController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final patientsAsync = ref.watch(patientsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Select User'),
        backgroundColor: AppColors.sageGreen,
        foregroundColor: AppColors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 24),
            patientsAsync.when(
              loading: () => const Center(
                child: Padding(
                  padding: EdgeInsets.symmetric(vertical: 40),
                  child: CircularProgressIndicator(color: AppColors.sageGreen),
                ),
              ),
              error: (_, __) => const SizedBox.shrink(),

              data: (patients) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 24),
                    const Text(
                      'Create New Patient',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: AppColors.darkSageGreen,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Form(
                      key: _formKey,
                      child: Column(
                        children: [
                          TextFormField(
                            controller: _nameController,
                            decoration: const InputDecoration(
                              border: OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return 'Enter a name';
                                hintText: 'Name',
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: _contactController,
                            decoration: const InputDecoration(
                              hintText: 'Email or phone',
                              border: OutlineInputBorder(),
                            ),
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return 'Enter contact info';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 20),
                          ElevatedButton.icon(
                            onPressed: () => _createPatient(context),
                            label: const Text('Create'),
                            style: ElevatedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 20),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _createPatient(BuildContext context) async {
    if (!_formKey.currentState!.validate()) return;

    final repository = ref.read(bookingRepositoryProvider);
    final name = _nameController.text.trim();
    final contact = _contactController.text.trim();

    try {
      final patient = await repository.createPatient(
        name: name,
        contact: contact,
      );
      ref.read(selectedPatientProvider.notifier).state = patient;
      _nameController.clear();
      _contactController.clear();
      if (!context.mounted) return;
      _continue(context);
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not create patient: $e'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  void _continue(BuildContext context) {
    ref.read(cartProvider.notifier).clear();
    ref.read(selectedServiceProvider.notifier).state = null;
    ref.read(selectedCaregiverProvider.notifier).state = null;
    ref.read(selectedDateProvider.notifier).state = null;

    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => const ServiceSelectionScreen(),
      ),
    );
  }
}
