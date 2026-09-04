import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../../core/routes/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/booking_model.dart';
import '../../../models/flight_model.dart';

/// Modal sub-view presenting human-in-the-loop pending booking confirmation.
class BookingPendingView extends StatelessWidget {
  final BookingModel booking;
  final FlightModel flight;
  final String passengerName;
  final bool isSubmitting;
  final String? errorMessage;
  final VoidCallback onConfirm;
  final VoidCallback onCancel;

  const BookingPendingView({
    super.key,
    required this.booking,
    required this.flight,
    required this.passengerName,
    required this.isSubmitting,
    this.errorMessage,
    required this.onConfirm,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    final priceFormat = NumberFormat('#,##,###');

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
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
        const Row(
          children: [
            Icon(Icons.shield_outlined, color: AppColors.warning, size: 24),
            SizedBox(width: 8),
            Text(
              'Explicit Confirmation Required',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 8),
        const Text(
          'In accordance with AI Safety Protocols, booking is in PENDING status. Please confirm your reservation below.',
          style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
        ),
        const Divider(height: 24),

        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.border),
          ),
          child: Column(
            children: [
              _infoRow('Reference PNR', booking.bookingReference),
              const SizedBox(height: 8),
              _infoRow('Flight', '${flight.airline} (${flight.flightNumber})'),
              const SizedBox(height: 8),
              _infoRow('Passenger', passengerName),
              const SizedBox(height: 8),
              _infoRow('Total Payable', '₹${priceFormat.format(booking.totalPrice)}', isBold: true),
            ],
          ),
        ),
        const SizedBox(height: 24),

        if (errorMessage != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 16.0),
            child: Text(errorMessage!, style: const TextStyle(color: AppColors.error)),
          ),

        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: onCancel,
                child: const Text('Cancel'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.success),
                onPressed: isSubmitting ? null : onConfirm,
                child: isSubmitting
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                      )
                    : const Text('Confirm & Book'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _infoRow(String label, String value, {bool isBold = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
        Text(
          value,
          style: TextStyle(
            fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
            fontSize: isBold ? 15 : 13,
            color: isBold ? AppColors.primary : AppColors.textPrimary,
          ),
        ),
      ],
    );
  }
}

/// Modal sub-view displaying confirmed booking PNR and navigation actions.
class BookingSuccessView extends StatelessWidget {
  final BookingModel confirmed;

  const BookingSuccessView({super.key, required this.confirmed});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
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
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: const BoxDecoration(color: AppColors.toolBadge, shape: BoxShape.circle),
          child: const Icon(Icons.check_circle, color: AppColors.success, size: 56),
        ),
        const SizedBox(height: 16),
        const Text('Booking Confirmed!', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        Text(
          'PNR: ${confirmed.bookingReference}',
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.primary),
        ),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          height: 48,
          child: ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Get.toNamed(AppRoutes.trips);
            },
            child: const Text('View in My Trips'),
          ),
        ),
        const SizedBox(height: 12),
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Back to Search'),
        ),
      ],
    );
  }
}
