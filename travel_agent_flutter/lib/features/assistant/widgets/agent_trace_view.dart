import 'dart:convert';
import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../models/agent_models.dart';
import '../../../../models/chat_message_model.dart';

/// Developer Observability Trace sheet showing real-time tool execution, arguments, latency, and travel state.
class AgentTraceView extends StatelessWidget {
  final List<ToolCallTrace> traces;
  final TravelStateModel travelState;
  final String sessionId;

  const AgentTraceView({
    super.key,
    required this.traces,
    required this.travelState,
    required this.sessionId,
  });

  @override
  Widget build(BuildContext context) {
    int totalMs = 0;
    for (final t in traces) {
      totalMs += t.executionTimeMs ?? 0;
    }

    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              margin: const EdgeInsets.only(top: 10, bottom: 6),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.analytics_outlined, color: AppColors.primary, size: 20),
                ),
                const SizedBox(width: 10),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Agent Observability Trace',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        'Real-time tool execution & conversational state',
                        style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          // Body
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16.0),
              children: [
                // Metrics Summary Card
                _buildMetricsCard(totalMs),
                const SizedBox(height: 16),

                // Active State Inspector
                _buildStateCard(),
                const SizedBox(height: 16),

                // Tool Execution Timeline
                const Text(
                  'Executed Tool Trace Timeline',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),

                if (traces.isEmpty)
                  _buildEmptyTraces()
                else
                  ...traces.asMap().entries.map((entry) {
                    final idx = entry.key;
                    final trace = entry.value;
                    return _buildToolTraceCard(idx + 1, trace);
                  }),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsCard(int totalMs) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.assistantBubble,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildMetricItem('Tool Calls', '${traces.length}', Icons.build_circle_outlined),
          _buildMetricItem('Total Time', '${totalMs}ms', Icons.timer_outlined),
          _buildMetricItem('Session', sessionId.substring(0, 8), Icons.fingerprint_outlined),
        ],
      ),
    );
  }

  Widget _buildMetricItem(String title, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 18, color: AppColors.primary),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
        Text(title, style: const TextStyle(color: AppColors.textSecondary, fontSize: 11)),
      ],
    );
  }

  Widget _buildStateCard() {
    final hasRoute = travelState.origin != null && travelState.destination != null;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.tune, size: 16, color: AppColors.secondary),
              SizedBox(width: 6),
              Text(
                'Active Travel Context',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: [
              _buildStateChip('Route', hasRoute ? '${travelState.origin} → ${travelState.destination}' : 'Unset'),
              if (travelState.departureDate != null)
                _buildStateChip('Date', travelState.departureDate!),
              if (travelState.maxPrice != null)
                _buildStateChip('Max Price', '₹${travelState.maxPrice!.toInt()}'),
              if (travelState.maxStops != null)
                _buildStateChip('Stops', travelState.maxStops == 0 ? 'Non-stop' : '≤${travelState.maxStops}'),
              if (travelState.preferredAirline != null)
                _buildStateChip('Airline', travelState.preferredAirline!),
              if (travelState.bookingReference != null)
                _buildStateChip('PNR', travelState.bookingReference!, isHighlight: true),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStateChip(String label, String value, {bool isHighlight = false}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isHighlight ? AppColors.accent.withValues(alpha: 0.15) : AppColors.assistantBubble,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: isHighlight ? AppColors.accent : AppColors.border),
      ),
      child: Text(
        '$label: $value',
        style: TextStyle(
          fontSize: 11,
          fontWeight: isHighlight ? FontWeight.bold : FontWeight.w500,
          color: isHighlight ? AppColors.accent : AppColors.textPrimary,
        ),
      ),
    );
  }

  Widget _buildToolTraceCard(int stepNum, ToolCallTrace trace) {
    const encoder = JsonEncoder.withIndent('  ');
    final argsStr = encoder.convert(trace.arguments);
    final resultStr = trace.result != null ? encoder.convert(trace.result) : 'None';

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      child: Material(
        color: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: const BorderSide(color: AppColors.border),
        ),
        clipBehavior: Clip.antiAlias,
        child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
        childrenPadding: const EdgeInsets.all(12),
        leading: CircleAvatar(
          radius: 12,
          backgroundColor: AppColors.primary,
          child: Text(
            '$stepNum',
            style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
          ),
        ),
        title: Text(
          trace.toolName,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: AppColors.assistantBubble,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            '${trace.executionTimeMs ?? 0}ms',
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
          ),
        ),
        children: [
          const Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Arguments:',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: AppColors.textSecondary),
            ),
          ),
          const SizedBox(height: 4),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey.shade900,
              borderRadius: BorderRadius.circular(6),
            ),
            child: SelectableText(
              argsStr,
              style: const TextStyle(fontFamily: 'monospace', fontSize: 11, color: Colors.greenAccent),
            ),
          ),
          const SizedBox(height: 8),
          const Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Result Payload:',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: AppColors.textSecondary),
            ),
          ),
          const SizedBox(height: 4),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey.shade900,
              borderRadius: BorderRadius.circular(6),
            ),
            child: SelectableText(
              resultStr,
              maxLines: 8,
              style: const TextStyle(fontFamily: 'monospace', fontSize: 11, color: Colors.lightBlueAccent),
            ),
          ),
        ],
        ),
      ),
    );
  }

  Widget _buildEmptyTraces() {
    return Container(
      padding: const EdgeInsets.all(24),
      alignment: Alignment.center,
      child: Column(
        children: [
          Icon(Icons.terminal, size: 40, color: Colors.grey.shade400),
          const SizedBox(height: 8),
          const Text(
            'No tool calls executed yet',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
          ),
          const SizedBox(height: 4),
          const Text(
            'Send a query in chat to observe the agent call deterministic travel microservices.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 11, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }
}
