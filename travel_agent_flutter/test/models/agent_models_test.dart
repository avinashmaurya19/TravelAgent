import 'package:flutter_test/flutter_test.dart';
import 'package:travel_agent_flutter/models/agent_models.dart';
import 'package:travel_agent_flutter/models/chat_message_model.dart';

void main() {
  group('TravelStateModel', () {
    test('parses json into TravelStateModel correctly', () {
      final json = {
        'origin': 'DEL',
        'destination': 'BOM',
        'departure_date': '2026-09-06',
        'passengers': 2,
        'cabin_class': 'economy',
        'max_price': 6000.0,
        'max_stops': 0,
        'preferred_airline': 'IndiGo',
        'selected_flight_id': 'flight-del-bom-1',
        'last_search_flight_ids': ['flight-del-bom-1', 'flight-del-bom-2'],
      };

      final state = TravelStateModel.fromJson(json);

      expect(state.origin, equals('DEL'));
      expect(state.destination, equals('BOM'));
      expect(state.departureDate, equals('2026-09-06'));
      expect(state.passengers, equals(2));
      expect(state.maxPrice, equals(6000.0));
      expect(state.maxStops, equals(0));
      expect(state.preferredAirline, equals('IndiGo'));
      expect(state.selectedFlightId, equals('flight-del-bom-1'));
      expect(state.lastSearchFlightIds.length, equals(2));
    });

    test('serializes TravelStateModel to JSON', () {
      const state = TravelStateModel(
        origin: 'DEL',
        destination: 'BLR',
        passengers: 1,
        maxPrice: 5500.0,
      );

      final json = state.toJson();

      expect(json['origin'], equals('DEL'));
      expect(json['destination'], equals('BLR'));
      expect(json['passengers'], equals(1));
      expect(json['max_price'], equals(5500.0));
    });
  });

  group('AgentChatResponse', () {
    test('parses full agent response with recommended flights and tool traces', () {
      final json = {
        'response': 'I found 2 flights matching your request.',
        'state': {
          'origin': 'DEL',
          'destination': 'BOM',
        },
        'recommended_flights': [
          {
            'id': 'flight-del-bom-1',
            'flight_number': '6E-204',
            'airline': 'IndiGo',
            'origin': 'DEL',
            'destination': 'BOM',
            'departure_time': '2026-09-06T08:30:00.000Z',
            'arrival_time': '2026-09-06T10:45:00.000Z',
            'duration_minutes': 135,
            'stops': 0,
            'cabin_class': 'economy',
            'price': 4500.0,
            'available_seats': 45,
          }
        ],
        'tool_trace': [
          {
            'tool_name': 'search_flights',
            'arguments': {'origin': 'DEL', 'destination': 'BOM'},
            'result': {'count': 1},
            'execution_time_ms': 12,
          }
        ],
      };

      final response = AgentChatResponse.fromJson(json);

      expect(response.response, equals('I found 2 flights matching your request.'));
      expect(response.state.origin, equals('DEL'));
      expect(response.recommendedFlights.length, equals(1));
      expect(response.recommendedFlights.first.flightNumber, equals('6E-204'));
      expect(response.toolTrace.length, equals(1));
      expect(response.toolTrace.first.toolName, equals('search_flights'));
      expect(response.toolTrace.first.executionTimeMs, equals(12));
    });
  });

  group('ChatMessage with multiple tool traces', () {
    test('allTraces returns list of toolTraces if populated', () {
      final message = ChatMessage(
        id: 'msg-1',
        role: MessageRole.assistant,
        content: 'Flights found',
        timestamp: DateTime.now(),
        toolTraces: const [
          ToolCallTrace(toolName: 'search_flights', arguments: {}),
          ToolCallTrace(toolName: 'filter_flights', arguments: {}),
        ],
      );

      expect(message.allTraces.length, equals(2));
      expect(message.allTraces[0].toolName, equals('search_flights'));
      expect(message.allTraces[1].toolName, equals('filter_flights'));
    });
  });
}
