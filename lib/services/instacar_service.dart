import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/lot.dart';

class InstacarService {
  final String baseUrl;

  InstacarService(this.baseUrl);

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  Future<List<Lot>> getLots() async {
    final res = await http.get(_uri('/lots')).timeout(const Duration(seconds: 10));
    if (res.statusCode != 200) throw Exception('Error ${res.statusCode}');
    final list = jsonDecode(res.body) as List;
    return list.map((e) => Lot.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Map<String, dynamic>> getStats() async {
    final res = await http.get(_uri('/stats')).timeout(const Duration(seconds: 10));
    if (res.statusCode != 200) throw Exception('Error ${res.statusCode}');
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getConfig() async {
    final res = await http.get(_uri('/config')).timeout(const Duration(seconds: 10));
    if (res.statusCode != 200) throw Exception('Error ${res.statusCode}');
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<void> saveConfig(Map<String, dynamic> data) async {
    final res = await http
        .post(_uri('/config'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(data))
        .timeout(const Duration(seconds: 10));
    if (res.statusCode != 200) throw Exception('Error ${res.statusCode}');
  }

  Future<bool> getBotRunning() async {
    final res = await http.get(_uri('/status')).timeout(const Duration(seconds: 10));
    if (res.statusCode != 200) return false;
    final body = jsonDecode(res.body) as Map<String, dynamic>;
    return body['running'] == true;
  }

  Future<void> startBot() async {
    await http.post(_uri('/start')).timeout(const Duration(seconds: 10));
  }

  Future<void> stopBot() async {
    await http.post(_uri('/stop')).timeout(const Duration(seconds: 10));
  }
}
