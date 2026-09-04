import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../core/theme/app_colors.dart';
import '../../models/booking_model.dart';
import 'trips_controller.dart';

class TripsView extends GetView<TripsController> {
  const TripsView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Trips & Bookings'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Search / Lookup Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Lookup Booking',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Enter your 6-character PNR reference code or booking UUID',
                      style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: controller.searchPnrController,
                            textCapitalization: TextCapitalization.characters,
                            decoration: const InputDecoration(
                              hintText: 'e.g. DELBOM99 or UUID',
                              prefixIcon: Icon(Icons.confirmation_number_outlined),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        ElevatedButton(
                          onPressed: () => controller.lookupBooking(controller.searchPnrController.text),
                          child: const Text('Search'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Loading Indicator
            Obx(() {
              if (controller.isLoading.value) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32.0),
                    child: CircularProgressIndicator(),
                  ),
                );
              }

              if (controller.errorMessage.value != null) {
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Center(
                      child: Column(
                        children: [
                          const Icon(Icons.error_outline, size: 40, color: AppColors.error),
                          const SizedBox(height: 8),
                          Text(
                            controller.errorMessage.value!,
                            style: const TextStyle(color: AppColors.error),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }

              final booking = controller.currentBooking.value;
              if (booking == null) {
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.all(40.0),
                    child: Column(
                      children: const [
                        Icon(Icons.airplane_ticket_outlined, size: 64, color: AppColors.textMuted),
                        SizedBox(height: 12),
                        Text(
                          'Search for an existing booking to view details, fare breakdown, or cancel.',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                );
              }

              return _buildBookingCard(context, booking);
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildBookingCard(BuildContext context, BookingModel booking) {
    final priceFormat = NumberFormat('#,##,###');
    final dateFormat = DateFormat('EEE, d MMM yyyy, HH:mm');

    Color statusColor;
    switch (booking.status) {
      case BookingStatus.confirmed:
        statusColor = AppColors.success;
        break;
      case BookingStatus.pending:
        statusColor = AppColors.warning;
        break;
      case BookingStatus.cancelled:
        statusColor = AppColors.error;
        break;
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('PNR Reference', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                    Text(
                      booking.bookingReference,
                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, letterSpacing: 1.2),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: statusColor),
                  ),
                  child: Text(
                    booking.status.displayName,
                    style: TextStyle(color: statusColor, fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),

            if (booking.flight != null) ...[
              Text(
                '${booking.flight!.airline} (${booking.flight!.flightNumber})',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                '${booking.flight!.origin} → ${booking.flight!.destination} • ${booking.flight!.formattedDuration}',
                style: const TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 4),
              Text(
                'Departure: ${dateFormat.format(booking.flight!.departureTime)}',
                style: const TextStyle(fontSize: 13),
              ),
              const Divider(height: 24),
            ],

            const Text('Passengers', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            ...booking.passengers.map(
              (p) => Text('• ${p.fullName} (Age ${p.age}, ${p.gender})', style: const TextStyle(fontSize: 13)),
            ),
            const Divider(height: 24),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Total Amount Paid / Due:', style: TextStyle(fontWeight: FontWeight.bold)),
                Text(
                  '₹${priceFormat.format(booking.totalPrice)}',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.primary),
                ),
              ],
            ),
            const SizedBox(height: 20),

            if (booking.status != BookingStatus.cancelled)
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.cancel_outlined, color: AppColors.error),
                  label: const Text('Cancel Booking', style: TextStyle(color: AppColors.error)),
                  style: OutlinedButton.styleFrom(side: const BorderSide(color: AppColors.error)),
                  onPressed: () {
                    Get.defaultDialog(
                      title: 'Cancel Booking?',
                      middleText: 'Are you sure you want to cancel booking ${booking.bookingReference}? Reserved seats will be released.',
                      textConfirm: 'Yes, Cancel',
                      textCancel: 'Keep Booking',
                      confirmTextColor: Colors.white,
                      buttonColor: AppColors.error,
                      onConfirm: () {
                        Get.back();
                        controller.cancelCurrentBooking();
                      },
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}
