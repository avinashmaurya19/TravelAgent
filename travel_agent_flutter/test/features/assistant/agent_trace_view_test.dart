import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:travel_agent_flutter/features/assistant/widgets/agent_trace_view.dart';
import 'package:travel_agent_flutter/models/agent_models.dart';
import 'package:travel_agent_flutter/models/chat_message_model.dart';

void main() {
  testWidgets('AgentTraceView renders tool executions, latency, and travel state',
      (WidgetTester tester) async {
    const traces = [
      ToolCallTrace(
        toolName: 'search_flights',
        arguments: {'origin': 'DEL', 'destination': 'BOM', 'departure_date': '2026-09-07'},
        result: {'status': 'success', 'flights_count': 5},
        executionTimeMs: 14,
      ),
      ToolCallTrace(
        toolName: 'calculate_fare',
        arguments: {'flight_id': 'mock-1', 'passengers': 1},
        result: {'total_fare': 4500.0},
        executionTimeMs: 8,
      ),
    ];

    const state = TravelStateModel(
      origin: 'DEL',
      destination: 'BOM',
      departureDate: '2026-09-07',
      maxPrice: 6000.0,
      bookingReference: 'TA78X9',
    );

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AgentTraceView(
            traces: traces,
            travelState: state,
            sessionId: 'sess-12345678-abcd',
          ),
        ),
      ),
    );

    // Verify Title and Subtitle
    expect(find.text('Agent Observability Trace'), findsOneWidget);
    expect(find.text('Real-time tool execution & conversational state'), findsOneWidget);

    // Verify Metrics Summary Card
    expect(find.text('Tool Calls'), findsOneWidget);
    expect(find.text('Total Time'), findsOneWidget);
    expect(find.text('22ms'), findsOneWidget); // 14 + 8 ms
    expect(find.text('sess-123'), findsOneWidget); // Session prefix

    // Verify Active Travel Context Chips
    expect(find.text('Route: DEL → BOM'), findsOneWidget);
    expect(find.text('Date: 2026-09-07'), findsOneWidget);
    expect(find.text('Max Price: ₹6000'), findsOneWidget);
    expect(find.text('PNR: TA78X9'), findsOneWidget);

    // Verify Tool Trace cards
    expect(find.text('search_flights'), findsOneWidget);
    expect(find.text('calculate_fare'), findsOneWidget);
    expect(find.text('14ms'), findsOneWidget);
    expect(find.text('8ms'), findsOneWidget);
  });

  testWidgets('AgentTraceView renders empty placeholder when no traces exist',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AgentTraceView(
            traces: [],
            travelState: TravelStateModel(),
            sessionId: 'empty-session-123',
          ),
        ),
      ),
    );

    expect(find.text('No tool calls executed yet'), findsOneWidget);
  });
}
