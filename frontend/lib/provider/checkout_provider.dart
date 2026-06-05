import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../datasource/api_client.dart';
import 'api_provider.dart';
import 'cart_provider.dart';
import 'patient_provider.dart';

final checkoutProvider = FutureProvider.family<CheckoutResponse, int>(
  (ref, patientId) async {
    final repository = ref.watch(bookingRepositoryProvider);
    final cart = ref.watch(cartProvider);

    if (cart.isEmpty) {
      throw Exception('Cart is empty');
    }

    return repository.checkout(
      patientId: patientId,
      bookings: cart,
    );
  },
);

final checkoutForSelectedPatientProvider =
    FutureProvider<CheckoutResponse?>((ref) async {
  final patient = ref.watch(selectedPatientProvider);
  if (patient == null) {
    return null;
  }

  final repository = ref.watch(bookingRepositoryProvider);
  final cart = ref.watch(cartProvider);

  if (cart.isEmpty) {
    throw Exception('Cart is empty');
  }

  return repository.checkout(
    patientId: patient.id,
    bookings: cart,
  );
});

// State for tracking checkout result
final checkoutResultProvider = StateProvider<CheckoutResponse?>((ref) => null);

final checkoutLoadingProvider = StateProvider<bool>((ref) => false);
