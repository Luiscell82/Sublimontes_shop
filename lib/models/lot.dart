class Lot {
  final String id;
  final String brand;
  final String model;
  final int? year;
  final int? mileage;
  final double? price;
  final int score;
  final String? url;
  final String? seenAt;

  const Lot({
    required this.id,
    required this.brand,
    required this.model,
    this.year,
    this.mileage,
    this.price,
    required this.score,
    this.url,
    this.seenAt,
  });

  factory Lot.fromJson(Map<String, dynamic> j) => Lot(
        id: j['id']?.toString() ?? '',
        brand: j['brand']?.toString() ?? 'N/D',
        model: j['model']?.toString() ?? '',
        year: j['year'] as int?,
        mileage: j['mileage'] as int?,
        price: (j['price'] as num?)?.toDouble(),
        score: (j['score'] as int?) ?? 0,
        url: j['url']?.toString(),
        seenAt: j['seen_at']?.toString(),
      );

  String get scoreLabel {
    if (score >= 80) return '🔥 Excelente';
    if (score >= 65) return '✅ Bueno';
    return '🔔 Regular';
  }
}
