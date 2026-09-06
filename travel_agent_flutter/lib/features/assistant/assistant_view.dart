import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import 'assistant_controller.dart';
import 'widgets/message_bubble.dart';
import 'widgets/ixigo_flight_card.dart';
import 'widgets/date_fare_strip.dart';
import 'widgets/exclusive_offers_card.dart';
import 'widgets/floating_ai_dock.dart';

class AssistantView extends GetView<AssistantController> {
  const AssistantView({super.key});

  String _getCityName(String? code) {
    if (code == null) return 'Delhi';
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF10131A),
      appBar: _buildIxigoAppBar(context),
      body: SafeArea(
        child: Stack(
          children: [
            // Layer 1: Results Canvas or Conversational Stream
            Obx(() {
              final flights = controller.displayedFlights;
              final hasFlights = flights.isNotEmpty;

              if (hasFlights) {
                return _buildResultsCanvas(context);
              } else {
                return _buildInitialChatStream(context);
              }
            }),

            // Layer 2: Persistent Floating AI Co-Pilot Dock (Glowing Orb & Mic)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: FloatingAiDock(
                controller: controller,
                onToggleChatSheet: () => _showChatBottomSheet(context),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Top context header matching ixigo (e.g. New Delhi ✈ Mumbai, date, travellers).
  PreferredSizeWidget _buildIxigoAppBar(BuildContext context) {
    return AppBar(
      backgroundColor: const Color(0xFF141720),
      elevation: 0,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white, size: 20),
        onPressed: () => Get.back(),
      ),
      title: Obx(() {
        final origin = controller.currentOrigin ?? controller.travelState.origin ?? 'DEL';
        final dest = controller.currentDestination ?? controller.travelState.destination ?? 'BOM';
        final originCity = _getCityName(origin);
        final destCity = _getCityName(dest);

        final dateStr = DateFormat('d MMM').format(controller.selectedDate.value);
        final passengers = controller.travelState.passengers;
        final cabin = controller.travelState.cabinClass.capitalizeFirst ?? 'Economy';

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  '$originCity ',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                ),
                const Icon(Icons.flight_takeoff_rounded, size: 16, color: Color(0xFF8E9BAE)),
                Text(
                  ' $destCity',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                ),
              ],
            ),
            const SizedBox(height: 2),
            Text(
              '$dateStr • $passengers Traveller${passengers > 1 ? 's' : ''} • $cabin',
              style: const TextStyle(fontSize: 11, color: Color(0xFF8E9BAE)),
            ),
          ],
        );
      }),
      actions: [
        // Mode toggle: Toggle between full flight cards and chat list
        Obx(() {
          final hasFlights = controller.displayedFlights.isNotEmpty;
          if (!hasFlights) return const SizedBox.shrink();
          return IconButton(
            icon: const Icon(Icons.chat_bubble_outline_rounded, color: Colors.white, size: 20),
            tooltip: 'View Chat History',
            onPressed: () => _showChatBottomSheet(context),
          );
        }),

        // Developer Trace Sheet
        IconButton(
          icon: const Icon(Icons.analytics_outlined, color: Colors.white, size: 20),
          tooltip: 'Agent Observability Trace',
          onPressed: controller.showTraceSheet,
        ),
      ],
    );
  }

  /// Full Native Flight Results Canvas (Date Strip, Filter Pills, Dark Cards, Offers).
  Widget _buildResultsCanvas(BuildContext context) {
    return Column(
      children: [
        // 1. Horizontal Date Fare Calendar Strip
        // Obx(() {
        //   final basePrice = controller.displayedFlights.isNotEmpty
        //       ? controller.displayedFlights.first.price
        //       : 5000.0;

        //   return DateFareStrip(
        //     selectedDate: controller.selectedDate.value,
        //     basePrice: basePrice,
        //     onDateSelected: (date) => controller.selectDate(date),
        //   );
        // }),

        // // 2. Filter & Sort Horizontal Chips
        // _buildFilterBar(),

        // 3. Scrollable List of Ixigo Flight Cards + Exclusive Offers
        Expanded(
          child: Obx(() {
            final flights = controller.displayedFlights;

            return ListView.builder(
              padding: const EdgeInsets.only(top: 8, bottom: 150),
              itemCount: flights.length + 1, // +1 for the Exclusive Offers banner
              itemBuilder: (context, index) {
                // Insert Exclusive Offers carousel after the 1st flight (exact match to ixigo screenshot!)
                if (index == 1) {
                  return const Column(
                    children: [
                      ExclusiveOffersCard(),
                      // SizedBox(height:20),
                    ],
                  );
                }

                final flightIdx = index > 1 ? index - 1 : index;
                if (flightIdx >= flights.length) return const SizedBox.shrink();

                final flight = flights[flightIdx];
                final isCheapest = flightIdx == 0;

                return IxigoFlightCard(
                  flight: flight,
                  isCheapest: isCheapest,
                );
              },
            );
          }),
        ),
        SizedBox(height: 50,)
      ],
    );
  }

  /// Horizontal filter & sort pills bar.
  Widget _buildFilterBar() {
    final filters = [
      {'label': 'Filters ⫽', 'action': 'Filters'},
      {'label': 'Sort By ▾', 'action': 'Sort-by Cheapest'},
      {'label': 'Non-Stop', 'action': 'Only non-stop flights'},
      {'label': 'Airlines ▾', 'action': 'Show IndiGo flights'},
      {'label': 'Morning', 'action': 'Morning departure flights'},
    ];

    return Container(
      height: 44,
      color: const Color(0xFF141720),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        itemCount: filters.length,
        itemBuilder: (context, index) {
          final item = filters[index];
          return Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: ActionChip(
              backgroundColor: const Color(0xFF1E222B),
              side: const BorderSide(color: Color(0xFF2C3240)),
              label: Text(
                item['label']!,
                style: const TextStyle(color: Color(0xFFB0BEC5), fontSize: 12, fontWeight: FontWeight.w600),
              ),
              onPressed: () => controller.sendMessage(item['action']!),
            ),
          );
        },
      ),
    );
  }

  /// Initial Welcome and Chat Stream before flights are searched.
  Widget _buildInitialChatStream(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: Obx(
            () => ListView.builder(
              controller: controller.scrollController,
              padding: const EdgeInsets.only(top: 12, bottom: 160),
              itemCount: controller.messages.length,
              itemBuilder: (context, index) {
                final message = controller.messages[index];
                return MessageBubble(message: message);
              },
            ),
          ),
        ),
      ],
    );
  }

  /// Expandable Bottom Sheet displaying complete chat dialogue and keyboard input.
  void _showChatBottomSheet(BuildContext context) {
    Get.bottomSheet(
      Container(
        height: MediaQuery.of(context).size.height * 0.75,
        decoration: const BoxDecoration(
          color: Color(0xFF161A23),
          borderRadius: BorderRadius.only(
            topLeft: Radius.circular(20),
            topRight: Radius.circular(20),
          ),
        ),
        child: Column(
          children: [
            // Sheet Handle & Header
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: const BoxDecoration(
                border: Border(bottom: BorderSide(color: Color(0xFF252C3B))),
              ),
              child: Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Color(0xFF00E676),
                    ),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'AI Co-Pilot Dialogue',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close_rounded, color: Colors.white70, size: 20),
                    onPressed: () => Get.back(),
                  ),
                ],
              ),
            ),

            // Dialogue message history
            Expanded(
              child: Obx(
                () => ListView.builder(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: controller.messages.length,
                  itemBuilder: (context, index) {
                    final message = controller.messages[index];
                    return MessageBubble(message: message);
                  },
                ),
              ),
            ),

            // Keyboard Text Input Field
            Container(
              padding: const EdgeInsets.all(12),
              decoration: const BoxDecoration(
                color: Color(0xFF1E222B),
                border: Border(top: BorderSide(color: Color(0xFF2C3240))),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: controller.textController,
                      style: const TextStyle(color: Colors.white, fontSize: 14),
                      decoration: const InputDecoration(
                        hintText: 'Type flight search, filter, or policy question...',
                        hintStyle: TextStyle(color: Color(0xFF78909C), fontSize: 13),
                        border: InputBorder.none,
                      ),
                      onSubmitted: (val) {
                        if (val.trim().isNotEmpty) {
                          Get.back();
                          controller.sendMessage(val);
                        }
                      },
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.send_rounded, color: Color(0xFF2979FF)),
                    onPressed: () {
                      final text = controller.textController.text.trim();
                      if (text.isNotEmpty) {
                        Get.back();
                        controller.sendMessage(text);
                      }
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
    );
  }
}
