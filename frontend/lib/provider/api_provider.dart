import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../datasource/api_client.dart';
import '../repository/booking_repository.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

final bookingRepositoryProvider = Provider<BookingRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return BookingRepository(apiClient);
});
