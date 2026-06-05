import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../model/caregiver.dart';
import 'api_provider.dart';
import 'service_provider.dart';

final caregiversProvider = FutureProvider<List<Caregiver>>((ref) async {
  final selectedService = ref.watch(selectedServiceProvider);
  
  if (selectedService == null) {
    return [];
  }

  final repository = ref.watch(bookingRepositoryProvider);
  return repository.fetchCaregivers(selectedService.id);
});

final selectedCaregiverProvider = StateProvider<Caregiver?>((ref) => null);
