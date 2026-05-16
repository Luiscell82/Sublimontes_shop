import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../utils/app_state.dart';

class MembershipScreen extends StatefulWidget {
  const MembershipScreen({super.key});

  @override
  State<MembershipScreen> createState() => _MembershipScreenState();
}

class _MembershipScreenState extends State<MembershipScreen> {
  bool _isActivating = false;

  Future<void> _activarMembresia(AppState appState) async {
    setState(() => _isActivating = true);

    // Simular demora de procesamiento de pago
    await Future.delayed(const Duration(seconds: 2));

    await appState.activarMembresia();

    if (!mounted) return;
    setState(() => _isActivating = false);

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green, size: 28),
            SizedBox(width: 8),
            Text('Membresía Activada'),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Tu membresía ha sido activada exitosamente.',
              style: TextStyle(fontSize: 15),
            ),
            SizedBox(height: 12),
            Text(
              'Ahora puedes publicar productos ilimitados en Sublimontes Shop.',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context); // Cerrar dialog
              Navigator.pop(context); // Volver a pantalla anterior
            },
            child: const Text('Comenzar a publicar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appState = context.watch<AppState>();

    if (!appState.isLoggedIn) {
      return Scaffold(
        appBar: AppBar(title: const Text('Membresía')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.lock, size: 64, color: Colors.grey),
              const SizedBox(height: 16),
              const Text(
                'Debes iniciar sesión para activar una membresía.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey, fontSize: 16),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () =>
                    Navigator.pushReplacementNamed(context, '/login'),
                child: const Text('Iniciar Sesión'),
              ),
            ],
          ),
        ),
      );
    }

    if (appState.tieneMembresia) {
      return Scaffold(
        appBar: AppBar(title: const Text('Membresía')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.verified, size: 80, color: Colors.green),
                const SizedBox(height: 20),
                const Text(
                  'Membresía Activa',
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  appState.currentUser!.fechaMembresia != null
                      ? 'Activada el ${_formatDate(appState.currentUser!.fechaMembresia!)}'
                      : 'Membresía activa',
                  style: const TextStyle(color: Colors.grey),
                ),
                const SizedBox(height: 32),
                Card(
                  color: Colors.green.shade50,
                  child: const Padding(
                    padding: EdgeInsets.all(16),
                    child: Column(
                      children: [
                        _BenefitRow(
                          icon: Icons.check,
                          text: 'Publicaciones ilimitadas',
                        ),
                        _BenefitRow(
                          icon: Icons.check,
                          text: 'Acceso prioritario al soporte',
                        ),
                        _BenefitRow(
                          icon: Icons.check,
                          text: 'Estadísticas de productos',
                        ),
                        _BenefitRow(
                          icon: Icons.check,
                          text: 'Badge de vendedor verificado',
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                ElevatedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, '/publish'),
                  icon: const Icon(Icons.add_box),
                  label: const Text('Publicar un Producto'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 14,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Activar Membresía')),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Header degradado
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 24),
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFF6A1B9A), Color(0xFFFF6F00)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: const Column(
                children: [
                  Icon(Icons.star, size: 64, color: Colors.white),
                  SizedBox(height: 16),
                  Text(
                    'Membresía Premium',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Publica tus productos y llega a más clientes',
                    style: TextStyle(color: Colors.white70, fontSize: 15),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),

            Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  // Precio
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.purple.shade50,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.purple.shade200),
                    ),
                    child: Column(
                      children: [
                        const Text(
                          'Plan Mensual',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '\$',
                              style: TextStyle(
                                fontSize: 22,
                                color: Color(0xFF6A1B9A),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              '1.500',
                              style: TextStyle(
                                fontSize: 52,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF6A1B9A),
                                height: 1,
                              ),
                            ),
                          ],
                        ),
                        const Text(
                          'por mes',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Beneficios
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Incluye:',
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Card(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 8),
                      child: Column(
                        children: [
                          _BenefitRow(
                            icon: Icons.add_box,
                            text: 'Publicaciones ilimitadas de productos',
                          ),
                          _BenefitRow(
                            icon: Icons.chat,
                            text: 'Chat directo con compradores',
                          ),
                          _BenefitRow(
                            icon: Icons.share,
                            text: 'Herramientas de compartir',
                          ),
                          _BenefitRow(
                            icon: Icons.verified_user,
                            text: 'Badge de vendedor verificado',
                          ),
                          _BenefitRow(
                            icon: Icons.support_agent,
                            text: 'Soporte prioritario',
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // Botón activar
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _isActivating
                          ? null
                          : () => _activarMembresia(appState),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 18),
                        backgroundColor: const Color(0xFFFF6F00),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: _isActivating
                          ? const Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                SizedBox(
                                  width: 22,
                                  height: 22,
                                  child: CircularProgressIndicator(
                                    color: Colors.white,
                                    strokeWidth: 2,
                                  ),
                                ),
                                SizedBox(width: 12),
                                Text(
                                  'Procesando pago...',
                                  style: TextStyle(fontSize: 16),
                                ),
                              ],
                            )
                          : const Text(
                              'Activar Membresía - \$1.500/mes',
                              style: TextStyle(
                                fontSize: 17,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                  ),

                  const SizedBox(height: 12),
                  Text(
                    'Pago simulado para demostración. Sin cargo real.',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade500,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

class _BenefitRow extends StatelessWidget {
  final IconData icon;
  final String text;

  const _BenefitRow({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      dense: true,
      leading: Icon(icon, color: Colors.green, size: 20),
      title: Text(text),
    );
  }
}
