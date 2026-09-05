import '../core/constants/api_endpoints.dart';
import '../core/network/api_client.dart';
import '../models/agent_models.dart';

/// Repository for Agent orchestrator dialogs and structured intent recognition.
class AgentRepository {
  final ApiClient apiClient;

  AgentRepository({required this.apiClient});

  /// Submit a user prompt to the AgentOrchestrator loop with conversational state.
  Future<AgentChatResponse> chatWithAgent({
    required String message,
    TravelStateModel? state,
    String? sessionId,
  }) async {
    final payload = <String, dynamic>{
      'message': message,
      'session_id': ?sessionId,
      'state': ?state?.toJson(),
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
