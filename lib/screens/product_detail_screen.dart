import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';
import '../utils/app_state.dart';
import '../models/product.dart';

class ProductDetailScreen extends StatelessWidget {
  final String productId;

  const ProductDetailScreen({super.key, required this.productId});

  Product? _findProduct(AppState state) {
    try {
      return state.products.firstWhere((p) => p.id == productId);
    } catch (_) {
      return null;
    }
  }

  void _compartir(Product product) {
    final text =
        'Mira este producto en Sublimontes Shop!\n\n'
        '${product.titulo}\n'
        'Precio: \$${product.precio.toStringAsFixed(0)}\n'
        'Vendedor: ${product.vendedorNombre}\n\n'
        '${product.descripcion}\n\n'
        '[Sublimontes Shop - ID: ${product.id}]';
    Share.share(text, subject: product.titulo);
  }

  void _irAlChat(BuildContext context, AppState appState, Product product) {
    if (!appState.isLoggedIn) {
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Iniciar sesión requerido'),
          content: const Text(
            'Debes iniciar sesión para acceder al chat con el vendedor.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/login');
              },
              child: const Text('Iniciar Sesión'),
            ),
          ],
        ),
      );
      return;
    }
    Navigator.pushNamed(context, '/chat', arguments: product.id);
  }

  @override
  Widget build(BuildContext context) {
    final appState = context.watch<AppState>();
    final product = _findProduct(appState);

    if (product == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Producto')),
        body: const Center(
          child: Text('Producto no encontrado.'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(product.titulo, overflow: TextOverflow.ellipsis),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            tooltip: 'Compartir',
            onPressed: () => _compartir(product),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Imagen placeholder
            Container(
              height: 250,
              width: double.infinity,
              color: Colors.purple.shade50,
              child: const Center(
                child: Icon(Icons.image, size: 100, color: Colors.purple),
              ),
            ),

            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Precio destacado
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          product.titulo,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFF6A1B9A),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '\$${product.precio.toStringAsFixed(0)}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 12),

                  // Vendedor
                  Card(
                    child: ListTile(
                      leading: const CircleAvatar(
                        backgroundColor: Color(0xFFE1BEE7),
                        child: Icon(Icons.store, color: Color(0xFF6A1B9A)),
                      ),
                      title: Text(product.vendedorNombre),
                      subtitle: Text(
                        'Publicado el ${_formatDate(product.fechaPublicacion)}',
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Descripción
                  const Text(
                    'Descripción',
                    style: TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    product.descripcion,
                    style: const TextStyle(fontSize: 15, height: 1.5),
                  ),

                  const SizedBox(height: 32),

                  // Botones de acción
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _compartir(product),
                          icon: const Icon(Icons.share),
                          label: const Text('Compartir'),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        flex: 2,
                        child: ElevatedButton.icon(
                          onPressed: () =>
                              _irAlChat(context, appState, product),
                          icon: const Icon(Icons.chat_bubble_outline),
                          label: const Text('Chatear con vendedor'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                        ),
                      ),
                    ],
                  ),

                  if (!appState.isLoggedIn) ...[
                    const SizedBox(height: 8),
                    Text(
                      'Inicia sesión para contactar al vendedor',
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 12,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    if (diff.inDays == 0) {
      if (diff.inHours == 0) return 'hace ${diff.inMinutes} minutos';
      return 'hace ${diff.inHours} horas';
    }
    if (diff.inDays == 1) return 'ayer';
    if (diff.inDays < 7) return 'hace ${diff.inDays} días';
    return '${date.day}/${date.month}/${date.year}';
  }
}
