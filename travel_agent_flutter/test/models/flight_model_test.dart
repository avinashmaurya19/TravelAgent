import 'package:flutter_test/flutter_test.dart';
import 'package:travel_agent_flutter/models/flight_model.dart';
import 'package:travel_agent_flutter/models/booking_model.dart';

void main() {
  group('FlightModel Serialization', () {
    final sampleJson = {
      'id': 'test-uuid-123',
      'flight_number': '6E-204',
      'airline': 'IndiGo',
      'origin': 'DEL',
      'destination': 'BOM',
      'departure_time': '2026-09-05T08:00:00.000Z',
      'arrival_time': '2026-09-05T10:15:00.000Z',
      'duration_minutes': 135,
      'stops': 0,
      'cabin_class': 'economy',
      'price': 4500.0,
      'available_seats': 80,
      'badge': 'Best Overall',
      'ranking_explanation': 'Top composite score across price and duration',
      'ranking_score': 0.15,
    };

    test('parses json correctly into FlightModel', () {
      final flight = FlightModel.fromJson(sampleJson);

      expect(flight.id, equals('test-uuid-123'));
      expect(flight.flightNumber, equals('6E-204'));
      expect(flight.airline, equals('IndiGo'));
      expect(flight.origin, equals('DEL'));
      expect(flight.destination, equals('BOM'));
      expect(flight.durationMinutes, equals(135));
      expect(flight.formattedDuration, equals('2h 15m'));
      expect(flight.stopsText, equals('Non-stop'));
      expect(flight.price, equals(4500.0));
      expect(flight.availableSeats, equals(80));
      expect(flight.badge, equals('Best Overall'));
      expect(flight.rankingExplanation, equals('Top composite score across price and duration'));
      expect(flight.rankingScore, equals(0.15));
    });

    test('serializes FlightModel to JSON correctly', () {
      final flight = FlightModel.fromJson(sampleJson);
      final json = flight.toJson();

      expect(json['flight_number'], equals('6E-204'));
      expect(json['origin'], equals('DEL'));
      expect(json['destination'], equals('BOM'));
      expect(json['price'], equals(4500.0));
      expect(json['badge'], equals('Best Overall'));
      expect(json['ranking_explanation'], equals('Top composite score across price and duration'));
      expect(json['ranking_score'], equals(0.15));
    });
  });

  group('FareBreakdownModel Serialization', () {
    final sampleFare = {
      'flight_id': 'flight-123',
      'flight_number': 'AI-559',
      'airline': 'Air India',
      'passengers_count': 2,
      'base_fare_per_passenger': 4000.0,
      'total_base_fare': 8000.0,
      'tax_rate_percentage': 18.0,
      'tax_amount': 1440.0,
      'baggage_fee': 2400.0,
      'seat_fee': 1200.0,
      'total_amount': 13040.0,
      'currency': 'INR',
    };

    test('parses fare breakdown json', () {
      final fare = FareBreakdownModel.fromJson(sampleFare);

      expect(fare.flightNumber, equals('AI-559'));
      expect(fare.passengersCount, equals(2));
      expect(fare.totalBaseFare, equals(8000.0));
      expect(fare.taxAmount, equals(1440.0));
      expect(fare.baggageFee, equals(2400.0));
      expect(fare.seatFee, equals(1200.0));
      expect(fare.totalAmount, equals(13040.0));
    });
  });

  group('BookingModel Serialization', () {
    final sampleBooking = {
      'id': 'booking-uuid-789',
      'booking_reference': 'DELBOM42',
      'flight_id': 'flight-123',
      'status': 'PENDING',
      'base_fare': 4500.0,
      'tax_amount': 810.0,
      'baggage_fee': 0.0,
      'seat_fee': 0.0,
      'total_price': 5310.0,
      'passengers_count': 1,
      'created_at': '2026-09-05T10:00:00.000Z',
      'passengers': [
        {
          'first_name': 'Amit',
          'last_name': 'Sharma',
          'age': 28,
          'gender': 'Male',
        }
      ],
    };

    test('parses booking JSON into model', () {
      final booking = BookingModel.fromJson(sampleBooking);

      expect(booking.bookingReference, equals('DELBOM42'));
      expect(booking.status, equals(BookingStatus.pending));
      expect(booking.totalPrice, equals(5310.0));
      expect(booking.passengers.length, equals(1));
      expect(booking.passengers.first.fullName, equals('Amit Sharma'));
    });
  });
}
