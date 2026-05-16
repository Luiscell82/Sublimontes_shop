import 'package:connectivity_plus/connectivity_plus.dart';

Future<bool> isConnected() async {
  final results = await Connectivity().checkConnectivity();
  // connectivity_plus v6+ returns List<ConnectivityResult>
  if (results is List) {
    return !(results as List).every((r) => r == ConnectivityResult.none);
  }
  // Fallback for older API returning a single value
  return results != ConnectivityResult.none;
}
