class Message {
  final String id;
  final String texto;
  final String senderId;
  final String senderNombre;
  final DateTime timestamp;
  final String productId;

  Message({
    required this.id,
    required this.texto,
    required this.senderId,
    required this.senderNombre,
    required this.timestamp,
    required this.productId,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'texto': texto,
      'senderId': senderId,
      'senderNombre': senderNombre,
      'timestamp': timestamp.toIso8601String(),
      'productId': productId,
    };
  }

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] as String,
      texto: json['texto'] as String,
      senderId: json['senderId'] as String,
      senderNombre: json['senderNombre'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      productId: json['productId'] as String,
    );
  }
}
