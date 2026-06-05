class CartBooking {
  final int serviceId;
  final int caregiverId;
  final DateTime startTime;
  final String date; // YYYY-MM-DD
  final String serviceName;
  final double price;
  final int durationMinutes;

  CartBooking({
    required this.serviceId,
    required this.caregiverId,
    required this.startTime,
    required this.date,
    required this.serviceName,
    required this.price,
    required this.durationMinutes,
  });

  // Convert to request body format
  Map<String, dynamic> toRequestJson() => {
    'service_id': serviceId,
    'caregiver_id': caregiverId,
    'start_time': startTime.toIso8601String(),
    'date': date,
  };

  @override
  String toString() => 'CartBooking($serviceName on $date at ${startTime.hour}:${startTime.minute.toString().padLeft(2, '0')}, \$$price)';
}

class ConfirmedBooking {
  final int id;
  final int serviceId;
  final int caregiverId;
  final int patientId;
  final DateTime startTime;
  final DateTime endTime;
  final double price;
  final DateTime createdAt;

  ConfirmedBooking({
    required this.id,
    required this.serviceId,
    required this.caregiverId,
    required this.patientId,
    required this.startTime,
    required this.endTime,
    required this.price,
    required this.createdAt,
  });

  factory ConfirmedBooking.fromJson(Map<String, dynamic> json) {
    return ConfirmedBooking(
      id: json['id'] as int,
      serviceId: json['service_id'] as int,
      caregiverId: json['caregiver_id'] as int,
      patientId: json['patient_id'] as int,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
      price: (json['price'] as num).toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  @override
  String toString() => 'ConfirmedBooking(id: $id, $startTime - $endTime, \$$price)';
}