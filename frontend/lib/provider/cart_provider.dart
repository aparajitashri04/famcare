import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../model/booking.dart';

class CartNotifier extends StateNotifier<List<CartBooking>> {
  CartNotifier() : super([]);

  bool addBooking({
    required CartBooking booking,
  }) {
    if (_hasOverlap(booking)) {
      return false;
    }

    state = [...state, booking];
    return true;
  }

  void removeBooking(int index) {
    state = [
      for (int i = 0; i < state.length; i++)
        if (i != index) state[i],
    ];
  }

  void clear() {
    state = [];
  }

  double getTotalPrice() {
    return state.fold(0.0, (sum, booking) => sum + booking.price);
  }

  int getBookingCount() {
    return state.length;
  }

  bool _hasOverlap(CartBooking candidate) {
    final candidateEnd = candidate.startTime.add(Duration(minutes: candidate.durationMinutes));

    for (final existing in state) {
      if (existing.date != candidate.date) {
        continue;
      }

      final existingEnd = existing.startTime.add(Duration(minutes: existing.durationMinutes));
      final overlaps = candidate.startTime.isBefore(existingEnd) && candidateEnd.isAfter(existing.startTime);
      if (overlaps) {
        return true;
      }
    }

    return false;
  }
}

final cartProvider = StateNotifierProvider<CartNotifier, List<CartBooking>>((ref) {
  return CartNotifier();
});

final cartTotalProvider = Provider<double>((ref) {
  final cart = ref.watch(cartProvider);
  return cart.fold(0.0, (sum, booking) => sum + booking.price);
});
