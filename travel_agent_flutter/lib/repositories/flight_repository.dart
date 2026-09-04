import 'package:intl/intl.dart';
import '../core/constants/api_endpoints.dart';
import '../core/network/api_client.dart';
import '../models/flight_model.dart';

/// Repository for flight search, details, availability, and fare calculation.
class FlightRepository {
  final ApiClient apiClient;

  FlightRepository({required this.apiClient});

  /// Search flights matching route, date, and user filter criteria.
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
    final dateStr = DateFormat('yyyy-MM-dd').format(departureDate);
    final queryParams = <String, dynamic>{
      'origin': origin.toUpperCase(),
      'destination': destination.toUpperCase(),
      'departure_date': dateStr,
      'passengers': passengers,
      'limit': limit,
      'offset': offset,
    };

    if (cabinClass != null) queryParams['cabin_class'] = cabinClass;
    if (maxPrice != null) queryParams['max_price'] = maxPrice;
    if (maxStops != null) queryParams['max_stops'] = maxStops;
    if (preferredAirline != null) queryParams['preferred_airline'] = preferredAirline;
    if (sortBy != null) queryParams['sort_by'] = sortBy;

    final response = await apiClient.get<List<dynamic>>(
      ApiEndpoints.flightSearch,
      queryParameters: queryParams,
    );

    if (response.data == null) return [];
    return response.data!
        .map((json) => FlightModel.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  /// Retrieve details for a specific flight by UUID or flight number.
  Future<FlightModel> getFlightDetails(String flightId) async {
    final response = await apiClient.get<Map<String, dynamic>>(
      '${ApiEndpoints.flightDetails}/$flightId',
    );
    return FlightModel.fromJson(response.data!);
  }

  /// Check remaining seat availability for a flight.
  Future<AvailabilityModel> checkAvailability(String flightId, {int passengers = 1}) async {
    final path = ApiEndpoints.flightAvailability.replaceAll('{id}', flightId);
    final response = await apiClient.get<Map<String, dynamic>>(
      path,
      queryParameters: {'passengers': passengers},
    );
    return AvailabilityModel.fromJson(response.data!);
  }

  /// Calculate itemized fare breakdown (base fare, 18% GST, baggage, seat).
  Future<FareBreakdownModel> calculateFareBreakdown({
    required String flightId,
    int passengersCount = 1,
    bool addExtraBaggage = false,
    String seatSelection = 'standard',
  }) async {
    final payload = {
      'flight_id': flightId,
      'passengers_count': passengersCount,
      'add_extra_baggage': addExtraBaggage,
      'seat_selection': seatSelection,
    };

    final response = await apiClient.post<Map<String, dynamic>>(
      ApiEndpoints.fareBreakdown,
      data: payload,
    );
    return FareBreakdownModel.fromJson(response.data!);
  }
}
