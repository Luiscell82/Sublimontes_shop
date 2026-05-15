import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';

// ─── Data models ───────────────────────────────────────────────
enum DrawTool { pencil, brush, eraser, line, rect, circle, fill, text }

class DrawnPoint {
  final Offset point;
  final Paint paint;
  final bool isStart;
  const DrawnPoint({required this.point, required this.paint, required this.isStart});
}

class DrawnShape {
  final DrawTool type;
  final Offset start;
  final Offset end;
  final Paint paint;
  final bool filled;
  const DrawnShape({
    required this.type,
    required this.start,
    required this.end,
    required this.paint,
    required this.filled,
  });
}

class DrawnText {
  final Offset position;
  final String text;
  final TextStyle style;
  const DrawnText({required this.position, required this.text, required this.style});
}

// ─── Painter ───────────────────────────────────────────────────
class CanvasPainter extends CustomPainter {
  final List<List<DrawnPoint>> strokes;
  final List<DrawnPoint> currentStroke;
  final List<DrawnShape> shapes;
  final DrawnShape? previewShape;
  final List<DrawnText> texts;
  final Color bgColor;
  final bool showGrid;

  const CanvasPainter({
    required this.strokes,
    required this.currentStroke,
    required this.shapes,
    this.previewShape,
    required this.texts,
    required this.bgColor,
    required this.showGrid,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // background
    canvas.drawRect(
      Rect.fromLTWH(0, 0, size.width, size.height),
      Paint()..color = bgColor,
    );

    // grid
    if (showGrid) {
      final gridPaint = Paint()
        ..color = Colors.grey.withOpacity(0.25)
        ..strokeWidth = 0.5;
      const step = 40.0;
      for (double x = 0; x < size.width;  x += step) canvas.drawLine(Offset(x, 0), Offset(x, size.height), gridPaint);
      for (double y = 0; y < size.height; y += step) canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    // committed strokes
    for (final stroke in strokes) _drawStroke(canvas, stroke);

    // current stroke
    _drawStroke(canvas, currentStroke);

    // shapes
    for (final s in shapes) _drawShape(canvas, s);
    if (previewShape != null) _drawShape(canvas, previewShape!);

    // texts
    for (final t in texts) {
      final tp = TextPainter(
        text: TextSpan(text: t.text, style: t.style),
        textDirection: ui.TextDirection.ltr,
      )..layout();
      tp.paint(canvas, t.position);
    }
  }

  void _drawStroke(Canvas canvas, List<DrawnPoint> stroke) {
    if (stroke.isEmpty) return;
    final path = Path();
    for (int i = 0; i < stroke.length; i++) {
      if (stroke[i].isStart || i == 0) {
        path.moveTo(stroke[i].point.dx, stroke[i].point.dy);
      } else {
        final prev = stroke[i - 1].point;
        final curr = stroke[i].point;
        path.quadraticBezierTo(prev.dx, prev.dy, (prev.dx + curr.dx) / 2, (prev.dy + curr.dy) / 2);
      }
    }
    canvas.drawPath(path, stroke.first.paint);
  }

  void _drawShape(Canvas canvas, DrawnShape s) {
    final p = s.paint;
    switch (s.type) {
      case DrawTool.line:
        canvas.drawLine(s.start, s.end, p);
        break;
      case DrawTool.rect:
        final r = Rect.fromPoints(s.start, s.end);
        if (s.filled) canvas.drawRect(r, p..style = PaintingStyle.fill);
        canvas.drawRect(r, p..style = PaintingStyle.stroke);
        break;
      case DrawTool.circle:
        final c = Rect.fromPoints(s.start, s.end);
        if (s.filled) canvas.drawOval(c, p..style = PaintingStyle.fill);
        canvas.drawOval(c, p..style = PaintingStyle.stroke);
        break;
      default:
        break;
    }
  }

  @override
  bool shouldRepaint(CanvasPainter old) => true;
}

// ─── Screen ────────────────────────────────────────────────────
class CanvasScreen extends StatefulWidget {
  const CanvasScreen({super.key});

  @override
  State<CanvasScreen> createState() => _CanvasScreenState();
}

class _CanvasScreenState extends State<CanvasScreen> {
  // drawing state
  DrawTool _tool        = DrawTool.pencil;
  Color    _color       = const Color(0xFFe94560);
  double   _strokeWidth = 6;
  double   _opacity     = 1.0;
  bool     _filled      = false;
  bool     _showGrid    = false;
  Color    _bgColor     = Colors.white;

  // history
  List<List<DrawnPoint>> _strokes         = [];
  List<DrawnPoint>       _currentStroke   = [];
  List<DrawnShape>       _shapes          = [];
  DrawnShape?            _previewShape;
  List<DrawnText>        _texts           = [];

  // undo/redo stacks — each entry is a full snapshot
  final List<_Snapshot> _history  = [];
  final List<_Snapshot> _redoStack = [];

  Offset? _shapeStart;

  // palette
  static const _palette = [
    Color(0xFF000000), Color(0xFF444444), Color(0xFF888888), Color(0xFFcccccc),
    Color(0xFFffffff), Color(0xFFe94560), Color(0xFFff9f43), Color(0xFFffd32a),
    Color(0xFF2ecc71), Color(0xFF00d2d3), Color(0xFF54a0ff), Color(0xFF5f27cd),
    Color(0xFFb71c1c), Color(0xFF006064), Color(0xFF1b5e20), Color(0xFF4a148c),
  ];

  Paint get _activePaint => Paint()
    ..color       = _color.withOpacity(_opacity)
    ..strokeWidth = _strokeWidth
    ..strokeCap   = StrokeCap.round
    ..strokeJoin  = StrokeJoin.round
    ..style       = PaintingStyle.stroke
    ..isAntiAlias = true;

  // ── History helpers ──────────────────────────────
  void _saveHistory() {
    _history.add(_Snapshot(
      strokes: List.from(_strokes.map((s) => List<DrawnPoint>.from(s))),
      shapes: List<DrawnShape>.from(_shapes),
      texts:  List<DrawnText>.from(_texts),
    ));
    _redoStack.clear();
  }

  void _undo() {
    if (_history.length <= 1) return;
    _redoStack.add(_history.removeLast());
    final snap = _history.last;
    setState(() {
      _strokes = List.from(snap.strokes.map((s) => List<DrawnPoint>.from(s)));
      _shapes  = List<DrawnShape>.from(snap.shapes);
      _texts   = List<DrawnText>.from(snap.texts);
    });
  }

  void _redo() {
    if (_redoStack.isEmpty) return;
    final snap = _redoStack.removeLast();
    _history.add(snap);
    setState(() {
      _strokes = List.from(snap.strokes.map((s) => List<DrawnPoint>.from(s)));
      _shapes  = List<DrawnShape>.from(snap.shapes);
      _texts   = List<DrawnText>.from(snap.texts);
    });
  }

  // ── Gesture handlers ────────────────────────────
  void _onPanStart(DragStartDetails d) {
    final pos = d.localPosition;
    if (_tool == DrawTool.text) {
      _showTextDialog(pos);
      return;
    }
    if (_isShapeTool) {
      _shapeStart = pos;
    } else {
      setState(() => _currentStroke = [DrawnPoint(point: pos, paint: _activePaint, isStart: true)]);
    }
  }

  void _onPanUpdate(DragUpdateDetails d) {
    final pos = d.localPosition;
    if (_isShapeTool && _shapeStart != null) {
      setState(() => _previewShape = DrawnShape(
        type: _tool, start: _shapeStart!, end: pos,
        paint: _activePaint, filled: _filled,
      ));
    } else if (_tool == DrawTool.eraser) {
      setState(() => _currentStroke.add(
        DrawnPoint(point: pos, paint: Paint()
          ..color = _bgColor
          ..strokeWidth = _strokeWidth * 2
          ..strokeCap = StrokeCap.round
          ..style = PaintingStyle.stroke, isStart: false),
      ));
    } else if (_tool == DrawTool.pencil || _tool == DrawTool.brush) {
      setState(() => _currentStroke.add(
        DrawnPoint(point: pos, paint: _activePaint, isStart: false),
      ));
    }
  }

  void _onPanEnd(DragEndDetails _) {
    if (_isShapeTool && _previewShape != null) {
      _saveHistory();
      setState(() { _shapes.add(_previewShape!); _previewShape = null; _shapeStart = null; });
    } else if (_currentStroke.isNotEmpty) {
      _saveHistory();
      setState(() { _strokes.add(List.from(_currentStroke)); _currentStroke = []; });
    }
  }

  bool get _isShapeTool => [DrawTool.line, DrawTool.rect, DrawTool.circle].contains(_tool);

  void _showTextDialog(Offset pos) async {
    final ctrl = TextEditingController();
    final result = await showDialog<String>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF16213e),
        title: const Text('Agregar texto', style: TextStyle(color: Colors.white)),
        content: TextField(
          controller: ctrl,
          autofocus: true,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(hintText: 'Escribe aquí…', hintStyle: TextStyle(color: Colors.grey)),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFe94560)),
            onPressed: () => Navigator.pop(context, ctrl.text),
            child: const Text('Confirmar'),
          ),
        ],
      ),
    );
    if (result != null && result.isNotEmpty) {
      _saveHistory();
      setState(() => _texts.add(DrawnText(
        position: pos,
        text:     result,
        style:    TextStyle(color: _color.withOpacity(_opacity), fontSize: max(_strokeWidth * 3, 14), fontWeight: FontWeight.bold),
      )));
    }
  }

  void _clear() {
    _saveHistory();
    setState(() { _strokes.clear(); _shapes.clear(); _texts.clear(); _currentStroke.clear(); });
  }

  // ── Build ────────────────────────────────────────
  @override
  void initState() {
    super.initState();
    _saveHistory(); // initial empty snapshot
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1a1a2e),
      appBar: AppBar(
        backgroundColor: const Color(0xFF16213e),
        title: const Text('Diseño Sublimontes', style: TextStyle(color: Colors.white, fontSize: 16)),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(icon: const Icon(Icons.undo), tooltip: 'Deshacer', onPressed: _undo),
          IconButton(icon: const Icon(Icons.redo), tooltip: 'Rehacer',  onPressed: _redo),
          IconButton(
            icon: Icon(_showGrid ? Icons.grid_on : Icons.grid_off, color: _showGrid ? const Color(0xFFe94560) : Colors.white),
            tooltip: 'Cuadrícula',
            onPressed: () => setState(() => _showGrid = !_showGrid),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Color(0xFFe94560)),
            tooltip: 'Limpiar',
            onPressed: () => showDialog(
              context: context,
              builder: (_) => AlertDialog(
                title: const Text('¿Limpiar lienzo?'),
                content: const Text('Esta acción se puede deshacer.'),
                actions: [
                  TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
                  ElevatedButton(onPressed: () { Navigator.pop(context); _clear(); }, child: const Text('Limpiar')),
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          // tool bar
          _buildToolbar(),
          // canvas
          Expanded(
            child: GestureDetector(
              onPanStart:  _onPanStart,
              onPanUpdate: _onPanUpdate,
              onPanEnd:    _onPanEnd,
              child: ClipRect(
                child: CustomPaint(
                  painter: CanvasPainter(
                    strokes:       _strokes,
                    currentStroke: _currentStroke,
                    shapes:        _shapes,
                    previewShape:  _previewShape,
                    texts:         _texts,
                    bgColor:       _bgColor,
                    showGrid:      _showGrid,
                  ),
                  size: Size.infinite,
                ),
              ),
            ),
          ),
          // bottom panel
          _buildBottomPanel(),
        ],
      ),
    );
  }

  Widget _buildToolbar() {
    final tools = [
      (DrawTool.pencil, Icons.edit,            'Lápiz'),
      (DrawTool.brush,  Icons.brush,            'Pincel'),
      (DrawTool.eraser, Icons.cleaning_services,'Borrador'),
      (DrawTool.line,   Icons.remove,           'Línea'),
      (DrawTool.rect,   Icons.crop_square,      'Rectángulo'),
      (DrawTool.circle, Icons.circle_outlined,  'Círculo'),
      (DrawTool.text,   Icons.text_fields,      'Texto'),
    ];
    return Container(
      color: const Color(0xFF16213e),
      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: tools.map((t) {
            final selected = _tool == t.$1;
            return Padding(
              padding: const EdgeInsets.only(right: 4),
              child: Tooltip(
                message: t.$3,
                child: InkWell(
                  borderRadius: BorderRadius.circular(8),
                  onTap: () => setState(() => _tool = t.$1),
                  child: Container(
                    width: 44, height: 44,
                    decoration: BoxDecoration(
                      color: selected ? const Color(0xFF1e1030) : Colors.transparent,
                      border: Border.all(color: selected ? const Color(0xFFe94560) : Colors.transparent, width: 2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(t.$2, color: selected ? const Color(0xFFe94560) : Colors.grey, size: 22),
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildBottomPanel() {
    return Container(
      color: const Color(0xFF16213e),
      padding: const EdgeInsets.all(10),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Color palette
          SizedBox(
            height: 32,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: _palette.length,
              separatorBuilder: (_, __) => const SizedBox(width: 4),
              itemBuilder: (_, i) {
                final c = _palette[i];
                final sel = _color == c;
                return GestureDetector(
                  onTap: () => setState(() => _color = c),
                  child: Container(
                    width: 28, height: 28,
                    decoration: BoxDecoration(
                      color: c,
                      border: Border.all(color: sel ? Colors.white : Colors.transparent, width: 2),
                      borderRadius: BorderRadius.circular(6),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 8),
          // Size + Opacity
          Row(
            children: [
              const Text('Tamaño', style: TextStyle(color: Colors.grey, fontSize: 11)),
              const SizedBox(width: 8),
              Expanded(
                child: Slider(
                  value: _strokeWidth,
                  min: 1, max: 60,
                  activeColor: const Color(0xFFe94560),
                  onChanged: (v) => setState(() => _strokeWidth = v),
                ),
              ),
              Text('${_strokeWidth.round()}', style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
              const SizedBox(width: 16),
              const Text('Opacidad', style: TextStyle(color: Colors.grey, fontSize: 11)),
              const SizedBox(width: 8),
              Expanded(
                child: Slider(
                  value: _opacity,
                  min: 0.05, max: 1.0,
                  activeColor: const Color(0xFFe94560),
                  onChanged: (v) => setState(() => _opacity = v),
                ),
              ),
              Text('${(_opacity * 100).round()}%', style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
            ],
          ),
          if (_isShapeTool)
            Row(
              children: [
                Checkbox(
                  value: _filled,
                  activeColor: const Color(0xFFe94560),
                  onChanged: (v) => setState(() => _filled = v ?? false),
                ),
                const Text('Relleno sólido', style: TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
        ],
      ),
    );
  }
}

// ─── Snapshot ──────────────────────────────────────────────────
class _Snapshot {
  final List<List<DrawnPoint>> strokes;
  final List<DrawnShape> shapes;
  final List<DrawnText> texts;
  const _Snapshot({required this.strokes, required this.shapes, required this.texts});
}
