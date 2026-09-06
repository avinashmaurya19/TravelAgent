import 'dart:convert';
import 'package:dio/dio.dart';
import '../core/constants/api_endpoints.dart';
import '../core/network/api_client.dart';
import '../models/agent_models.dart';

/// Repository for Agent orchestrator dialogs and structured intent recognition.
class AgentRepository {
  final ApiClient apiClient;

  AgentRepository({required this.apiClient});

  /// Submit a user prompt to the AgentOrchestrator loop with conversational state and prior message history.
  Future<AgentChatResponse> chatWithAgent({
    required String message,
    TravelStateModel? state,
    String? sessionId,
    List<Map<String, String>>? chatHistory,
  }) async {
    final payload = <String, dynamic>{
      'message': message,
      'session_id': ?sessionId,
      'state': ?state?.toJson(),
      'chat_history': ?chatHistory,
    };

    final response = await apiClient.post<Map<String, dynamic>>(
      ApiEndpoints.agentChat,
      data: payload,
    );

    if (response.data == null) {
      throw Exception('Empty response from agent service');
    }

    return AgentChatResponse.fromJson(response.data!);
  }

  /// Stream real-time agent execution events (start, tool_start, tool_result, assistant_message, stream_end) via SSE.
  Stream<Map<String, dynamic>> chatWithAgentStream({
    required String message,
    TravelStateModel? state,
    String? sessionId,
    List<Map<String, String>>? chatHistory,
  }) async* {
    final payload = <String, dynamic>{
      'message': message,
      'session_id': ?sessionId,
      'state': ?state?.toJson(),
      'chat_history': ?chatHistory,
    };

    final response = await apiClient.dio.post<ResponseBody>(
      ApiEndpoints.agentChatStream,
      data: payload,
      options: Options(
        responseType: ResponseType.stream,
        headers: {
          'Accept': 'text/event-stream',
          'Content-Type': 'application/json',
        },
      ),
    );

    final stream = response.data?.stream;
    if (stream == null) {
      throw Exception('Failed to open SSE stream');
    }

    String buffer = '';
    String currentEvent = 'message';

    await for (final chunk in stream.cast<List<int>>().transform(utf8.decoder)) {
      buffer += chunk;
      final lines = buffer.split('\n');
      buffer = lines.removeLast();

      for (final line in lines) {
        final trimmed = line.trim();
        if (trimmed.isEmpty) {
          currentEvent = 'message';
          continue;
        }
        if (trimmed.startsWith('event:')) {
          currentEvent = trimmed.substring(6).trim();
        } else if (trimmed.startsWith('data:')) {
          final dataStr = trimmed.substring(5).trim();
          try {
            final dataJson = jsonDecode(dataStr);
            if (dataJson is Map<String, dynamic>) {
              yield {'event': currentEvent, 'data': dataJson};
            } else {
              yield {'event': currentEvent, 'data': dataJson};
            }
          } catch (_) {
            yield {'event': currentEvent, 'data': dataStr};
          }
        }
      }
    }
  }

  /// Recognize structured travel intent from natural language query.
  Future<Map<String, dynamic>> recognizeIntent({
    required String query,
    String? context,
  }) async {
    final payload = <String, dynamic>{
      'query': query,
      'context': ?context,
    };

    final response = await apiClient.post<Map<String, dynamic>>(
      ApiEndpoints.agentIntent,
      data: payload,
    );

    return response.data ?? {};
  }
}
