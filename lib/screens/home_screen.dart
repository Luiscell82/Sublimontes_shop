
import 'package:flutter/material.dart';
import 'instacar_screen.dart';

class HomeScreen extends StatelessWidget {
  final bool tieneMembresia = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sublimontes Shop'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              'Los usuarios invitados pueden ver productos sin registrarse.\n'
              'Para publicar productos debes pagar la membresía.\n'
              'Solo usuarios con membresía activa pueden publicar.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.black54),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {},
              child: const Text('Publicar Producto'),
            ),
            ElevatedButton(
              onPressed: () {},
              child: const Text('Chat de Usuarios'),
            ),
            ElevatedButton(
              onPressed: () {},
              child: const Text('Compartir Productos'),
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1565C0),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
                icon: const Icon(Icons.car_rental),
                label: const Text('Bot Instacar — Ver Lotes',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const InstacarScreen()),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
