import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../provider/caregiver_provider.dart';
import '../provider/availability_provider.dart';
import '../provider/service_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/app_bar_with_cart.dart';
import '../widgets/service_card.dart';
import 'caregiver_selection_screen.dart';

class ServiceSelectionScreen extends ConsumerWidget {
  const ServiceSelectionScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final servicesAsync = ref.watch(servicesProvider);

    return Scaffold(
      appBar: AppBarWithCart(
        title: 'Select a Service',
        showBackButton: false,
      ),
      body: servicesAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.sageGreen),
        ),
        error: (err, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.error_outline,
                  size: 48,
                  color: AppColors.error,
                ),
                const SizedBox(height: 16),
                Text(
                  'Error: $err',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () => ref.refresh(servicesProvider),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
        data: (services) {
          if (services.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.inbox_outlined,
                      size: 48,
                      color: AppColors.neutral,
                    ),
                    const SizedBox(height: 16),
                    const Text('No services available'),
                  ],
                ),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: services.length,
            itemBuilder: (context, index) {
              final service = services[index];
              return ServiceCard(
                service: service,
                onTap: () {
                  // Reset dependent booking state before moving forward.
                  ref.read(selectedServiceProvider.notifier).state = service;
                  ref.read(selectedCaregiverProvider.notifier).state = null;
                  ref.read(selectedDateProvider.notifier).state = null;

                  // Navigate to caregiver selection.
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => const CaregiverSelectionScreen(),
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
