import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/flight_model.dart';
import '../../booking/widgets/booking_confirm_sheet.dart';

/// Side-by-side comparison sheet for evaluating multiple flights.
class FlightCompareSheet extends StatelessWidget {
  final List<FlightModel> flights;

  const FlightCompareSheet({super.key, required this.flights});

  @override
  Widget build(BuildContext context) {
    final timeFormat = DateFormat('HH:mm');
    final priceFormat = NumberFormat('#,##,###');

    return Container(
      padding: const EdgeInsets.all(20.0),
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.8,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Center(
            child: Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: AppColors.border,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Flight Comparison',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Comparison columns
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: flights.map((flight) {
                  return Container(
                    width: 220,
                    margin: const EdgeInsets.only(right: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Airline & Flight Number
                        Text(
                          flight.airline,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        Text(
                          flight.flightNumber,
                          style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
                        ),
                        const Divider(height: 20),

                        // Route & Times
                        _metric('Route', '${flight.origin} → ${flight.destination}'),
                        const SizedBox(height: 8),
                        _metric(
                          'Schedule',
                          '${timeFormat.format(flight.departureTime)} - ${timeFormat.format(flight.arrivalTime)}',
                        ),
                        const SizedBox(height: 8),
                        _metric('Duration', flight.formattedDuration),
                        const SizedBox(height: 8),
                        _metric('Stops', flight.stopsText),
                        const SizedBox(height: 8),
                        _metric('Seats Left', '${flight.availableSeats}'),
                        const Divider(height: 20),

                        // Price
                        Text(
                          '₹${priceFormat.format(flight.price)}',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: AppColors.primary,
                          ),
                        ),
                        const Spacer(),

                        // CTA
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.secondary,
                            ),
                            onPressed: () {
                              Navigator.pop(context);
                              showModalBottomSheet(
                                context: context,
                                isScrollControlled: true,
                                shape: const RoundedRectangleBorder(
                                  borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                                ),
                                builder: (_) => BookingConfirmSheet(flight: flight),
                              );
                            },
                            child: const Text('Book This'),
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _metric(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
        ),
        Text(
          value,
          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }
}
