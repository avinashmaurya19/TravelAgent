import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/flight_model.dart';
import '../../../repositories/flight_repository.dart';
import '../../booking/widgets/booking_confirm_sheet.dart';

/// Modal bottom sheet displaying detailed fare breakdown and flight policy info.
class FlightDetailsSheet extends StatefulWidget {
  final FlightModel flight;

  const FlightDetailsSheet({super.key, required this.flight});

  @override
  State<FlightDetailsSheet> createState() => _FlightDetailsSheetState();
}

class _FlightDetailsSheetState extends State<FlightDetailsSheet> {
  final FlightRepository flightRepo = Get.find<FlightRepository>();

  bool isLoading = true;
  FareBreakdownModel? fareBreakdown;
  String? errorMessage;

  bool addExtraBaggage = false;
  String seatSelection = 'standard';
  int passengersCount = 1;

  @override
  void initState() {
    super.initState();
    _fetchFare();
  }

  Future<void> _fetchFare() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    try {
      final result = await flightRepo.calculateFareBreakdown(
        flightId: widget.flight.id,
        passengersCount: passengersCount,
        addExtraBaggage: addExtraBaggage,
        seatSelection: seatSelection,
      );
      if (mounted) {
        setState(() {
          fareBreakdown = result;
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          errorMessage = e.toString();
          isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final currencyFormat = NumberFormat('#,##,###');

    return Container(
      padding: const EdgeInsets.all(20.0),
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.85,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header handle & title
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
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${widget.flight.airline} (${widget.flight.flightNumber})',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '${widget.flight.origin} → ${widget.flight.destination} • ${widget.flight.formattedDuration}',
                    style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
          const Divider(height: 24),

          // Options: Baggage & Seat
          const Text(
            'Add-ons & Options',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
          const SizedBox(height: 8),
          SwitchListTile.adaptive(
            contentPadding: EdgeInsets.zero,
            title: const Text('Extra Check-in Baggage (+15kg)', style: TextStyle(fontSize: 14)),
            subtitle: const Text('₹1,200 per passenger', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
            value: addExtraBaggage,
            onChanged: (val) {
              setState(() => addExtraBaggage = val);
              _fetchFare();
            },
          ),
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Seat Preference', style: TextStyle(fontSize: 14)),
            trailing: DropdownButton<String>(
              value: seatSelection,
              underline: const SizedBox(),
              items: const [
                DropdownMenuItem(value: 'standard', child: Text('Standard (Free)')),
                DropdownMenuItem(value: 'extra_legroom', child: Text('Extra Legroom (+₹600)')),
                DropdownMenuItem(value: 'premium', child: Text('Premium (+₹800)')),
              ],
              onChanged: (val) {
                if (val != null) {
                  setState(() => seatSelection = val);
                  _fetchFare();
                }
              },
            ),
          ),
          const Divider(height: 20),

          // Live Fare Breakdown Section
          const Text(
            'Transparent Fare Breakdown',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
          const SizedBox(height: 12),

          if (isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(24.0),
                child: CircularProgressIndicator(),
              ),
            )
          else if (fareBreakdown != null)
            _buildBreakdownTable(fareBreakdown!, currencyFormat)
          else
            Text(errorMessage ?? 'Failed to load fare', style: const TextStyle(color: AppColors.error)),

          const Spacer(),

          // Confirm CTA
          SizedBox(
            width: double.infinity,
            height: 48,
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
                  builder: (_) => BookingConfirmSheet(
                    flight: widget.flight,
                    addExtraBaggage: addExtraBaggage,
                    seatSelection: seatSelection,
                    passengersCount: passengersCount,
                  ),
                );
              },
              child: Text(
                fareBreakdown != null
                    ? 'Proceed to Book • ₹${currencyFormat.format(fareBreakdown!.totalAmount)}'
                    : 'Proceed to Book',
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBreakdownTable(FareBreakdownModel fare, NumberFormat format) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.toolBadge,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          _row('Base Fare (${fare.passengersCount}x)', '₹${format.format(fare.totalBaseFare)}'),
          const SizedBox(height: 6),
          _row('Taxes & GST (18%)', '₹${format.format(fare.taxAmount)}'),
          if (fare.baggageFee > 0) ...[
            const SizedBox(height: 6),
            _row('Extra Baggage', '₹${format.format(fare.baggageFee)}'),
          ],
          if (fare.seatFee > 0) ...[
            const SizedBox(height: 6),
            _row('Seat Selection', '₹${format.format(fare.seatFee)}'),
          ],
          const Divider(height: 16),
          _row(
            'Total Amount',
            '₹${format.format(fare.totalAmount)}',
            isTotal: true,
          ),
        ],
      ),
    );
  }

  Widget _row(String label, String value, {bool isTotal = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: isTotal ? 15 : 13,
            fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            color: isTotal ? AppColors.textPrimary : AppColors.textSecondary,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: isTotal ? 16 : 13,
            fontWeight: isTotal ? FontWeight.bold : FontWeight.w600,
            color: isTotal ? AppColors.primary : AppColors.textPrimary,
          ),
        ),
      ],
    );
  }
}
