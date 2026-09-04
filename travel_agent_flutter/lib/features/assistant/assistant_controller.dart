import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:uuid/uuid.dart';
import '../../models/chat_message_model.dart';
import '../../models/flight_model.dart';
import '../../repositories/flight_repository.dart';
import '../flights/widgets/flight_compare_sheet.dart';

class AssistantController extends GetxController {
  final FlightRepository flightRepository = Get.find<FlightRepository>();

  final textController = TextEditingController();
  final scrollController = ScrollController();
  final messages = <ChatMessage>[].obs;
  final isProcessing = false.obs;

  // Active conversational state
  String currentOrigin = 'DEL';
  String currentDestination = 'BOM';
  DateTime currentDate = DateTime.now().add(const Duration(days: 1));
  List<FlightModel> lastLoadedFlights = [];

  final List<String> quickSuggestions = [
    'Show cheaper flights',
    'Only non-stop flights',
    'Compare top 2 flights',
    'What about Air India?',
  ];

  @override
  void onInit() {
    super.onInit();
    _initChat();
  }

  @override
  void onClose() {
    textController.dispose();
    scrollController.dispose();
    super.onClose();
  }

  void _initChat() {
    // Add introductory welcome message from assistant
    messages.add(
      ChatMessage(
        id: const Uuid().v4(),
        role: MessageRole.assistant,
        content: 'Hello! I am your AI Travel Agent. Tell me where you would like to fly, your budget, or any travel policy questions you have.',
        timestamp: DateTime.now(),
      ),
    );

    // Check if launched with initial prompt
    if (Get.arguments != null && Get.arguments is Map) {
      final args = Get.arguments as Map;
      if (args['origin'] != null) currentOrigin = args['origin'] as String;
      if (args['destination'] != null) currentDestination = args['destination'] as String;
      if (args['date'] != null) currentDate = args['date'] as DateTime;

      if (args['initialPrompt'] != null) {
        final prompt = args['initialPrompt'] as String;
        sendUserMessage(prompt);
      }
    }
  }

  Future<void> sendUserMessage(String text) async {
    final query = text.trim();
    if (query.isEmpty) return;

    textController.clear();

    // 1. Append User Message
    final userMsg = ChatMessage(
      id: const Uuid().v4(),
      role: MessageRole.user,
      content: query,
      timestamp: DateTime.now(),
    );
    messages.add(userMsg);
    _scrollToBottom();

    // 2. Append Thinking Indicator
    final thinkingMsgId = const Uuid().v4();
    final thinkingMsg = ChatMessage(
      id: thinkingMsgId,
      role: MessageRole.assistant,
      content: '',
      timestamp: DateTime.now(),
      isThinking: true,
    );
    messages.add(thinkingMsg);
    isProcessing.value = true;
    _scrollToBottom();

    // 3. Process query using deterministic services
    await _handleQuery(query, thinkingMsgId);
    isProcessing.value = false;
    _scrollToBottom();
  }

  Future<void> _handleQuery(String query, String thinkingMsgId) async {
    final lower = query.toLowerCase();
    final stopwatch = Stopwatch()..start();

    try {
      // Comparison intent
      if (lower.contains('compare') && lastLoadedFlights.length >= 2) {
        stopwatch.stop();
        messages.removeWhere((m) => m.id == thinkingMsgId);

        messages.add(
          ChatMessage(
            id: const Uuid().v4(),
            role: MessageRole.assistant,
            content: 'Here is a side-by-side comparison of the top options:',
            timestamp: DateTime.now(),
            toolTrace: ToolCallTrace(
              toolName: 'compare_flights',
              arguments: {'count': 2},
              executionTimeMs: stopwatch.elapsedMilliseconds,
            ),
          ),
        );

        // Open bottom sheet comparison
        Get.bottomSheet(
          FlightCompareSheet(flights: lastLoadedFlights.take(3).toList()),
          isScrollControlled: true,
          backgroundColor: Colors.white,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
        );
        return;
      }

      // Check if user asked for non-stop
      int? maxStops;
      if (lower.contains('non-stop') || lower.contains('nonstop') || lower.contains('direct')) {
        maxStops = 0;
      }

      // Check if user asked for airline
      String? airline;
      if (lower.contains('air india')) airline = 'Air India';
      if (lower.contains('indigo')) airline = 'IndiGo';
      if (lower.contains('spicejet')) airline = 'SpiceJet';

      // Check for cheaper filter
      String sortBy = 'price_asc';
      double? maxPrice;
      if (lower.contains('under') || lower.contains('below') || lower.contains('cheap')) {
        final regex = RegExp(r'(\d+[\d,.]*)');
        final match = regex.firstMatch(lower);
        if (match != null) {
          final priceClean = match.group(1)!.replaceAll(',', '');
          maxPrice = double.tryParse(priceClean);
        }
      }

      // Execute flight search tool
      final results = await flightRepository.searchFlights(
        origin: currentOrigin,
        destination: currentDestination,
        departureDate: currentDate,
        maxStops: maxStops,
        preferredAirline: airline,
        maxPrice: maxPrice,
        sortBy: sortBy,
        limit: 5,
      );

      stopwatch.stop();
      lastLoadedFlights = results;

      // Replace thinking message with result
      messages.removeWhere((m) => m.id == thinkingMsgId);

      if (results.isEmpty) {
        messages.add(
          ChatMessage(
            id: const Uuid().v4(),
            role: MessageRole.assistant,
            content: 'I searched flights from $currentOrigin to $currentDestination but could not find any matching your exact filters. Try relaxing price or stop constraints.',
            timestamp: DateTime.now(),
            toolTrace: ToolCallTrace(
              toolName: 'search_flights',
              arguments: {'origin': currentOrigin, 'destination': currentDestination},
              executionTimeMs: stopwatch.elapsedMilliseconds,
            ),
          ),
        );
      } else {
        messages.add(
          ChatMessage(
            id: const Uuid().v4(),
            role: MessageRole.assistant,
            content: 'Found ${results.length} flight(s) from $currentOrigin to $currentDestination. Here are the best options ranked for you:',
            timestamp: DateTime.now(),
            recommendedFlights: results,
            toolTrace: ToolCallTrace(
              toolName: 'search_flights',
              arguments: {
                'origin': currentOrigin,
                'destination': currentDestination,
                'date': currentDate.toIso8601String().split('T')[0],
              },
              executionTimeMs: stopwatch.elapsedMilliseconds,
            ),
          ),
        );
      }
    } catch (e) {
      messages.removeWhere((m) => m.id == thinkingMsgId);
      messages.add(
        ChatMessage(
          id: const Uuid().v4(),
          role: MessageRole.assistant,
          content: 'Sorry, I encountered an error while searching flights: $e',
          timestamp: DateTime.now(),
        ),
      );
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (scrollController.hasClients) {
        scrollController.animateTo(
          scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }
}
