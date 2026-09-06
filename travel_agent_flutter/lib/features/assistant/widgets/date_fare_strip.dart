import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

/// Horizontal Date Fare Calendar Strip matching the ixigo header design.
class DateFareStrip extends StatelessWidget {
  final DateTime selectedDate;
  final double basePrice;
  final ValueChanged<DateTime> onDateSelected;
  final VoidCallback? onCalendarTap;

  const DateFareStrip({
    super.key,
    required this.selectedDate,
    required this.basePrice,
    required this.onDateSelected,
    this.onCalendarTap,
  });

  @override
  Widget build(BuildContext context) {
    final monthStr = DateFormat('MMM').format(selectedDate).toUpperCase();

    // Generate surrounding 7 days: 2 days before, selected day, 4 days after
    final days = List.generate(7, (i) {
      final d = selectedDate.add(Duration(days: i - 1));
      // Calculate realistic simulated price variation for surrounding days
      final delta = ((i * 37 + d.day * 13) % 5 - 2) * 200;
      final price = (basePrice > 0 ? basePrice : 5500.0) + delta;
      return {'date': d, 'price': price.clamp(3200.0, 18000.0)};
    });

    // Find lowest price among the days to highlight in green
    final minPrice = days.map((e) => e['price'] as double).reduce((a, b) => a < b ? a : b);

    return Container(
      height: 62,
      color: const Color(0xFF14171F),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      child: Row(
        children: [
          // Month Label
          RotatedBox(
            quarterTurns: 3,
            child: Text(
              monthStr,
              style: const TextStyle(
                color: Color(0xFF6C788A),
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
          ),
          const SizedBox(width: 8),

          // Scrollable Days List
          Expanded(
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: days.length,
              itemBuilder: (context, index) {
                final item = days[index];
                final d = item['date'] as DateTime;
                final price = item['price'] as double;
                final isSelected = d.year == selectedDate.year &&
                    d.month == selectedDate.month &&
                    d.day == selectedDate.day;
                final isLowest = price == minPrice;

                final dayName = DateFormat('E').format(d);
                final dayNum = d.day;
                final formattedPrice = NumberFormat.currency(
                  locale: 'en_IN',
                  symbol: '₹',
                  decimalDigits: 0,
                ).format(price);

                return InkWell(
                  onTap: () => onDateSelected(d),
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      border: Border(
                        bottom: BorderSide(
                          color: isSelected ? Colors.white : Colors.transparent,
                          width: 2.5,
                        ),
                      ),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '$dayName, $dayNum',
                          style: TextStyle(
                            color: isSelected ? Colors.white : const Color(0xFF8E9BAE),
                            fontSize: 11,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          formattedPrice,
                          style: TextStyle(
                            color: isLowest
                                ? const Color(0xFF00E676)
                                : (isSelected ? Colors.white : const Color(0xFFB0BEC5)),
                            fontSize: 12,
                            fontWeight: isSelected || isLowest ? FontWeight.w800 : FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          // Calendar Picker Icon Button
          IconButton(
            icon: const Icon(
              Icons.calendar_month_outlined,
              color: Color(0xFF8E9BAE),
              size: 20,
            ),
            onPressed: onCalendarTap ?? () async {
              final picked = await showDatePicker(
                context: context,
                initialDate: selectedDate,
                firstDate: DateTime.now(),
                lastDate: DateTime.now().add(const Duration(days: 90)),
                builder: (context, child) {
                  return Theme(
                    data: Theme.of(context).copyWith(
                      colorScheme: const ColorScheme.dark(
                        primary: Color(0xFF2979FF),
                        surface: Color(0xFF1E222B),
                      ),
                    ),
                    child: child!,
                  );
                },
              );
              if (picked != null) {
                onDateSelected(picked);
              }
            },
          ),
        ],
      ),
    );
  }
}
