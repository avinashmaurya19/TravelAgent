import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../core/routes/app_routes.dart';
import '../../core/theme/app_colors.dart';
import '../assistant/widgets/flight_card.dart';
import 'home_controller.dart';

class HomeView extends GetView<HomeController> {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.flight_takeoff, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'TravelAgent AI',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                Text(
                  'Intelligent Flight Booking',
                  style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.luggage_outlined),
            tooltip: 'My Trips',
            onPressed: () => Get.toNamed(AppRoutes.trips),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Search Card
            _buildSearchCard(context),
            const SizedBox(height: 24),

            // AI Prompt Shortcuts Section
            _buildPromptShortcuts(),
            const SizedBox(height: 24),

            // Today's Top Routes / Flight Results
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Available Flights',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Obx(
                  () => controller.isLoading.value
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : TextButton.icon(
                          icon: const Icon(Icons.refresh, size: 16),
                          label: const Text('Refresh'),
                          onPressed: controller.loadSampleFlights,
                        ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildFlightsList(),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.auto_awesome),
        label: const Text('Ask AI Agent'),
        onPressed: () => Get.toNamed(AppRoutes.assistant),
      ),
    );
  }

  Widget _buildSearchCard(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: AppColors.border),
      ),
      child: Padding(
        padding: const EdgeInsets.all(18.0),
        child: Column(
          children: [
            // Origin & Destination with Swap Button
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: controller.originController,
                    textCapitalization: TextCapitalization.characters,
                    decoration: const InputDecoration(
                      labelText: 'From',
                      prefixIcon: Icon(Icons.flight_takeoff, color: AppColors.primary),
                      hintText: 'DEL',
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.swap_horiz, color: AppColors.primary),
                  onPressed: controller.swapAirports,
                ),
                Expanded(
                  child: TextField(
                    controller: controller.destinationController,
                    textCapitalization: TextCapitalization.characters,
                    decoration: const InputDecoration(
                      labelText: 'To',
                      prefixIcon: Icon(Icons.flight_land, color: AppColors.accent),
                      hintText: 'BOM',
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Date & Passengers Row
            Row(
              children: [
                Expanded(
                  child: Obx(
                    () => OutlinedButton.icon(
                      icon: const Icon(Icons.calendar_month_outlined, size: 18),
                      label: Text(
                        DateFormat('EEE, d MMM').format(controller.departureDate.value),
                        style: const TextStyle(fontSize: 14),
                      ),
                      onPressed: () async {
                        final picked = await showDatePicker(
                          context: context,
                          initialDate: controller.departureDate.value,
                          firstDate: DateTime.now(),
                          lastDate: DateTime.now().add(const Duration(days: 60)),
                        );
                        if (picked != null) {
                          controller.setDate(picked);
                        }
                      },
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Obx(
                    () => OutlinedButton.icon(
                      icon: const Icon(Icons.person_outline, size: 18),
                      label: Text(
                        '${controller.passengers.value} Passenger',
                        style: const TextStyle(fontSize: 14),
                      ),
                      onPressed: () {
                        if (controller.passengers.value >= 4) {
                          controller.passengers.value = 1;
                        } else {
                          controller.passengers.value++;
                        }
                      },
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Search Flights Button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.search),
                label: const Text('Search Flights with Agent'),
                onPressed: controller.searchFlights,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPromptShortcuts() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.tips_and_updates_outlined, size: 18, color: AppColors.secondary),
            const SizedBox(width: 8),
            const Text(
              'Try Asking AI Assistant',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: controller.promptChips.map((chip) {
            return ActionChip(
              avatar: const Icon(Icons.auto_awesome, size: 14, color: AppColors.primary),
              label: Text(chip['label'] as String),
              onPressed: () => controller.openAssistantWithPrompt(chip['query'] as String),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildFlightsList() {
    return Obx(() {
      if (controller.isLoading.value && controller.recentFlights.isEmpty) {
        return const Center(
          child: Padding(
            padding: EdgeInsets.all(32.0),
            child: CircularProgressIndicator(),
          ),
        );
      }

      if (controller.recentFlights.isEmpty) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Center(
              child: Column(
                children: [
                  const Icon(Icons.flight_outlined, size: 48, color: AppColors.textMuted),
                  const SizedBox(height: 8),
                  Text(
                    controller.errorMessage.value ?? 'No flights found for selected route/date.',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: AppColors.textSecondary),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: controller.loadSampleFlights,
                    child: const Text('Try Again'),
                  ),
                ],
              ),
            ),
          ),
        );
      }

      return ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: controller.recentFlights.length,
        separatorBuilder: (context, index) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final flight = controller.recentFlights[index];
          return FlightCard(flight: flight);
        },
      );
    });
  }
}
