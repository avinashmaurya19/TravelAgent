import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/chat_message_model.dart';
import 'flight_card.dart';

/// Renders user and assistant chat bubbles, tool trace badges, and flight cards.
class MessageBubble extends StatelessWidget {
  final ChatMessage message;

  const MessageBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == MessageRole.user;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
      child: Column(
        crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          // Tool Trace Badges if present (Shows agent reasoning/tool action)
          if (message.allTraces.isNotEmpty)
            _buildToolTraces(message.allTraces),

          // Bubble Container
          Row(
            mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (!isUser) ...[
                Container(
                  padding: const EdgeInsets.all(6),
                  margin: const EdgeInsets.only(right: 8, top: 4),
                  decoration: const BoxDecoration(
                    color: AppColors.primary,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.auto_awesome, size: 14, color: Colors.white),
                ),
              ],
              Flexible(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: isUser ? AppColors.userBubble : AppColors.assistantBubble,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(16),
                      topRight: const Radius.circular(16),
                      bottomLeft: Radius.circular(isUser ? 16 : 4),
                      bottomRight: Radius.circular(isUser ? 4 : 16),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (message.isThinking)
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const SizedBox(
                              width: 14,
                              height: 14,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              message.content.isNotEmpty
                                  ? message.content
                                  : 'Agent is thinking & querying services...',
                              style: const TextStyle(fontSize: 13, fontStyle: FontStyle.italic),
                            ),
                          ],
                        )
                      else
                        Text(
                          message.content,
                          style: TextStyle(
                            color: isUser ? Colors.white : AppColors.textPrimary,
                            fontSize: 14,
                            height: 1.4,
                          ),
                        ),
                      const SizedBox(height: 4),
                      Text(
                        DateFormat('HH:mm').format(message.timestamp),
                        style: TextStyle(
                          fontSize: 10,
                          color: isUser ? Colors.white70 : AppColors.textMuted,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),

          // Recommended Flights Cards in the chat stream
          if (message.recommendedFlights != null && message.recommendedFlights!.isNotEmpty) ...[
            const SizedBox(height: 10),
            Padding(
              padding: const EdgeInsets.only(left: 36.0),
              child: Column(
                children: message.recommendedFlights!.map((flight) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: FlightCard(flight: flight),
                  );
                }).toList(),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildToolTraces(List<ToolCallTrace> traces) {
    // Group traces by toolName to avoid vertical UI clutter
    final Map<String, List<ToolCallTrace>> grouped = {};
    for (final trace in traces) {
      grouped.putIfAbsent(trace.toolName, () => []).add(trace);
    }

    return Padding(
      padding: const EdgeInsets.only(left: 36, bottom: 6),
      child: Wrap(
        spacing: 6,
        runSpacing: 4,
        children: grouped.entries.map((entry) {
          final toolName = entry.key;
          final toolTraces = entry.value;
          final count = toolTraces.length;
          final totalMs = toolTraces.fold<int>(
            0,
            (sum, t) => sum + (t.executionTimeMs ?? 0),
          );

          final label = count > 1
              ? 'Executed: $toolName ($count queries • ${totalMs}ms)'
              : (toolTraces.first.executionTimeMs != null
                  ? 'Executed: $toolName (${toolTraces.first.executionTimeMs}ms)'
                  : 'Executed: $toolName');

          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.toolBadge,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.border),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.build_circle_outlined, size: 14, color: AppColors.toolBadgeText),
                const SizedBox(width: 6),
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: AppColors.toolBadgeText,
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}
