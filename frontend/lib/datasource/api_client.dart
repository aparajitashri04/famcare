import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../model/service.dart';
import '../model/caregiver.dart';
import '../model/patient.dart';
import '../model/slot.dart';
import '../model/booking.dart';

String resolveApiBaseUrl() {
  const envBaseUrl = String.fromEnvironment('API_BASE_URL');
  if (envBaseUrl.isNotEmpty) {
    return envBaseUrl;
  }

  if (kIsWeb) {
    return 'http://localhost:8000';
  }

  if (defaultTargetPlatform == TargetPlatform.android) {
    return 'http://10.0.2.2:8000';
  }

  return 'http://localhost:8000';
}

class ApiClient {
  late Dio _dio;
  final String baseUrl;

  ApiClient({String? baseUrl}) : baseUrl = baseUrl ?? resolveApiBaseUrl() {
    _dio = Dio(
      BaseOptions(
        baseUrl: this.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        contentType: 'application/json',
      ),
    );
  }

  // GET /slots/services
  Future<List<Service>> getServices() async {
    try {
      final response = await _dio.get('/slots/services');
      final list = response.data as List;
      return list.map((json) => Service.fromJson(json)).toList();
    } on DioException catch (e) {
      throw ApiException(_formatNetworkError('services', e));
    }
  }

  // GET /slots/caregivers-for-service/{service_id}
  Future<List<Caregiver>> getCaregiversByService(int serviceId) async {
    try {
      final response = await _dio.get('/slots/caregivers-for-service/$serviceId');
      final list = response.data as List;
      return list.map((json) => Caregiver.fromJson(json)).toList();
    } on DioException catch (e) {
      throw ApiException(_formatNetworkError('caregivers', e));
    }
  }

  Future<List<Patient>> getPatients() async {
    try {
      final response = await _dio.get('/slots/patients');
      final list = response.data as List;
      return list.map((json) => Patient.fromJson(json)).toList();
    } on DioException catch (e) {
      throw ApiException(_formatNetworkError('patients', e));
    }
  }

  Future<Patient> createPatient({
    required String name,
    required String contact,
  }) async {
    try {
      final response = await _dio.post(
        '/slots/patients',
        data: {
          'name': name,
          'contact': contact,
        },
      );
      return Patient.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException(_formatNetworkError('patient creation', e));
    }
  }

  // GET /slots/available
  Future<AvailableSlotsResponse> getAvailableSlots({
    required int serviceId,
    required String date, // YYYY-MM-DD
    int? caregiverId,
    int? patientId,
  }) async {
    try {
      final params = {
        'service_id': serviceId,
        'date': date,
        if (caregiverId != null) 'caregiver_id': caregiverId,
        if (patientId != null) 'patient_id': patientId,
      };

      final response = await _dio.get(
        '/slots/available',
        queryParameters: params,
      );

      return AvailableSlotsResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(_formatNetworkError('availability', e));
    }
  }

  // POST /cart/checkout
  Future<CheckoutResponse> checkout({
    required int patientId,
    required List<CartBooking> bookings,
  }) async {
    try {
      final payload = {
        'patient_id': patientId,
        'bookings': bookings.map((b) => b.toRequestJson()).toList(),
      };

      final response = await _dio.post('/cart/checkout', data: payload);
      return CheckoutResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException(_formatNetworkError('checkout', e));
    }
  }

  String _formatNetworkError(String action, DioException error) {
    final message = error.message ?? 'Unknown network error';
    final uri = error.requestOptions.uri;

    if (error.type == DioExceptionType.connectionError ||
        error.type == DioExceptionType.connectionTimeout) {
      return 'Failed to load $action from $baseUrl ($uri). '
          'Check that the backend is running and that the device can reach it. '
          'If you are on an Android emulator, use 10.0.2.2 instead of localhost. '
          'Details: $message';
    }

    return 'Failed to load $action: $message';
  }
}

// Response models

class AvailableSlotsResponse {
  final int serviceId;
  final String date;
  final String serviceName;
  final int durationMinutes;
  final List<Slot> availableSlots;

  AvailableSlotsResponse({
    required this.serviceId,
    required this.date,
    required this.serviceName,
    required this.durationMinutes,
    required this.availableSlots,
  });

  factory AvailableSlotsResponse.fromJson(Map<String, dynamic> json) {
    final slotsList = (json['available_slots'] as List)
        .map((slot) => Slot.fromJson(slot))
        .toList();

    return AvailableSlotsResponse(
      serviceId: json['service_id'] as int,
      date: json['date'] as String,
      serviceName: json['service_name'] as String,
      durationMinutes: json['duration_minutes'] as int,
      availableSlots: slotsList,
    );
  }
}

class CheckoutResponse {
  final bool success;
  final String message;
  final List<ConfirmedBooking>? bookings;
  final double? totalPrice;
  final int? failedBookingIndex;
  final String? reason;

  CheckoutResponse({
    required this.success,
    required this.message,
    this.bookings,
    this.totalPrice,
    this.failedBookingIndex,
    this.reason,
  });

  factory CheckoutResponse.fromJson(Map<String, dynamic> json) {
    final bookingsList = json['bookings'] != null
        ? (json['bookings'] as List)
            .map((b) => ConfirmedBooking.fromJson(b))
            .toList()
        : null;

    return CheckoutResponse(
      success: json['success'] as bool,
      message: json['message'] as String,
      bookings: bookingsList,
      totalPrice: json['total_price'] != null
          ? (json['total_price'] as num).toDouble()
          : null,
      failedBookingIndex: json['failed_booking_index'],
      reason: json['reason'],
    );
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
