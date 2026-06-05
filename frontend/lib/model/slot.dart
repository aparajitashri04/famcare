class Slot {
  final DateTime startTime;
  final DateTime endTime;
  final int serviceId;
  final int caregiverId;

  Slot({
    required this.startTime,
    required this.endTime,
    required this.serviceId,
    required this.caregiverId,
  });

  factory Slot.fromJson(Map<String, dynamic> json) {
    return Slot(
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
      serviceId: json['service_id'] as int,
      caregiverId: json['caregiver_id'] as int,
    );
  }

  Map<String, dynamic> toJson() => {
    'start_time': startTime.toIso8601String(),
    'end_time': endTime.toIso8601String(),
    'service_id': serviceId,
    'caregiver_id': caregiverId,
  };

  @override
  String toString() => 'Slot($startTime - $endTime, service: $serviceId, caregiver: $caregiverId)';
}