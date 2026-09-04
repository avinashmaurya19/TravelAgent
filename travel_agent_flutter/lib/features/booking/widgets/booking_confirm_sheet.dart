import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/booking_model.dart';
import '../../../models/flight_model.dart';
import '../../../repositories/booking_repository.dart';
import '../../../repositories/flight_repository.dart';
import 'booking_status_views.dart';

/// Human-in-the-Loop booking confirmation sheet.
/// Re-verifies seat availability and fare before creating a pending reservation,
/// and requires explicit user confirmation before finalizing.
class BookingConfirmSheet extends StatefulWidget {
  final FlightModel flight;
  final bool addExtraBaggage;
  final String seatSelection;
  final int passengersCount;

  const BookingConfirmSheet({
    super.key,
    required this.flight,
    this.addExtraBaggage = false,
    this.seatSelection = 'standard',
    this.passengersCount = 1,
  });

  @override
  State<BookingConfirmSheet> createState() => _BookingConfirmSheetState();
}

class _BookingConfirmSheetState extends State<BookingConfirmSheet> {
  final FlightRepository flightRepo = Get.find<FlightRepository>();
  final BookingRepository bookingRepo = Get.find<BookingRepository>();

  final _firstNameController = TextEditingController(text: 'John');
  final _lastNameController = TextEditingController(text: 'Doe');
  final _ageController = TextEditingController(text: '30');
  final _emailController = TextEditingController(text: 'john.doe@example.com');
  final _phoneController = TextEditingController(text: '+919876543210');
  String _gender = 'Male';

  bool _isChecking = true;
  bool _isSubmitting = false;
  String? _errorMessage;
  AvailabilityModel? _availability;
  FareBreakdownModel? _fare;
  BookingModel? _pendingBooking;
  BookingModel? _confirmedBooking;

  @override
  void initState() {
    super.initState();
    _preFlightCheck();
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _ageController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  /// Double-check availability and live fare breakdown before confirmation
  Future<void> _preFlightCheck() async {
    setState(() {
      _isChecking = true;
      _errorMessage = null;
    });

    try {
      final avail = await flightRepo.checkAvailability(
        widget.flight.id,
        passengers: widget.passengersCount,
      );
      final fare = await flightRepo.calculateFareBreakdown(
        flightId: widget.flight.id,
        passengersCount: widget.passengersCount,
        addExtraBaggage: widget.addExtraBaggage,
        seatSelection: widget.seatSelection,
      );

      if (mounted) {
        setState(() {
          _availability = avail;
          _fare = fare;
          _isChecking = false;
          if (!avail.isAvailable) {
            _errorMessage = 'Only ${avail.availableSeats} seat(s) remaining.';
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isChecking = false;
        });
      }
    }
  }

  /// Step 1: Create pending booking reservation
  Future<void> _createPendingBooking() async {
    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final passenger = PassengerModel(
        firstName: _firstNameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        age: int.tryParse(_ageController.text.trim()) ?? 25,
        gender: _gender,
      );

      final pending = await bookingRepo.createPendingBooking(
        flightId: widget.flight.id,
        passengers: [passenger],
        addExtraBaggage: widget.addExtraBaggage,
        seatSelection: widget.seatSelection,
        contactEmail: _emailController.text.trim(),
        contactPhone: _phoneController.text.trim(),
      );

      if (mounted) {
        setState(() {
          _pendingBooking = pending;
          _isSubmitting = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isSubmitting = false;
        });
      }
    }
  }

  /// Step 2: Finalize booking (Human-in-the-loop explicit confirmation)
  Future<void> _confirmBooking() async {
    if (_pendingBooking == null) return;

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    try {
      final confirmed = await bookingRepo.confirmBooking(_pendingBooking!.id);
      if (mounted) {
        setState(() {
          _confirmedBooking = confirmed;
          _isSubmitting = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isSubmitting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20.0),
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.9,
      ),
      child: _confirmedBooking != null
          ? BookingSuccessView(confirmed: _confirmedBooking!)
          : _pendingBooking != null
              ? BookingPendingView(
                  booking: _pendingBooking!,
                  flight: widget.flight,
                  passengerName: '${_firstNameController.text} ${_lastNameController.text}',
                  isSubmitting: _isSubmitting,
                  errorMessage: _errorMessage,
                  onConfirm: _confirmBooking,
                  onCancel: () => Navigator.pop(context),
                )
              : _buildPassengerFormView(),
    );
  }

  Widget _buildPassengerFormView() {
    final priceFormat = NumberFormat('#,##,###');

    return SingleChildScrollView(
      child: Column(
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
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Passenger & Contact Details',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '${widget.flight.airline} ${widget.flight.flightNumber} • ${widget.flight.origin} → ${widget.flight.destination}',
                    style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                ],
              ),
              IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(context)),
            ],
          ),
          const Divider(height: 24),

          if (_isChecking)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 12),
                    Text('Double-checking seat availability & fare...'),
                  ],
                ),
              ),
            )
          else ...[
            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: AppColors.error.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: AppColors.error, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: AppColors.error, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),

            // Form inputs
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _firstNameController,
                    decoration: const InputDecoration(labelText: 'First Name'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _lastNameController,
                    decoration: const InputDecoration(labelText: 'Last Name'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _ageController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Age'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    initialValue: _gender,
                    decoration: const InputDecoration(labelText: 'Gender'),
                    items: const [
                      DropdownMenuItem(value: 'Male', child: Text('Male')),
                      DropdownMenuItem(value: 'Female', child: Text('Female')),
                      DropdownMenuItem(value: 'Other', child: Text('Other')),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => _gender = val);
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(labelText: 'Contact Email'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _phoneController,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(labelText: 'Contact Phone'),
            ),
            const SizedBox(height: 20),

            // Total summary
            if (_fare != null)
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.toolBadge,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Total Amount', style: TextStyle(fontWeight: FontWeight.bold)),
                        Text('Includes 18% GST & selected add-ons', style: TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                      ],
                    ),
                    Text(
                      '₹${priceFormat.format(_fare!.totalAmount)}',
                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.primary),
                    ),
                  ],
                ),
              ),
            const SizedBox(height: 20),

            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                onPressed: _isSubmitting || (_availability != null && !_availability!.isAvailable)
                    ? null
                    : _createPendingBooking,
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('Review & Finalize Booking'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
