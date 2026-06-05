import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../model/booking.dart';
import '../provider/service_provider.dart';
import '../provider/availability_provider.dart';
import '../provider/cart_provider.dart';
import '../provider/patient_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/app_bar_with_cart.dart';
import '../widgets/slot_card.dart';
import 'service_selection_screen.dart';

class AvailabilityScreen extends ConsumerWidget {
  const AvailabilityScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedService = ref.watch(selectedServiceProvider);
    final selectedDate = ref.watch(selectedDateProvider);
    final selectedPatient = ref.watch(selectedPatientProvider);
    final slotsAsync = ref.watch(availableSlotsProvider);

    if (selectedService == null) {
      return Scaffold(
        appBar: const AppBarWithCart(title: 'Select Time'),
        body: const Center(child: Text('No service selected')),
      );
    }

    if (selectedPatient == null) {
      return Scaffold(
        appBar: const AppBarWithCart(title: 'Select Time'),
        body: const Center(
          child: Text('Please select a patient before choosing a time slot'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBarWithCart(
        title: '${selectedService.name} - Select Time',
      ),
      body: Column(
        children: [
          // Date picker
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(Icons.calendar_today, color: AppColors.sageGreen),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () async {
                      final picked = await showDatePicker(
                        context: context,
                        initialDate: DateTime.now(),
                        firstDate: DateTime.now(),
                        lastDate: DateTime.now().add(const Duration(days: 30)),
                      );

                      if (picked != null) {
                        final formattedDate = DateFormat('yyyy-MM-dd').format(picked);
                        ref.read(selectedDateProvider.notifier).state = formattedDate;
                      }
                    },
                    child: Text(
                      selectedDate ?? 'Pick a Date',
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Slots
          Expanded(
            child: selectedDate == null
                ? const Center(
                    child: Text('Select a date to see available slots'),
                  )
                : slotsAsync.when(
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
                            onPressed: () => ref.refresh(availableSlotsProvider),
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    ),
                    data: (response) {
                      if (response == null || response.availableSlots.isEmpty) {
                        return Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.schedule_outlined, size: 48, color: AppColors.neutral),
                              const SizedBox(height: 16),
                              const Text('No slots available for this date'),
                              const SizedBox(height: 8),
                              const Padding(
                                padding: EdgeInsets.symmetric(horizontal: 24),
                                child: Text(
                                  'This time may already be booked. Please pick another date or try a different slot.',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: AppColors.darkGray,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 24),
                              ElevatedButton(
                                onPressed: () {
                                  ref.read(selectedDateProvider.notifier).state = null;
                                },
                                child: const Text('Pick Another Date'),
                              ),
                            ],
                          ),
                        );
                      }

                      return ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: response.availableSlots.length,
                        itemBuilder: (context, index) {
                          final slot = response.availableSlots[index];
                          return SlotCard(
                            slot: slot,
                            serviceName: selectedService.name,
                            servicePrice: selectedService.price,
                            durationMinutes: selectedService.durationMinutes,
                            date: selectedDate,
                            onTap: () {
                              // Add to cart
                              final booking = CartBooking(
                                serviceId: selectedService.id,
                                caregiverId: slot.caregiverId,
                                startTime: slot.startTime,
                                date: selectedDate,
                                serviceName: selectedService.name,
                                price: selectedService.price,
                                durationMinutes: selectedService.durationMinutes,
                              );

                              final added = ref.read(cartProvider.notifier).addBooking(booking: booking);

                              if (!added) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('That slot is already in your cart. Pick a different time.'),
                                    backgroundColor: AppColors.error,
                                  ),
                                );
                                return;
                              }

                              // Show confirmation
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(
                                    '${selectedService.name} added to cart (${ref.read(cartProvider).length} total)',
                                  ),
                                  duration: const Duration(seconds: 2),
                                  backgroundColor: AppColors.success,
                                ),
                              );

                              Navigator.of(context).pushAndRemoveUntil(
                                MaterialPageRoute(
                                  builder: (_) => const ServiceSelectionScreen(),
                                ),
                                (route) => false,
                              );
                            },
                          );
                        },
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
