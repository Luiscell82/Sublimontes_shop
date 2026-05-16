import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import '../models/user.dart';
import '../models/product.dart';
import '../models/message.dart';

const _uuid = Uuid();

class AppState extends ChangeNotifier {
  User? _currentUser;
  List<User> _users = [];
  List<Product> _products = [];
  List<Message> _messages = [];
  bool _isLoading = false;

  User? get currentUser => _currentUser;
  bool get isLoggedIn => _currentUser != null;
  bool get tieneMembresia => _currentUser?.tieneMembresia ?? false;
  bool get isLoading => _isLoading;

  List<Product> get products => List.unmodifiable(_products);

  List<Message> mensajesPorProducto(String productId) {
    return _messages
        .where((m) => m.productId == productId)
        .toList()
      ..sort((a, b) => a.timestamp.compareTo(b.timestamp));
  }

  AppState() {
    _init();
  }

  Future<void> _init() async {
    _isLoading = true;
    notifyListeners();
    await _loadFromPrefs();
    if (_products.isEmpty) {
      _seedProducts();
    }
    _isLoading = false;
    notifyListeners();
  }

  void _seedProducts() {
    final seedVendedorId = _uuid.v4();
    _products = [
      Product(
        id: _uuid.v4(),
        titulo: 'Camiseta Personalizada',
        descripcion:
            'Camiseta 100% algodón con sublimación de alta calidad. Disponible en todos los talles. '
            'Diseño personalizable con fotos o texto.',
        precio: 4500,
        imagen: null,
        vendedorId: seedVendedorId,
        vendedorNombre: 'Sublimaciones Pérez',
        fechaPublicacion: DateTime.now().subtract(const Duration(days: 3)),
      ),
      Product(
        id: _uuid.v4(),
        titulo: 'Taza Sublimada',
        descripcion:
            'Taza cerámica de 11oz con impresión sublimada a todo color. '
            'Resistente al lavavajillas. Ideal para regalos corporativos.',
        precio: 2800,
        imagen: null,
        vendedorId: seedVendedorId,
        vendedorNombre: 'Sublimaciones Pérez',
        fechaPublicacion: DateTime.now().subtract(const Duration(days: 5)),
      ),
      Product(
        id: _uuid.v4(),
        titulo: 'Almohada Decorativa',
        descripcion:
            'Almohada 40x40cm con funda sublimada. Relleno de fibra siliconada. '
            'Cierre con cremallera invisible. Lavable a máquina.',
        precio: 6200,
        imagen: null,
        vendedorId: _uuid.v4(),
        vendedorNombre: 'Arte en Tela',
        fechaPublicacion: DateTime.now().subtract(const Duration(days: 1)),
      ),
      Product(
        id: _uuid.v4(),
        titulo: 'Mousepad Personalizado',
        descripcion:
            'Mousepad de 20x24cm con base antideslizante. Superficie de tela de alta definición. '
            'Impresión de borde a borde con tu diseño favorito.',
        precio: 1900,
        imagen: null,
        vendedorId: _uuid.v4(),
        vendedorNombre: 'Prints & More',
        fechaPublicacion: DateTime.now().subtract(const Duration(hours: 12)),
      ),
    ];
    _saveProductsToPrefs();
  }

  // --------------- AUTH ---------------

  Future<String?> register({
    required String nombre,
    required String email,
    required String password,
  }) async {
    if (nombre.trim().isEmpty || email.trim().isEmpty || password.isEmpty) {
      return 'Todos los campos son obligatorios.';
    }
    if (!email.contains('@') || !email.contains('.')) {
      return 'El email no es válido.';
    }
    if (password.length < 6) {
      return 'La contraseña debe tener al menos 6 caracteres.';
    }
    final exists = _users.any(
      (u) => u.email.toLowerCase() == email.toLowerCase(),
    );
    if (exists) {
      return 'Ya existe una cuenta con ese email.';
    }

    final newUser = User(
      id: _uuid.v4(),
      nombre: nombre.trim(),
      email: email.trim().toLowerCase(),
      password: password,
    );
    _users.add(newUser);
    _currentUser = newUser;
    await _saveToPrefs();
    notifyListeners();
    return null; // null = éxito
  }

  Future<String?> login({
    required String email,
    required String password,
  }) async {
    if (email.trim().isEmpty || password.isEmpty) {
      return 'Ingresa email y contraseña.';
    }
    final user = _users.firstWhere(
      (u) =>
          u.email.toLowerCase() == email.trim().toLowerCase() &&
          u.password == password,
      orElse: () => User(id: '', nombre: '', email: '', password: ''),
    );
    if (user.id.isEmpty) {
      return 'Email o contraseña incorrectos.';
    }
    _currentUser = user;
    await _saveCurrentUserToPrefs();
    notifyListeners();
    return null;
  }

