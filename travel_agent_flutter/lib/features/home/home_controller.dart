import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/routes/app_routes.dart';
import '../../models/flight_model.dart';
import '../../repositories/flight_repository.dart';

class HomeController extends GetxController {
  final FlightRepository flightRepository = Get.find<FlightRepository>();

  // Search input state
  final originController = TextEditingController(text: 'DEL');
  final destinationController = TextEditingController(text: 'BOM');
  final departureDate = Rx<DateTime>(DateTime.now().add(const Duration(days: 1)));
  final passengers = 1.obs;
  final cabinClass = 'economy'.obs;

  // Loading & search results
  final isLoading = false.obs;
  final recentFlights = <FlightModel>[].obs;
  final errorMessage = RxnString();

  final List<Map<String, dynamic>> promptChips = [
    {
      'label': '✈️ Delhi to Mumbai tomorrow',
      'origin': 'DEL',
      'destination': 'BOM',
      'query': 'Find flights from Delhi to Mumbai tomorrow morning under ₹5,000'
    },
    {
      'label': '🏖️ Delhi to Goa weekend',
      'origin': 'DEL',
      'destination': 'GOI',
      'query': 'Show me non-stop flights from Delhi to Goa this weekend'
    },
    {
      'label': '💼 Bangalore to Delhi non-stop',
      'origin': 'BLR',
      'destination': 'DEL',
      'query': 'Find the fastest non-stop flight from Bangalore to Delhi'
    },
    {
      'label': '🧳 IndiGo baggage allowance?',
      'query': 'What is the check-in and cabin baggage policy for IndiGo?'
    },
  ];

  @override
  void onInit() {
    super.onInit();
    loadSampleFlights();
  }

  @override
  void onClose() {
    originController.dispose;
    destinationController.dispose;
    super.onClose();
  }

  void setDate(DateTime date) {
    departureDate.value = date;
  }

  void swapAirports() {
    final temp = originController.text;
    originController.text = destinationController.text;
    destinationController.text = temp;
  }

  Future<void> loadSampleFlights() async {
    try {
      isLoading.value = true;
      errorMessage.value = null;
      final results = await flightRepository.searchFlights(
        origin: originController.text.trim(),
        destination: destinationController.text.trim(),
        departureDate: departureDate.value,
        passengers: passengers.value,
        limit: 5,
      );
      recentFlights.assignAll(results);
    } catch (e) {
      errorMessage.value = e.toString();
    } finally {
      isLoading.value = false;
    }
  }

  void searchFlights() {
    Get.toNamed(
      AppRoutes.assistant,
      arguments: {
        'initialPrompt':
            'Find flights from ${originController.text} to ${destinationController.text} on ${departureDate.value.toIso8601String().split("T")[0]} for ${passengers.value} passenger(s)',
        'origin': originController.text,
        'destination': destinationController.text,
        'date': departureDate.value,
      },
    );
  }

  void openAssistantWithPrompt(String prompt) {
    Get.toNamed(
      AppRoutes.assistant,
      arguments: {'initialPrompt': prompt},
    );
  }
}
