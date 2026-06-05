import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../datasource/api_client.dart';
import 'api_provider.dart';
import 'service_provider.dart';
import 'caregiver_provider.dart';
import 'patient_provider.dart';

final selectedDateProvider = StateProvider<String?>((ref) => null);

final availableSlotsProvider = FutureProvider<AvailableSlotsResponse?>((ref) async {
  final selectedService = ref.watch(selectedServiceProvider);
  final selectedDate = ref.watch(selectedDateProvider);
  final selectedCaregiver = ref.watch(selectedCaregiverProvider);
  final selectedPatient = ref.watch(selectedPatientProvider);

  if (selectedService == null || selectedDate == null || selectedPatient == null) {
    return null;
  }

  final repository = ref.watch(bookingRepositoryProvider);
  return repository.fetchAvailableSlots(
    serviceId: selectedService.id,
    date: selectedDate,
    caregiverId: selectedCaregiver?.id,
    patientId: selectedPatient.id,
  );
});
