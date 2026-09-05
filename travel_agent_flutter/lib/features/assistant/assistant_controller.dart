import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:uuid/uuid.dart';
import '../../models/agent_models.dart';
import '../../models/chat_message_model.dart';
import '../../models/flight_model.dart';
import '../../repositories/agent_repository.dart';
import '../../repositories/flight_repository.dart';
import '../flights/widgets/flight_compare_sheet.dart';

/// Controller managing the AI Travel Assistant conversation, agent tool traces, and state.
class AssistantController extends GetxController {
  final FlightRepository flightRepository = Get.find<FlightRepository>();
  final AgentRepository agentRepository = Get.find<AgentRepository>();

  final textController = TextEditingController();
  final scrollController = ScrollController();
  final messages = <ChatMessage>[].obs;
  final isProcessing = false.obs;

  // Active conversational state
  String? currentOrigin;
  String? currentDestination;
  DateTime currentDate = DateTime.now().add(const Duration(days: 1));
  List<FlightModel> lastLoadedFlights = [];
  TravelStateModel travelState = const TravelStateModel();

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

      travelState = travelState.copyWith(
        origin: currentOrigin,
        destination: currentDestination,
        departureDate: currentDate.toIso8601String().split('T')[0],
      );

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

    // 3. Process query using Agent Orchestrator
    await _handleQuery(query, thinkingMsgId);
    isProcessing.value = false;
    _scrollToBottom();
  }

  Future<void> _handleQuery(String query, String thinkingMsgId) async {
    final lower = query.toLowerCase();

    try {
      // 1. Send query and current conversational state to Agent Orchestrator
      final agentResponse = await agentRepository.chatWithAgent(
        message: query,
        state: travelState,
      );

      // 2. Update local state from orchestrator's state
      travelState = agentResponse.state;
      if (travelState.origin != null) currentOrigin = travelState.origin!;
      if (travelState.destination != null) currentDestination = travelState.destination!;
      if (agentResponse.recommendedFlights.isNotEmpty) {
        lastLoadedFlights = agentResponse.recommendedFlights;
      }

      // 3. Remove thinking message and add assistant response
      messages.removeWhere((m) => m.id == thinkingMsgId);
      messages.add(
        ChatMessage(
          id: const Uuid().v4(),
          role: MessageRole.assistant,
          content: agentResponse.response,
          timestamp: DateTime.now(),
          recommendedFlights: agentResponse.recommendedFlights.isNotEmpty
              ? agentResponse.recommendedFlights
              : null,
          toolTraces: agentResponse.toolTrace.isNotEmpty
              ? agentResponse.toolTrace
              : null,
        ),
      );

      // 4. Trigger comparison sheet if user specifically requested comparison
      if (lower.contains('compare') && lastLoadedFlights.length >= 2) {
        Get.bottomSheet(
          FlightCompareSheet(flights: lastLoadedFlights.take(3).toList()),
          isScrollControlled: true,
          backgroundColor: Colors.white,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
        );
      }
    } catch (e) {
      // Graceful fallback to deterministic local search if backend agent fails
      await _fallbackSearch(query, thinkingMsgId, e.toString());
    }
  }

  Future<void> _fallbackSearch(String query, String thinkingMsgId, String error) async {
    final lower = query.toLowerCase();
    final stopwatch = Stopwatch()..start();

    try {
      int? maxStops;
      if (lower.contains('non-stop') || lower.contains('nonstop') || lower.contains('direct')) {
        maxStops = 0;
      }

      String? airline;
      if (lower.contains('air india')) airline = 'Air India';
      if (lower.contains('indigo')) airline = 'IndiGo';
      if (lower.contains('spicejet')) airline = 'SpiceJet';

      double? maxPrice;
      if (lower.contains('under') || lower.contains('below') || lower.contains('cheap')) {
        final regex = RegExp(r'(\d+[\d,.]*)');
        final match = regex.firstMatch(lower);
        if (match != null) {
          final priceClean = match.group(1)!.replaceAll(',', '');
          maxPrice = double.tryParse(priceClean);
        }
      }

      final origin = currentOrigin ?? 'DEL';
      final destination = currentDestination ?? 'BOM';

      final results = await flightRepository.searchFlights(
        origin: origin,
        destination: destination,
        departureDate: currentDate,
        maxStops: maxStops,
        preferredAirline: airline,
        maxPrice: maxPrice,
        sortBy: 'price_asc',
        limit: 5,
      );

      stopwatch.stop();
      lastLoadedFlights = results;

      messages.removeWhere((m) => m.id == thinkingMsgId);
      messages.add(
        ChatMessage(
          id: const Uuid().v4(),
          role: MessageRole.assistant,
          content: results.isEmpty
              ? 'I searched flights from $origin to $destination but could not find matching flights.'
              : 'Found ${results.length} flight(s) from $origin to $destination:',
          timestamp: DateTime.now(),
          recommendedFlights: results.isNotEmpty ? results : null,
          toolTrace: ToolCallTrace(
            toolName: 'search_flights',
            arguments: {'origin': origin, 'destination': destination},
            executionTimeMs: stopwatch.elapsedMilliseconds,
          ),
        ),
      );
    } catch (fallbackErr) {
      messages.removeWhere((m) => m.id == thinkingMsgId);
      messages.add(
        ChatMessage(
          id: const Uuid().v4(),
          role: MessageRole.assistant,
          content: 'Unable to connect to the agent service: $error',
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
