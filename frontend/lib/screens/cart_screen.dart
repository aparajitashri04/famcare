import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../provider/cart_provider.dart';
import '../provider/checkout_provider.dart';
import '../provider/patient_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/app_bar_with_cart.dart';
import '../widgets/booking_summary.dart';
import 'checkout_result_screen.dart';
import 'service_selection_screen.dart';

class CartScreen extends ConsumerWidget {
  const CartScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cart = ref.watch(cartProvider);
    final total = ref.watch(cartTotalProvider);

    if (cart.isEmpty) {
      return Scaffold(
        appBar: AppBarWithCart(
          title: 'Your Cart',
          showBackButton: true,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: AppColors.lightSageGreen,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.shopping_cart_outlined,
                  size: 40,
                  color: AppColors.sageGreen,
                ),
              ),
              const SizedBox(height: 24),
              const Text(
                'No bookings added yet',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.darkSageGreen,
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'Build your booking by selecting services',
                style: TextStyle(
                  fontSize: 14,
                  color: AppColors.darkGray,
                ),
              ),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(
                      builder: (_) => const ServiceSelectionScreen(),
                    ),
                    (route) => false,
                  );
                },
                icon: const Icon(Icons.storefront),
                label: const Text('Browse Services'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBarWithCart(
        title: 'Your Cart (${cart.length})',
        showBackButton: true,
      ),
      body: Column(
        children: [
          // Cart items
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: cart.length,
              itemBuilder: (context, index) {
                final booking = cart[index];
                return BookingSummaryCard(
                  booking: booking,
                  index: index,
                  showRemoveButton: true,
                  onRemove: () {
                    ref.read(cartProvider.notifier).removeBooking(index);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('${booking.serviceName} removed'),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                );
              },
            ),
          ),

          // Summary and checkout button
          Container(
            color: AppColors.lightSageGreen,
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${cart.length} booking${cart.length != 1 ? 's' : ''}',
                          style: const TextStyle(
                            fontSize: 16,
                            color: AppColors.darkGray,
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Total:',
                          style: TextStyle(
                            fontSize: 14,
                            color: AppColors.darkGray,
                          ),
                        ),
                      ],
                    ),
                    Text(
                      '\$${total.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: AppColors.sageGreen,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 16),

                OutlinedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pushAndRemoveUntil(
                      MaterialPageRoute(
                        builder: (_) => const ServiceSelectionScreen(),
                      ),
                      (route) => false,
                    );
                  },
                  icon: const Icon(Icons.add),
                  label: const Text('Add Another Service'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),

                const SizedBox(height: 12),

                ElevatedButton.icon(
                  onPressed: () => _handleCheckout(context, ref),
                  icon: const Icon(Icons.done_all),
                  label: const Text('Proceed to Checkout'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _handleCheckout(BuildContext context, WidgetRef ref) async {
    final cart = ref.read(cartProvider);
    final selectedPatient = ref.read(selectedPatientProvider);
    if (cart.isEmpty) return;
    if (selectedPatient == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select or create a patient first.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        title: Text('Processing Checkout'),
        content: CircularProgressIndicator(color: AppColors.sageGreen),
      ),
    );

    try {
      final result = await ref.read(checkoutProvider(selectedPatient.id).future);
      
      if (!context.mounted) return;
      Navigator.pop(context); // Close loading dialog

      // Navigate to result screen
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => CheckoutResultScreen(result: result),
        ),
      );
    } catch (e) {
      if (!context.mounted) return;
      Navigator.pop(context); // Close loading dialog

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Checkout error: $e'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }
}
