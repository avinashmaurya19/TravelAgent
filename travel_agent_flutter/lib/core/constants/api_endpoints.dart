import 'dart:io';
import 'package:flutter/foundation.dart';

/// Centralized API endpoint constants for TravelAgent AI.
class ApiEndpoints {
  ApiEndpoints._();

  /// Optional runtime override for cloud deployment (e.g. Render, ngrok, or Cloudflare tunnel URL).
  static String? remoteUrl = 'https://travelagent-1jxf.onrender.com';

  /// Resolves the base backend URL depending on target platform.
  /// Uses 10.0.2.2 for Android emulator, and localhost for Web/Desktop/iOS.
  static String get baseUrl {
    if (remoteUrl != null && remoteUrl!.isNotEmpty) {
      return remoteUrl!.endsWith('/api/v1') ? remoteUrl! : '${remoteUrl!}/api/v1';
    }
    const customUrl = String.fromEnvironment('API_BASE_URL');
    if (customUrl.isNotEmpty) {
      return customUrl.endsWith('/api/v1') ? customUrl : '$customUrl/api/v1';
    }
    if (kIsWeb) {
      return 'http://localhost:8000/api/v1';
    }
    if (!kIsWeb && Platform.isAndroid) {
      // 127.0.0.1 routes over USB to the host Mac via `adb reverse tcp:8000 tcp:8000`
      return 'http://127.0.0.1:8000/api/v1';
    }
    return 'http://localhost:8000/api/v1';
  }

  // Flights
  static const String flightSearch = '/flights/search';
  static const String flightDetails = '/flights';
  static const String fareBreakdown = '/flights/fare-breakdown';
  static const String flightAvailability = '/flights/{id}/availability';

  // Bookings
  static const String bookings = '/bookings';
  static const String confirmBooking = '/bookings/{id}/confirm';
  static const String cancelBooking = '/bookings/{id}/cancel';

  // Agent
  static const String agentChat = '/agent/chat';
  static const String agentChatStream = '/agent/chat/stream';
  static const String agentIntent = '/agent/intent';

  // Health
  static const String health = '/health';
}
