import 'flight_model.dart';

/// Passenger details for a flight booking.
class PassengerModel {
  final String? id;
  final String firstName;
  final String lastName;
  final int age;
  final String gender;
  final String? seatNumber;

  const PassengerModel({
    this.id,
    required this.firstName,
    required this.lastName,
    required this.age,
    required this.gender,
    this.seatNumber,
  });

  factory PassengerModel.fromJson(Map<String, dynamic> json) {
    return PassengerModel(
      id: json['id'] as String?,
      firstName: json['first_name'] as String,
      lastName: json['last_name'] as String,
      age: json['age'] as int,
      gender: json['gender'] as String,
      seatNumber: json['seat_number'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'first_name': firstName,
      'last_name': lastName,
      'age': age,
      'gender': gender,
      if (seatNumber != null) 'seat_number': seatNumber,
    };
  }

  String get fullName => '$firstName $lastName';
}

/// Booking lifecycle status enum.
enum BookingStatus {
  pending,
  confirmed,
  cancelled;

  static BookingStatus fromString(String status) {
    switch (status.toUpperCase()) {
      case 'CONFIRMED':
        return BookingStatus.confirmed;
      case 'CANCELLED':
        return BookingStatus.cancelled;
      default:
        return BookingStatus.pending;
    }
  }

  String get displayName {
    switch (this) {
      case BookingStatus.pending:
        return 'Pending Confirmation';
      case BookingStatus.confirmed:
        return 'Confirmed';
      case BookingStatus.cancelled:
        return 'Cancelled';
    }
  }
}

/// Flight booking representation.
class BookingModel {
  final String id;
  final String bookingReference;
  final String flightId;
  final String? userId;
  final BookingStatus status;
  final double baseFare;
  final double taxAmount;
  final double baggageFee;
  final double seatFee;
  final double totalPrice;
  final int passengersCount;
  final String? contactEmail;
  final String? contactPhone;
  final DateTime createdAt;
  final DateTime? confirmedAt;
  final DateTime? cancelledAt;
  final List<PassengerModel> passengers;
  final FlightModel? flight;

  const BookingModel({
    required this.id,
    required this.bookingReference,
    required this.flightId,
    this.userId,
    required this.status,
    required this.baseFare,
    required this.taxAmount,
    this.baggageFee = 0.0,
    this.seatFee = 0.0,
    required this.totalPrice,
    required this.passengersCount,
    this.contactEmail,
    this.contactPhone,
    required this.createdAt,
    this.confirmedAt,
    this.cancelledAt,
    this.passengers = const [],
    this.flight,
  });

  factory BookingModel.fromJson(Map<String, dynamic> json) {
    return BookingModel(
      id: json['id'] as String,
      bookingReference: json['booking_reference'] as String,
      flightId: json['flight_id'] as String,
      userId: json['user_id'] as String?,
      status: BookingStatus.fromString(json['status'] as String? ?? 'PENDING'),
      baseFare: (json['base_fare'] as num).toDouble(),
      taxAmount: (json['tax_amount'] as num).toDouble(),
      baggageFee: (json['baggage_fee'] as num?)?.toDouble() ?? 0.0,
      seatFee: (json['seat_fee'] as num?)?.toDouble() ?? 0.0,
      totalPrice: (json['total_price'] as num).toDouble(),
      passengersCount: json['passengers_count'] as int? ?? 1,
      contactEmail: json['contact_email'] as String?,
      contactPhone: json['contact_phone'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      confirmedAt: json['confirmed_at'] != null
          ? DateTime.parse(json['confirmed_at'] as String)
          : null,
      cancelledAt: json['cancelled_at'] != null
          ? DateTime.parse(json['cancelled_at'] as String)
          : null,
      passengers: (json['passengers'] as List<dynamic>?)
              ?.map((p) => PassengerModel.fromJson(p as Map<String, dynamic>))
              .toList() ??
          [],
      flight: json['flight'] != null
          ? FlightModel.fromJson(json['flight'] as Map<String, dynamic>)
          : null,
    );
  }
}