  Future<void> logout() async {
    _currentUser = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('currentUserId');
    notifyListeners();
  }

  // --------------- MEMBRESÍA ---------------

  Future<void> activarMembresia() async {
    if (_currentUser == null) return;
    final idx = _users.indexWhere((u) => u.id == _currentUser!.id);
    if (idx == -1) return;

    _users[idx].tieneMembresia = true;
    _users[idx].fechaMembresia = DateTime.now();
    _currentUser = _users[idx];
    await _saveToPrefs();
    notifyListeners();
  }

  // --------------- PRODUCTOS ---------------

  Future<String?> publicarProducto({
    required String titulo,
    required String descripcion,
    required double precio,
    String? imagen,
  }) async {
    if (_currentUser == null) {
      return 'Debes iniciar sesión para publicar.';
    }
    if (!_currentUser!.tieneMembresia) {
      return 'Necesitas membresía activa para publicar.';
    }
    if (titulo.trim().isEmpty) return 'El título es obligatorio.';
    if (descripcion.trim().isEmpty) return 'La descripción es obligatoria.';
    if (precio <= 0) return 'El precio debe ser mayor a cero.';

    final producto = Product(
      id: _uuid.v4(),
      titulo: titulo.trim(),
      descripcion: descripcion.trim(),
      precio: precio,
      imagen: imagen,
      vendedorId: _currentUser!.id,
      vendedorNombre: _currentUser!.nombre,
      fechaPublicacion: DateTime.now(),
    );
    _products.insert(0, producto);
    await _saveProductsToPrefs();
    notifyListeners();
    return null;
  }

  // --------------- MENSAJES ---------------

  Future<String?> enviarMensaje({
    required String texto,
    required String productId,
  }) async {
    if (_currentUser == null) {
      return 'Debes iniciar sesión para chatear.';
    }
    if (texto.trim().isEmpty) return 'El mensaje no puede estar vacío.';

    final msg = Message(
      id: _uuid.v4(),
      texto: texto.trim(),
      senderId: _currentUser!.id,
      senderNombre: _currentUser!.nombre,
      timestamp: DateTime.now(),
      productId: productId,
    );
    _messages.add(msg);
    await _saveMessagesToPrefs();
    notifyListeners();
    return null;
  }

  // --------------- PERSISTENCIA ---------------

  Future<void> _loadFromPrefs() async {
    final prefs = await SharedPreferences.getInstance();

    // Cargar usuarios
    final usersJson = prefs.getString('users');
    if (usersJson != null) {
      final List decoded = jsonDecode(usersJson) as List;
      _users = decoded
          .map((e) => User.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    // Cargar productos
    final productsJson = prefs.getString('products');
    if (productsJson != null) {
      final List decoded = jsonDecode(productsJson) as List;
      _products = decoded
          .map((e) => Product.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    // Cargar mensajes
    final messagesJson = prefs.getString('messages');
    if (messagesJson != null) {
      final List decoded = jsonDecode(messagesJson) as List;
      _messages = decoded
          .map((e) => Message.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    // Restaurar sesión
    final currentUserId = prefs.getString('currentUserId');
    if (currentUserId != null) {
      try {
        _currentUser = _users.firstWhere((u) => u.id == currentUserId);
      } catch (_) {
        _currentUser = null;
      }
    }
  }

  Future<void> _saveToPrefs() async {
    final prefs = await SharedPreferences.getInstance();
    final usersJson = jsonEncode(_users.map((u) => u.toJson()).toList());
    await prefs.setString('users', usersJson);
    await _saveCurrentUserToPrefs();
  }

  Future<void> _saveCurrentUserToPrefs() async {
    final prefs = await SharedPreferences.getInstance();
    if (_currentUser != null) {
      await prefs.setString('currentUserId', _currentUser!.id);
    }
  }

  Future<void> _saveProductsToPrefs() async {
    final prefs = await SharedPreferences.getInstance();
    final json = jsonEncode(_products.map((p) => p.toJson()).toList());
    await prefs.setString('products', json);
  }

  Future<void> _saveMessagesToPrefs() async {
    final prefs = await SharedPreferences.getInstance();
    final json = jsonEncode(_messages.map((m) => m.toJson()).toList());
    await prefs.setString('messages', json);
  }
}
