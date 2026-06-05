import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../model/service.dart';
import 'api_provider.dart';

final servicesProvider = FutureProvider<List<Service>>((ref) async {
  final repository = ref.watch(bookingRepositoryProvider);
  return repository.fetchServices();
});

final selectedServiceProvider = StateProvider<Service?>((ref) => null);
