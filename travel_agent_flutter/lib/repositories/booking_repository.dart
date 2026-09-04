import '../core/constants/api_endpoints.dart';
import '../core/network/api_client.dart';
import '../models/booking_model.dart';

/// Repository for creating and confirming flight bookings.
class BookingRepository {
  final ApiClient apiClient;

  BookingRepository({required this.apiClient});

  /// Create a new pending reservation awaiting explicit confirmation.
  Future<BookingModel> createPendingBooking({
    required String flightId,
    required List<PassengerModel> passengers,
    bool addExtraBaggage = false,
    String seatSelection = 'standard',
    String? contactEmail,
    String? contactPhone,
  }) async {
    final payload = {
      'flight_id': flightId,
      'passengers': passengers.map((p) => p.toJson()).toList(),
      'add_extra_baggage': addExtraBaggage,
      'seat_selection': seatSelection,
      'contact_email': contactEmail,
      'contact_phone': contactPhone,
    };

    final response = await apiClient.post<Map<String, dynamic>>(
      ApiEndpoints.bookings,
      data: payload,
    );
    return BookingModel.fromJson(response.data!);
  }

  /// Retrieve booking record by ID.
  Future<BookingModel> getBookingDetails(String bookingId) async {
    final response = await apiClient.get<Map<String, dynamic>>(
      '${ApiEndpoints.bookings}/$bookingId',
    );
    return BookingModel.fromJson(response.data!);
  }

  /// Confirm a pending booking (Human-in-the-loop confirmation step).
  Future<BookingModel> confirmBooking(String bookingId) async {
    final path = ApiEndpoints.confirmBooking.replaceAll('{id}', bookingId);
    final response = await apiClient.post<Map<String, dynamic>>(path);
    return BookingModel.fromJson(response.data!);
  }

  /// Cancel an existing booking.
  Future<Map<String, dynamic>> cancelBooking(String bookingId) async {
    final path = ApiEndpoints.cancelBooking.replaceAll('{id}', bookingId);
    final response = await apiClient.post<Map<String, dynamic>>(path);
    return response.data ?? {};
  }
}
