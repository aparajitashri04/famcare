import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../provider/service_provider.dart';
import '../provider/caregiver_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/app_bar_with_cart.dart';
import '../widgets/caregiver_card.dart';
import 'availability_screen.dart';

class CaregiverSelectionScreen extends ConsumerWidget {
  const CaregiverSelectionScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedService = ref.watch(selectedServiceProvider);
    final caregiversAsync = ref.watch(caregiversProvider);

    if (selectedService == null) {
      return Scaffold(
        appBar: const AppBarWithCart(title: 'Select a Caregiver'),
        body: const Center(child: Text('No service selected')),
      );
    }

    return Scaffold(
      appBar: AppBarWithCart(
        title: '${selectedService.name} - Select Caregiver',
      ),
      body: caregiversAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.sageGreen),
        ),
        error: (err, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: AppColors.error),
              const SizedBox(height: 16),
              Text('Error: $err', textAlign: TextAlign.center),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => ref.refresh(caregiversProvider),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
        data: (caregivers) {
          if (caregivers.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.people_outline,
                      size: 48,
                      color: AppColors.neutral,
                    ),
                    const SizedBox(height: 16),
                    const Text('No caregivers available for this service'),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Go Back'),
                    ),
                  ],
                ),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: caregivers.length + 1,
            itemBuilder: (context, index) {
              if (index == 0) {
                return Card(
                  color: AppColors.lightSageGreen,
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    title: const Text(
                      'Any Available Caregiver',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: AppColors.darkSageGreen,
                      ),
                    ),
                    subtitle: const Text('Show all available times'),
                    trailing: const Icon(
                      Icons.arrow_forward,
                      color: AppColors.sageGreen,
                    ),
                    onTap: () {
                      ref.read(selectedCaregiverProvider.notifier).state = null;
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => const AvailabilityScreen(),
                        ),
                      );
                    },
                  ),
                );
              }

              final caregiver = caregivers[index - 1];
              return CaregiverCard(
                caregiver: caregiver,
                onTap: () {
                  ref.read(selectedCaregiverProvider.notifier).state = caregiver;
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => const AvailabilityScreen(),
                    ),
                  );
                },
              );
            },
          );
        },
      ),
    );
  }
}
