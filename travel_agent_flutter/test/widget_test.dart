import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:travel_agent_flutter/core/network/api_client.dart';
import 'package:travel_agent_flutter/main.dart';
import 'package:travel_agent_flutter/models/flight_model.dart';
import 'package:travel_agent_flutter/repositories/booking_repository.dart';
import 'package:travel_agent_flutter/repositories/flight_repository.dart';

class FakeFlightRepository extends FlightRepository {
  FakeFlightRepository() : super(apiClient: ApiClient());

  @override
  Future<List<FlightModel>> searchFlights({
    required String origin,
    required String destination,
    required DateTime departureDate,
    int passengers = 1,
    String? cabinClass,
    double? maxPrice,
    int? maxStops,
    String? preferredAirline,
    String? sortBy,
    int limit = 50,
    int offset = 0,
  }) async {
    return [
      FlightModel(
        id: 'mock-1',
        flightNumber: 'AI-559',
        airline: 'Air India',
        origin: origin,
        destination: destination,
        departureTime: departureDate,
        arrivalTime: departureDate.add(const Duration(hours: 2)),
        durationMinutes: 120,
        price: 4500.0,
      ),
    ];
  }
}

void main() {
  setUp(() {
    Get.reset();
    final apiClient = ApiClient();
    Get.put<ApiClient>(apiClient);
    Get.put<FlightRepository>(FakeFlightRepository());
    Get.put<BookingRepository>(BookingRepository(apiClient: apiClient));
  });

  testWidgets('TravelAgentApp loads HomeView with branding and search controls',
      (WidgetTester tester) async {
    await tester.pumpWidget(const TravelAgentApp());
    await tester.pumpAndSettle();

    // Verify app bar title
    expect(find.text('TravelAgent AI'), findsOneWidget);
    expect(find.text('Intelligent Flight Booking'), findsOneWidget);

    // Verify search button
    expect(find.text('Search Flights with Agent'), findsOneWidget);

    // Verify AI prompt chip
    expect(find.text('Try Asking AI Assistant'), findsOneWidget);

    // Verify Floating Action Button
    expect(find.text('Ask AI Agent'), findsOneWidget);

    // Verify mock flight card rendered
    expect(find.text('AI-559'), findsOneWidget);
  });
}
