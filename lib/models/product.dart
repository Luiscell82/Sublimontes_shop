class Product {
  final String id;
  final String titulo;
  final String descripcion;
  final double precio;
  final String? imagen; // null = usa placeholder
  final String vendedorId;
  final String vendedorNombre;
  final DateTime fechaPublicacion;

  Product({
    required this.id,
    required this.titulo,
    required this.descripcion,
    required this.precio,
    this.imagen,
    required this.vendedorId,
    required this.vendedorNombre,
    required this.fechaPublicacion,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'titulo': titulo,
      'descripcion': descripcion,
      'precio': precio,
      'imagen': imagen,
      'vendedorId': vendedorId,
      'vendedorNombre': vendedorNombre,
      'fechaPublicacion': fechaPublicacion.toIso8601String(),
    };
  }

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as String,
      titulo: json['titulo'] as String,
      descripcion: json['descripcion'] as String,
      precio: (json['precio'] as num).toDouble(),
      imagen: json['imagen'] as String?,
      vendedorId: json['vendedorId'] as String,
      vendedorNombre: json['vendedorNombre'] as String,
      fechaPublicacion: DateTime.parse(json['fechaPublicacion'] as String),
    );
  }
}
