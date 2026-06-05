import '../datasource/api_client.dart';
import '../model/service.dart';
import '../model/caregiver.dart';
import '../model/patient.dart';
import '../model/booking.dart';

class BookingRepository {
  final ApiClient _apiClient;

  BookingRepository(this._apiClient);

  Future<List<Service>> fetchServices() async {
    return _apiClient.getServices();
  }

  Future<List<Caregiver>> fetchCaregivers(int serviceId) async {
    return _apiClient.getCaregiversByService(serviceId);
  }

  Future<List<Patient>> fetchPatients() async {
    return _apiClient.getPatients();
  }

  Future<Patient> createPatient({
    required String name,
    required String contact,
  }) async {
    return _apiClient.createPatient(
      name: name,
      contact: contact,
    );
  }

  Future<AvailableSlotsResponse> fetchAvailableSlots({
    required int serviceId,
    required String date,
    int? caregiverId,
    int? patientId,
  }) async {
    return _apiClient.getAvailableSlots(
      serviceId: serviceId,
      date: date,
      caregiverId: caregiverId,
      patientId: patientId,
    );
  }

  Future<CheckoutResponse> checkout({
    required int patientId,
    required List<CartBooking> bookings,
  }) async {
    return _apiClient.checkout(
      patientId: patientId,
      bookings: bookings,
    );
  }
}
