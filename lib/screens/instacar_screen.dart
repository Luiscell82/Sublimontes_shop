import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/instacar_service.dart';
import '../models/lot.dart';

class InstacarScreen extends StatefulWidget {
  const InstacarScreen({super.key});

  @override
  State<InstacarScreen> createState() => _InstacarScreenState();
}

class _InstacarScreenState extends State<InstacarScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabs;
  InstacarService? _svc;
  String _serverUrl = 'http://192.168.1.100:8765';

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
    _loadServerUrl();
  }

  Future<void> _loadServerUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('bot_server_url');
    setState(() {
      if (saved != null) _serverUrl = saved;
      _svc = InstacarService(_serverUrl);
    });
  }

  Future<void> _changeServerUrl() async {
    final controller = TextEditingController(text: _serverUrl);
    final result = await showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('IP del servidor'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'http://192.168.1.100:8765',
            labelText: 'URL del bot',
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          ElevatedButton(
              onPressed: () => Navigator.pop(context, controller.text.trim()),
              child: const Text('Guardar')),
        ],
      ),
    );
    if (result != null && result.isNotEmpty) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('bot_server_url', result);
      setState(() {
        _serverUrl = result;
        _svc = InstacarService(result);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bot Instacar'),
        backgroundColor: const Color(0xFF1565C0),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_ethernet),
            tooltip: 'Cambiar servidor',
            onPressed: _changeServerUrl,
          ),
        ],
        bottom: TabBar(
          controller: _tabs,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          indicatorColor: Colors.amber,
          tabs: const [
            Tab(icon: Icon(Icons.car_rental), text: 'Lotes'),
            Tab(icon: Icon(Icons.tune), text: 'Filtros'),
            Tab(icon: Icon(Icons.monitor_heart), text: 'Estado'),
          ],
        ),
      ),
      body: _svc == null
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabs,
              children: [
                _LotsTab(svc: _svc!),
                _ConfigTab(svc: _svc!),
                _StatusTab(svc: _svc!),
              ],
            ),
    );
  }
}

// ── Tab 1: Lotes ──────────────────────────────────────────────────────────────
class _LotsTab extends StatefulWidget {
  final InstacarService svc;
  const _LotsTab({required this.svc});
  @override
  State<_LotsTab> createState() => _LotsTabState();
}

class _LotsTabState extends State<_LotsTab> {
  late Future<List<Lot>> _future;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() => setState(() => _future = widget.svc.getLots());

  Color _scoreColor(int score) {
    if (score >= 80) return Colors.green.shade700;
    if (score >= 65) return Colors.orange.shade700;
    return Colors.grey.shade600;
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Lot>>(
      future: _future,
      builder: (ctx, snap) {
        if (snap.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snap.hasError) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.wifi_off, size: 60, color: Colors.grey),
                const SizedBox(height: 12),
                Text('No se pudo conectar al bot\n${snap.error}',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.grey)),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: _refresh,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Reintentar'),
                ),
              ],
            ),
          );
        }
        final lots = snap.data ?? [];
        if (lots.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.search_off, size: 60, color: Colors.grey),
                const SizedBox(height: 12),
                const Text('Sin lotes todavía.\nEl bot notificará cuando encuentre buenas oportunidades.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey)),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                    onPressed: _refresh,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Actualizar')),
              ],
            ),
          );
        }
        return RefreshIndicator(
          onRefresh: () async => _refresh(),
          child: ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: lots.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (_, i) {
              final lot = lots[i];
              return Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  leading: CircleAvatar(
                    backgroundColor: _scoreColor(lot.score),
                    child: Text('${lot.score}',
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                  title: Text(
                    '${lot.brand} ${lot.model} ${lot.year ?? ""}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 4),
                      Row(children: [
                        const Icon(Icons.speed, size: 14, color: Colors.blueGrey),
                        const SizedBox(width: 4),
                        Text(lot.mileage != null ? '${_fmt(lot.mileage!)} km' : 'N/D'),
                        const SizedBox(width: 16),
                        const Icon(Icons.attach_money, size: 14, color: Colors.green),
                        Text(lot.price != null
                            ? '\$${lot.price!.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},')} MXN'
                            : 'N/D'),
                      ]),
                      const SizedBox(height: 2),
                      Text(lot.scoreLabel,
                          style: TextStyle(color: _scoreColor(lot.score), fontSize: 12)),
                    ],
                  ),
                  trailing: lot.url != null && lot.url!.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.open_in_new, color: Colors.blue),
                          onPressed: () {/* url_launcher */},
                        )
                      : null,
                ),
              );
            },
          ),
        );
      },
    );
  }

  String _fmt(int n) =>
      n.toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}

// ── Tab 2: Configuración ──────────────────────────────────────────────────────
class _ConfigTab extends StatefulWidget {
  final InstacarService svc;
  const _ConfigTab({required this.svc});
  @override
  State<_ConfigTab> createState() => _ConfigTabState();
}

class _ConfigTabState extends State<_ConfigTab> {
  bool _loading = true;
  bool _saving = false;

