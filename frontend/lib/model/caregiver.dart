class Caregiver {
  final int id;
  final String name;
  final String specialization;

  Caregiver({
    required this.id,
    required this.name,
    required this.specialization,
  });

  factory Caregiver.fromJson(Map<String, dynamic> json) {
    return Caregiver(
      id: json['id'] as int,
      name: json['name'] as String,
      specialization: json['specialization'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'specialization': specialization,
  };

  @override
  String toString() => 'Caregiver(id: $id, name: $name, spec: $specialization)';
}