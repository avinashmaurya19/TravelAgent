import 'chat_message_model.dart';
import 'flight_model.dart';

/// Structured conversational travel state matching backend TravelState.
class TravelStateModel {
  final String? origin;
  final String? destination;
  final String? departureDate;
  final int passengers;
  final String cabinClass;
  final double? maxPrice;
  final int? maxStops;
  final String? preferredAirline;
  final String? selectedFlightId;
  final Map<String, dynamic>? passengerDetails;
  final String? bookingId;
  final String? bookingReference;
  final List<String> lastSearchFlightIds;

  const TravelStateModel({
    this.origin,
    this.destination,
    this.departureDate,
    this.passengers = 1,
    this.cabinClass = 'economy',
    this.maxPrice,
    this.maxStops,
    this.preferredAirline,
    this.selectedFlightId,
    this.passengerDetails,
    this.bookingId,
    this.bookingReference,
    this.lastSearchFlightIds = const [],
  });

  factory TravelStateModel.fromJson(Map<String, dynamic> json) {
    return TravelStateModel(
      origin: json['origin'] as String?,
      destination: json['destination'] as String?,
      departureDate: json['departure_date'] as String?,
      passengers: json['passengers'] as int? ?? 1,
      cabinClass: json['cabin_class'] as String? ?? 'economy',
      maxPrice: (json['max_price'] as num?)?.toDouble(),
      maxStops: json['max_stops'] as int?,
      preferredAirline: json['preferred_airline'] as String?,
      selectedFlightId: json['selected_flight_id'] as String?,
      passengerDetails: json['passenger_details'] as Map<String, dynamic>?,
      bookingId: json['booking_id'] as String?,
      bookingReference: json['booking_reference'] as String?,
      lastSearchFlightIds: (json['last_search_flight_ids'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (origin != null) 'origin': origin,
      if (destination != null) 'destination': destination,
      if (departureDate != null) 'departure_date': departureDate,
      'passengers': passengers,
      'cabin_class': cabinClass,
      if (maxPrice != null) 'max_price': maxPrice,
      if (maxStops != null) 'max_stops': maxStops,
      if (preferredAirline != null) 'preferred_airline': preferredAirline,
      if (selectedFlightId != null) 'selected_flight_id': selectedFlightId,
      if (passengerDetails != null) 'passenger_details': passengerDetails,
      if (bookingId != null) 'booking_id': bookingId,
      if (bookingReference != null) 'booking_reference': bookingReference,
      'last_search_flight_ids': lastSearchFlightIds,
    };
  }

  TravelStateModel copyWith({
    String? origin,
    String? destination,
    String? departureDate,
    int? passengers,
    String? cabinClass,
    double? maxPrice,
    int? maxStops,
    String? preferredAirline,
    String? selectedFlightId,
    Map<String, dynamic>? passengerDetails,
    String? bookingId,
    String? bookingReference,
    List<String>? lastSearchFlightIds,
  }) {
    return TravelStateModel(
      origin: origin ?? this.origin,
      destination: destination ?? this.destination,
      departureDate: departureDate ?? this.departureDate,
      passengers: passengers ?? this.passengers,
      cabinClass: cabinClass ?? this.cabinClass,
      maxPrice: maxPrice ?? this.maxPrice,
      maxStops: maxStops ?? this.maxStops,
      preferredAirline: preferredAirline ?? this.preferredAirline,
      selectedFlightId: selectedFlightId ?? this.selectedFlightId,
      passengerDetails: passengerDetails ?? this.passengerDetails,
      bookingId: bookingId ?? this.bookingId,
      bookingReference: bookingReference ?? this.bookingReference,
      lastSearchFlightIds: lastSearchFlightIds ?? this.lastSearchFlightIds,
    );
  }
}

/// Agent orchestrator chat response containing synthesized text, updated state, and tool trace.
class AgentChatResponse {
  final String response;
  final TravelStateModel state;
  final List<FlightModel> recommendedFlights;
  final List<ToolCallTrace> toolTrace;

  const AgentChatResponse({
    required this.response,
    required this.state,
    this.recommendedFlights = const [],
    this.toolTrace = const [],
  });

  factory AgentChatResponse.fromJson(Map<String, dynamic> json) {
    final stateJson = json['state'] as Map<String, dynamic>? ?? {};
    final flightsJson = json['recommended_flights'] as List<dynamic>? ?? [];
    final tracesJson = json['tool_trace'] as List<dynamic>? ?? [];

    return AgentChatResponse(
      response: json['response'] as String? ?? '',
      state: TravelStateModel.fromJson(stateJson),
      recommendedFlights: flightsJson
          .map((f) => FlightModel.fromJson(f as Map<String, dynamic>))
          .toList(),
      toolTrace: tracesJson
          .map((t) => ToolCallTrace.fromJson(t as Map<String, dynamic>))
          .toList(),
    );
  }
}
