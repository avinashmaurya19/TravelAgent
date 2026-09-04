/// Flight data models representing inventory, fare breakdowns, and availability.
library;

class FlightModel {
  final String id;
  final String flightNumber;
  final String airline;
  final String origin;
  final String destination;
  final DateTime departureTime;
  final DateTime arrivalTime;
  final int durationMinutes;
  final int stops;
  final List<dynamic>? stopsDetails;
  final String cabinClass;
  final double price;
  final int availableSeats;

  const FlightModel({
    required this.id,
    required this.flightNumber,
    required this.airline,
    required this.origin,
    required this.destination,
    required this.departureTime,
    required this.arrivalTime,
    required this.durationMinutes,
    this.stops = 0,
    this.stopsDetails,
    this.cabinClass = 'economy',
    required this.price,
    this.availableSeats = 100,
  });

  factory FlightModel.fromJson(Map<String, dynamic> json) {
    return FlightModel(
      id: json['id'] as String,
      flightNumber: json['flight_number'] as String,
      airline: json['airline'] as String,
      origin: json['origin'] as String,
      destination: json['destination'] as String,
      departureTime: DateTime.parse(json['departure_time'] as String),
      arrivalTime: DateTime.parse(json['arrival_time'] as String),
      durationMinutes: json['duration_minutes'] as int,
      stops: json['stops'] as int? ?? 0,
      stopsDetails: json['stops_details'] as List<dynamic>?,
      cabinClass: json['cabin_class'] as String? ?? 'economy',
      price: (json['price'] as num).toDouble(),
      availableSeats: json['available_seats'] as int? ?? 100,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'flight_number': flightNumber,
      'airline': airline,
      'origin': origin,
      'destination': destination,
      'departure_time': departureTime.toIso8601String(),
      'arrival_time': arrivalTime.toIso8601String(),
      'duration_minutes': durationMinutes,
      'stops': stops,
      'stops_details': stopsDetails,
      'cabin_class': cabinClass,
      'price': price,
      'available_seats': availableSeats,
    };
  }

  String get formattedDuration {
    final hours = durationMinutes ~/ 60;
    final mins = durationMinutes % 60;
    return '${hours}h ${mins}m';
  }

  String get stopsText {
    if (stops == 0) return 'Non-stop';
    if (stops == 1) return '1 Stop';
    return '$stops Stops';
  }
}

class FareBreakdownModel {
  final String flightId;
  final String flightNumber;
  final String airline;
  final int passengersCount;
  final double baseFarePerPassenger;
  final double totalBaseFare;
  final double taxRatePercentage;
  final double taxAmount;
  final double baggageFee;
  final double seatFee;
  final double totalAmount;
  final String currency;

  const FareBreakdownModel({
    required this.flightId,
    required this.flightNumber,
    required this.airline,
    required this.passengersCount,
    required this.baseFarePerPassenger,
    required this.totalBaseFare,
    this.taxRatePercentage = 18.0,
    required this.taxAmount,
    this.baggageFee = 0.0,
    this.seatFee = 0.0,
    required this.totalAmount,
    this.currency = 'INR',
  });

  factory FareBreakdownModel.fromJson(Map<String, dynamic> json) {
    return FareBreakdownModel(
      flightId: json['flight_id'] as String,
      flightNumber: json['flight_number'] as String,
      airline: json['airline'] as String,
      passengersCount: json['passengers_count'] as int,
      baseFarePerPassenger: (json['base_fare_per_passenger'] as num).toDouble(),
      totalBaseFare: (json['total_base_fare'] as num).toDouble(),
      taxRatePercentage: (json['tax_rate_percentage'] as num?)?.toDouble() ?? 18.0,
      taxAmount: (json['tax_amount'] as num).toDouble(),
      baggageFee: (json['baggage_fee'] as num?)?.toDouble() ?? 0.0,
      seatFee: (json['seat_fee'] as num?)?.toDouble() ?? 0.0,
      totalAmount: (json['total_amount'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'INR',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'flight_id': flightId,
      'flight_number': flightNumber,
      'airline': airline,
      'passengers_count': passengersCount,
      'base_fare_per_passenger': baseFarePerPassenger,
      'total_base_fare': totalBaseFare,
      'tax_rate_percentage': taxRatePercentage,
      'tax_amount': taxAmount,
      'baggage_fee': baggageFee,
      'seat_fee': seatFee,
      'total_amount': totalAmount,
      'currency': currency,
    };
  }
}

class AvailabilityModel {
  final String flightId;
  final int availableSeats;
  final int requestedPassengers;
  final bool isAvailable;
  final String message;

  const AvailabilityModel({
    required this.flightId,
    required this.availableSeats,
    required this.requestedPassengers,
    required this.isAvailable,
    required this.message,
  });

  factory AvailabilityModel.fromJson(Map<String, dynamic> json) {
    return AvailabilityModel(
      flightId: json['flight_id'] as String,
      availableSeats: json['available_seats'] as int,
      requestedPassengers: json['requested_passengers'] as int,
      isAvailable: json['is_available'] as bool,
      message: json['message'] as String,
    );
  }
}
