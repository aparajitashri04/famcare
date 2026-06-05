class Patient {
  final int id;
  final String name;
  final String contact;

  Patient({
    required this.id,
    required this.name,
    required this.contact,
  });

  factory Patient.fromJson(Map<String, dynamic> json) {
    return Patient(
      id: json['id'] as int,
      name: json['name'] as String,
      contact: json['contact'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'contact': contact,
      };

  @override
  String toString() => 'Patient(id: $id, name: $name, contact: $contact)';
}