  double _maxMileage = 80000;
  double _minYear = 2018;
  double _maxPrice = 0;
  double _minScore = 50;
  final _brandsCtrl = TextEditingController();
  final _intervalCtrl = TextEditingController(text: '15');

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  Future<void> _loadConfig() async {
    try {
      final cfg = await widget.svc.getConfig();
      setState(() {
        _maxMileage = (cfg['max_mileage_km'] as num?)?.toDouble() ?? 80000;
        _minYear    = (cfg['min_year'] as num?)?.toDouble() ?? 2018;
        _maxPrice   = (cfg['max_price_mxn'] as num?)?.toDouble() ?? 0;
        _minScore   = (cfg['min_score'] as num?)?.toDouble() ?? 50;
        _intervalCtrl.text = (cfg['check_interval_minutes'] ?? 15).toString();
        final brands = cfg['brands_priority'];
        _brandsCtrl.text = brands is List ? brands.join(', ') : (brands?.toString() ?? '');
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      final brands = _brandsCtrl.text
          .split(',')
          .map((s) => s.trim().toUpperCase())
          .where((s) => s.isNotEmpty)
          .toList();
      await widget.svc.saveConfig({
        'max_mileage_km': _maxMileage.round(),
        'min_year': _minYear.round(),
        'max_price_mxn': _maxPrice,
        'min_score': _minScore.round(),
        'brands_priority': brands,
        'check_interval_minutes': int.tryParse(_intervalCtrl.text) ?? 15,
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('✅ Configuración guardada'), backgroundColor: Colors.green));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red));
      }
    }
    setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionTitle('Kilometraje máximo'),
          Text('${_maxMileage.round().toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},')} km',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          Slider(
            value: _maxMileage,
            min: 10000,
            max: 200000,
            divisions: 19,
            label: '${(_maxMileage / 1000).round()}k km',
            onChanged: (v) => setState(() => _maxMileage = v),
          ),
          const SizedBox(height: 16),

          _sectionTitle('Año mínimo del vehículo'),
          Text('${_minYear.round()}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          Slider(
            value: _minYear,
            min: 2010,
            max: 2025,
            divisions: 15,
            label: _minYear.round().toString(),
            onChanged: (v) => setState(() => _minYear = v),
          ),
          const SizedBox(height: 16),

          _sectionTitle('Precio máximo (MXN, 0 = sin límite)'),
          Text(_maxPrice == 0 ? 'Sin límite' : '\$${_maxPrice.round().toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},')}',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          Slider(
            value: _maxPrice,
            min: 0,
            max: 1000000,
            divisions: 20,
            label: _maxPrice == 0 ? 'Sin límite' : '\$${(_maxPrice / 1000).round()}k',
            onChanged: (v) => setState(() => _maxPrice = v),
          ),
          const SizedBox(height: 16),

          _sectionTitle('Puntuación mínima para notificar (${_minScore.round()}/100)'),
          Slider(
            value: _minScore,
            min: 0,
            max: 100,
            divisions: 20,
            label: _minScore.round().toString(),
            onChanged: (v) => setState(() => _minScore = v),
          ),
          const SizedBox(height: 16),

          _sectionTitle('Marcas prioritarias (separadas por coma)'),
          TextField(
            controller: _brandsCtrl,
            decoration: const InputDecoration(
              hintText: 'TOYOTA, HONDA, NISSAN',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),

          _sectionTitle('Revisar cada N minutos'),
          TextField(
            controller: _intervalCtrl,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(
              suffixText: 'min',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 28),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1565C0),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14)),
              onPressed: _saving ? null : _save,
              icon: _saving
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.save),
              label: Text(_saving ? 'Guardando...' : 'Guardar configuración'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionTitle(String text) => Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Text(text, style: const TextStyle(fontWeight: FontWeight.w600, color: Colors.black54)));
}

// ── Tab 3: Estado del bot ─────────────────────────────────────────────────────
class _StatusTab extends StatefulWidget {
  final InstacarService svc;
  const _StatusTab({required this.svc});
  @override
  State<_StatusTab> createState() => _StatusTabState();
}

class _StatusTabState extends State<_StatusTab> {
  bool? _running;
  Map<String, dynamic>? _stats;
  bool _toggling = false;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    try {
      final running = await widget.svc.getBotRunning();
      final stats   = await widget.svc.getStats();
      setState(() {
        _running = running;
        _stats   = stats;
      });
    } catch (_) {
      setState(() => _running = null);
    }
  }

  Future<void> _toggle() async {
    if (_running == null) return;
    setState(() => _toggling = true);
    try {
      if (_running!) {
        await widget.svc.stopBot();
      } else {
        await widget.svc.startBot();
      }
      await _refresh();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red));
      }
    }
    setState(() => _toggling = false);
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _refresh,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _statusCard(),
          const SizedBox(height: 16),
          if (_stats != null) _statsCard(),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: _running == true ? Colors.red.shade700 : Colors.green.shade700,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              onPressed: _toggling ? null : _toggle,
              icon: _toggling
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : Icon(_running == true ? Icons.stop : Icons.play_arrow),
              label: Text(_running == true ? 'Detener bot' : 'Iniciar bot'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _statusCard() {
    final connected = _running != null;
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Icon(
              connected ? (_running! ? Icons.check_circle : Icons.pause_circle) : Icons.wifi_off,
              size: 48,
              color: !connected ? Colors.grey : (_running! ? Colors.green : Colors.orange),
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  !connected ? 'Sin conexión' : (_running! ? 'Bot activo' : 'Bot pausado'),
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                Text(
                  !connected
                      ? 'Verifica la IP del servidor'
                      : (_running! ? 'Monitoreando Instacar' : 'No está buscando lotes'),
                  style: const TextStyle(color: Colors.black54),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _statsCard() {
    final s = _stats!;
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Estadísticas', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const Divider(),
            _statRow('Lotes encontrados', '${s['total_lots_seen'] ?? 0}'),
            _statRow('Ciclos ejecutados', '${s['total_runs'] ?? 0}'),
            _statRow('Último ciclo', s['last_run']?.toString() ?? 'nunca'),
          ],
        ),
      ),
    );
  }

  Widget _statRow(String label, String value) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(color: Colors.black54)),
            Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      );
}
