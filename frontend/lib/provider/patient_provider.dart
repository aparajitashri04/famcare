import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../model/patient.dart';
import 'api_provider.dart';

final patientsProvider = FutureProvider<List<Patient>>((ref) async {
  final repository = ref.watch(bookingRepositoryProvider);
  return repository.fetchPatients();
});

final selectedPatientProvider = StateProvider<Patient?>((ref) => null);
