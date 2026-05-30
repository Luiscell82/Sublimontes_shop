
import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  final bool tieneMembresia = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Sublimontes Shop'),
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              'Los usuarios invitados pueden ver productos sin registrarse.\n'
              'Para publicar productos debes pagar la membresía.\n'
              'Solo usuarios con membresía activa pueden publicar.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.black54),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Ir a publicar producto (si tiene membresía)
              },
              child: Text('Publicar Producto'),
            ),
            ElevatedButton(
              onPressed: () {
                // Ir al chat
              },
              child: Text('Chat de Usuarios'),
            ),
            ElevatedButton(
              onPressed: () {
                // Compartir link público
              },
              child: Text('Compartir Productos'),
            ),
          ],
        ),
      ),
    );
  }
}
