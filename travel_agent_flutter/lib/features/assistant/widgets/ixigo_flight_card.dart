import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../models/flight_model.dart';
import '../../flights/widgets/flight_details_sheet.dart';
import 'package:get/get.dart';

/// Premium dark-themed flight card matching the ixigo visual design.
class IxigoFlightCard extends StatelessWidget {
  final FlightModel flight;
  final bool isCheapest;
  final VoidCallback? onTap;

  const IxigoFlightCard({
    super.key,
    required this.flight,
    this.isCheapest = false,
    this.onTap,
  });

  String _formatDuration(int minutes) {
    final h = minutes ~/ 60;
    final m = minutes % 60;
    return '${h}h ${m}m';
  }

  String _formatPrice(double price) {
    return NumberFormat.currency(
      locale: 'en_IN',
      symbol: '₹',
      decimalDigits: 0,
    ).format(price);
  }

  String _getCityName(String code) {
    const map = {
      'DEL': 'New Delhi',
      'BOM': 'Mumbai',
      'BLR': 'Bengaluru',
      'GOI': 'Goa',
      'DXB': 'Dubai',
      'CCU': 'Kolkata',
      'HYD': 'Hyderabad',
      'MAA': 'Chennai',
      'PNQ': 'Pune',
      'AMD': 'Ahmedabad',
    };
    return map[code.toUpperCase()] ?? code;
  }

  Color _getAirlineColor(String airline) {
    final lower = airline.toLowerCase();
    if (lower.contains('indigo')) return const Color(0xFF1A56DB);
    if (lower.contains('air india')) return const Color(0xFFD32F2F);
    if (lower.contains('vistara')) return const Color(0xFF6A1B9A);
    if (lower.contains('spicejet')) return const Color(0xFFFF5722);
    if (lower.contains('akasa')) return const Color(0xFFFF6F00);
    if (lower.contains('emirates')) return const Color(0xFFC62828);
    return const Color(0xFF00897B);
  }

  @override
  Widget build(BuildContext context) {
    final isNextDay = flight.arrivalTime.day != flight.departureTime.day;
    final originalPrice = flight.price * 1.18;
    final lockFee = (flight.price * 0.15).roundToDouble();

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF1E222B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF2A2F3D), width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.35),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap ?? () => Get.bottomSheet(
            FlightDetailsSheet(flight: flight),
            isScrollControlled: true,
          ),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Row: Airline brand, flight code & Cheapest Pill Badge
                Row(
                  children: [
                    Container(
                      width: 28,
                      height: 28,
                      decoration: BoxDecoration(
                        color: _getAirlineColor(flight.airline).withOpacity(0.2),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Icon(
                        Icons.flight_rounded,
                        color: _getAirlineColor(flight.airline),
                        size: 16,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      flight.airline,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      flight.flightNumber,
                      style: const TextStyle(
                        color: Color(0xFF8E9BAE),
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const Spacer(),
                    if (isCheapest || flight.badge == 'Best Value' || flight.badge == 'Cheapest')
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: const Color(0xFF00E676).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: const Color(0xFF00E676).withOpacity(0.35),
                          ),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '₹',
                              style: TextStyle(
                                color: Color(0xFF00E676),
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            SizedBox(width: 3),
                            Text(
                              'CHEAPEST',
                              style: TextStyle(
                                color: Color(0xFF00E676),
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                letterSpacing: 0.5,
                              ),
                            ),
                          ],
                        ),
                      )
                    else if (flight.stops == 0)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: const Color(0xFF29B6F6).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Text(
                          'NON-STOP',
                          style: TextStyle(
                            color: Color(0xFF29B6F6),
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 14),

                // Middle Row: Departure, Route Line, Arrival
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    // Departure
                    Expanded(
                      flex: 3,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            DateFormat('HH:mm').format(flight.departureTime),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                              letterSpacing: -0.5,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(
                            '${flight.origin}- ${_getCityName(flight.origin)}',
                            style: const TextStyle(
                              color: Color(0xFF8E9BAE),
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),

                    // Duration & Route Line
                    Expanded(
                      flex: 4,
                      child: Column(
                        children: [
                          Text(
                            '${_formatDuration(flight.durationMinutes)} • ${flight.stops == 0 ? 'Non-stop' : '${flight.stops} stop'}',
                            style: const TextStyle(
                              color: Color(0xFF8E9BAE),
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Stack(
                            alignment: Alignment.center,
                            children: [
                              Container(
                                height: 1.5,
                                color: const Color(0xFF384050),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 4),
                                color: const Color(0xFF1E222B),
                                child: const Icon(
                                  Icons.flight_takeoff_rounded,
                                  color: Color(0xFF8E9BAE),
                                  size: 14,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    // Arrival
                    Expanded(
                      flex: 3,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                DateFormat('HH:mm').format(flight.arrivalTime),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 22,
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: -0.5,
                                ),
                              ),
                              if (isNextDay)
                                const Text(
                                  '+1',
                                  style: TextStyle(
                                    color: Color(0xFFFF5252),
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(height: 3),
                          Text(
                            '${_getCityName(flight.destination)} -${flight.destination}',
                            style: const TextStyle(
                              color: Color(0xFF8E9BAE),
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                const Divider(height: 1, color: Color(0xFF2C3240)),
                const SizedBox(height: 12),

                // Bottom Row: Lock Price CTA and Final Fare
                Row(
                  children: [
                    // Lock Price Pill
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFF7A00).withOpacity(0.12),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: const Color(0xFFFF7A00).withOpacity(0.35),
                        ),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.shield_outlined,
                            color: Color(0xFFFF7A00),
                            size: 14,
                          ),
                          const SizedBox(width: 5),
                          Text(
                            'Lock Price at ${_formatPrice(lockFee)} >',
                            style: const TextStyle(
                              color: Color(0xFFFF7A00),
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ],
                      ),
                    ),

                    const Spacer(),

                    // Strike-through original fare
                    Text(
                      _formatPrice(originalPrice),
                      style: const TextStyle(
                        color: Color(0xFF6C788A),
                        fontSize: 12,
                        decoration: TextDecoration.lineThrough,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(width: 8),

                    // Net bold price
                    Text(
                      _formatPrice(flight.price),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
