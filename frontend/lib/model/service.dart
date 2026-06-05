class Service {
  final int id;
  final String name;
  final int durationMinutes;
  final double price;

  Service({
    required this.id,
    required this.name,
    required this.durationMinutes,
    required this.price,
  });

  factory Service.fromJson(Map<String, dynamic> json) {
    return Service(
      id: json['id'] as int,
      name: json['name'] as String,
      durationMinutes: json['duration_minutes'] as int,
      price: (json['price'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'duration_minutes': durationMinutes,
    'price': price,
  };

  @override
  String toString() => 'Service(id: $id, name: $name, duration: $durationMinutes min, price: \$${price.toStringAsFixed(2)})';
}