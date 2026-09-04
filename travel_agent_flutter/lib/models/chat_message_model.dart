import 'flight_model.dart';

enum MessageRole {
  user,
  assistant,
  system,
  tool;

  static MessageRole fromString(String role) {
    switch (role.toLowerCase()) {
      case 'user':
        return MessageRole.user;
      case 'assistant':
        return MessageRole.assistant;
      case 'system':
        return MessageRole.system;
      case 'tool':
        return MessageRole.tool;
      default:
        return MessageRole.assistant;
    }
  }
}

class ToolCallTrace {
  final String toolName;
  final Map<String, dynamic> arguments;
  final dynamic result;
  final int? executionTimeMs;

  const ToolCallTrace({
    required this.toolName,
    required this.arguments,
    this.result,
    this.executionTimeMs,
  });

  factory ToolCallTrace.fromJson(Map<String, dynamic> json) {
    return ToolCallTrace(
      toolName: json['tool_name'] as String,
      arguments: json['arguments'] as Map<String, dynamic>? ?? {},
      result: json['result'],
      executionTimeMs: json['execution_time_ms'] as int?,
    );
  }
}

class ChatMessage {
  final String id;
  final MessageRole role;
  final String content;
  final DateTime timestamp;
  final List<FlightModel>? recommendedFlights;
  final ToolCallTrace? toolTrace;
  final bool isThinking;

  const ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.timestamp,
    this.recommendedFlights,
    this.toolTrace,
    this.isThinking = false,
  });

  ChatMessage copyWith({
    String? content,
    List<FlightModel>? recommendedFlights,
    ToolCallTrace? toolTrace,
    bool? isThinking,
  }) {
    return ChatMessage(
      id: id,
      role: role,
      content: content ?? this.content,
      timestamp: timestamp,
      recommendedFlights: recommendedFlights ?? this.recommendedFlights,
      toolTrace: toolTrace ?? this.toolTrace,
      isThinking: isThinking ?? this.isThinking,
    );
  }
}
