import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:uuid/uuid.dart';
import '../../models/agent_models.dart';
import '../../models/chat_message_model.dart';
import '../../models/flight_model.dart';
import '../../repositories/agent_repository.dart';
import '../../repositories/flight_repository.dart';
import '../../models/booking_model.dart';
import '../flights/widgets/flight_compare_sheet.dart';
import '../booking/widgets/booking_confirm_sheet.dart';
import 'widgets/agent_trace_view.dart';

/// Controller managing the AI Travel Assistant conversation, agent tool traces, and state.
class AssistantController extends GetxController {
  final FlightRepository flightRepository = Get.find<FlightRepository>();
  final AgentRepository agentRepository = Get.find<AgentRepository>();

  final textController = TextEditingController();
  final scrollController = ScrollController();
  final messages = <ChatMessage>[].obs;
  final isProcessing = false.obs;

  // Session ID for short-term memory persistence
  final String sessionId = const Uuid().v4();

  // Observability: all executed tool traces across this conversation session
  final allExecutedTraces = <ToolCallTrace>[].obs;

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
    'What is IndiGo baggage limit?',
    'What is the cancellation fee?',
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
      // 0. Extract recent non-thinking message history to preserve multi-turn context
      final historyList = messages
          .where((m) => !m.isThinking && m.content.trim().isNotEmpty)
          .map((m) => {
                'role': m.role == MessageRole.user ? 'user' : 'assistant',
                'content': m.content,
              })
          .toList();
      final recentHistory = historyList.length > 6
          ? historyList.sublist(historyList.length - 6)
          : historyList;

      // 1. Try Streaming SSE connection for live tool progress
      AgentChatResponse? agentResponse;
      try {
        final List<ToolCallTrace> intermediateTraces = [];
        await for (final event in agentRepository.chatWithAgentStream(
          message: query,
          state: travelState,
          sessionId: sessionId,
          chatHistory: recentHistory,
        )) {
          final eventType = event['event'] as String?;
          final data = event['data'];

          if (eventType == 'start') {
            final idx = messages.indexWhere((m) => m.id == thinkingMsgId);
            if (idx != -1) {
              messages[idx] = ChatMessage(
                id: thinkingMsgId,
                role: MessageRole.assistant,
                content: 'Agent analyzing query...',
                timestamp: DateTime.now(),
                isThinking: true,
              );
              messages.refresh();
            }
          } else if (eventType == 'tool_start' && data is Map<String, dynamic>) {
            final toolName = data['tool_name'] as String? ?? 'tool';
            final idx = messages.indexWhere((m) => m.id == thinkingMsgId);
            if (idx != -1) {
              messages[idx] = ChatMessage(
                id: thinkingMsgId,
                role: MessageRole.assistant,
                content: 'Executing $toolName...',
                timestamp: DateTime.now(),
                isThinking: true,
                toolTraces: intermediateTraces.isNotEmpty ? List.from(intermediateTraces) : null,
              );
              messages.refresh();
              _scrollToBottom();
            }
          } else if (eventType == 'tool_result' && data is Map<String, dynamic>) {
            final trace = ToolCallTrace.fromJson(data);
            intermediateTraces.add(trace);
            allExecutedTraces.add(trace);

            final idx = messages.indexWhere((m) => m.id == thinkingMsgId);
            if (idx != -1) {
              messages[idx] = ChatMessage(
                id: thinkingMsgId,
                role: MessageRole.assistant,
                content: 'Processing results from ${trace.toolName}...',
                timestamp: DateTime.now(),
                isThinking: true,
                toolTraces: List.from(intermediateTraces),
              );
              messages.refresh();
              _scrollToBottom();
            }
          } else if (eventType == 'assistant_message' && data is Map<String, dynamic>) {
            agentResponse = AgentChatResponse.fromJson(data);
            break;
          }
        }
      } catch (streamError) {
        debugPrint('[SSE] Streaming fallback to standard chat: $streamError');
      }

      // If stream did not complete or failed, fall back seamlessly to standard /chat
      agentResponse ??= await agentRepository.chatWithAgent(
        message: query,
        state: travelState,
        sessionId: sessionId,
        chatHistory: recentHistory,
      );

      // 2. Update local state from orchestrator's state
      travelState = agentResponse.state;
      if (travelState.origin != null) currentOrigin = travelState.origin!;
      if (travelState.destination != null) currentDestination = travelState.destination!;
      if (agentResponse.recommendedFlights.isNotEmpty) {
        lastLoadedFlights = agentResponse.recommendedFlights;
      }
      if (agentResponse.toolTrace.isNotEmpty) {
        allExecutedTraces.addAll(agentResponse.toolTrace);
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

      // 4. Trigger comparison sheet ONLY if user explicitly asked to compare or compare tool was called,
      // and NEVER when the user is trying to book.
      final isBookingIntent = lower.contains('book') || lower.contains('confirm') || lower.contains('pnr');
      final hasCompareTool = agentResponse.toolTrace.any((t) => t.toolName == 'compare_flights');
      if (!isBookingIntent && (lower.contains('compare') || hasCompareTool) && lastLoadedFlights.length >= 2) {
        Get.bottomSheet(
          FlightCompareSheet(flights: lastLoadedFlights.take(3).toList()),
          isScrollControlled: true,
          backgroundColor: Colors.white,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
        );
      }

      // 5. Trigger booking confirmation sheet if create_booking tool was invoked
      ToolCallTrace? bookingTrace;
      for (final t in agentResponse.toolTrace) {
        if (t.toolName == 'create_booking') {
          bookingTrace = t;
          break;
        }
      }

      if (bookingTrace != null && travelState.bookingId != null) {
        final bookingId = travelState.bookingId!;
        final bookingRef = travelState.bookingReference ?? '';
        final flight = agentResponse.recommendedFlights.isNotEmpty
            ? agentResponse.recommendedFlights.first
            : (lastLoadedFlights.isNotEmpty ? lastLoadedFlights.first : null);

        if (flight != null) {
          final pendingModel = BookingModel(
            id: bookingId,
            bookingReference: bookingRef,
            flightId: flight.id,
            status: BookingStatus.pending,
            baseFare: (bookingTrace.result['base_fare'] as num?)?.toDouble() ?? flight.price,
            taxAmount: (bookingTrace.result['tax_amount'] as num?)?.toDouble() ?? (flight.price * 0.18),
            baggageFee: (bookingTrace.result['baggage_fee'] as num?)?.toDouble() ?? 0.0,
            seatFee: (bookingTrace.result['seat_fee'] as num?)?.toDouble() ?? 0.0,
            totalPrice: (bookingTrace.result['total_price'] as num?)?.toDouble() ?? (flight.price * 1.18),
            passengersCount: (bookingTrace.result['passengers_count'] as int?) ?? 1,
            createdAt: DateTime.now(),
            flight: flight,
          );

          Get.bottomSheet(
            BookingConfirmSheet(
              flight: flight,
              initialPendingBooking: pendingModel,
              initialPassengerName: travelState.passengerDetails?['name'] ?? 'Passenger',
            ),
            isScrollControlled: true,
            backgroundColor: Colors.white,
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
          );
        }
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

  /// Opens developer observability sheet showing executed tools, latency, and travel state.
  void showTraceSheet() {
    Get.bottomSheet(
      AgentTraceView(
        traces: allExecutedTraces,
        travelState: travelState,
        sessionId: sessionId,
      ),
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
    );
  }
}
