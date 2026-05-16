class User {
  final String id;
  final String nombre;
  final String email;
  final String password;
  bool tieneMembresia;
  DateTime? fechaMembresia;

  User({
    required this.id,
    required this.nombre,
    required this.email,
    required this.password,
    this.tieneMembresia = false,
    this.fechaMembresia,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'email': email,
      'password': password,
      'tieneMembresia': tieneMembresia,
      'fechaMembresia': fechaMembresia?.toIso8601String(),
    };
  }

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      email: json['email'] as String,
      password: json['password'] as String,
      tieneMembresia: json['tieneMembresia'] as bool? ?? false,
      fechaMembresia: json['fechaMembresia'] != null
          ? DateTime.parse(json['fechaMembresia'] as String)
          : null,
    );
  }

  User copyWith({
    String? id,
    String? nombre,
    String? email,
    String? password,
    bool? tieneMembresia,
    DateTime? fechaMembresia,
  }) {
    return User(
      id: id ?? this.id,
      nombre: nombre ?? this.nombre,
      email: email ?? this.email,
      password: password ?? this.password,
      tieneMembresia: tieneMembresia ?? this.tieneMembresia,
      fechaMembresia: fechaMembresia ?? this.fechaMembresia,
    );
  }
}
