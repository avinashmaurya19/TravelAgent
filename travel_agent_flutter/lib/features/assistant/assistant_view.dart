import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/theme/app_colors.dart';
import 'assistant_controller.dart';
import 'widgets/message_bubble.dart';

class AssistantView extends GetView<AssistantController> {
  const AssistantView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'AI Travel Assistant',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Text(
              'Deterministic Flight Search & Policies',
              style: TextStyle(fontSize: 11, color: AppColors.textSecondary),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            tooltip: 'Agent Architecture',
            onPressed: () {
              Get.dialog(
                AlertDialog(
                  title: const Row(
                    children: [
                      Icon(Icons.shield_outlined, color: AppColors.primary),
                      SizedBox(width: 8),
                      Text('Agentic AI Guardrails'),
                    ],
                  ),
                  content: const Text(
                    '1. Tool-Gated: LLM never accesses the DB directly.\n\n'
                    '2. Pre-Check: Availability and fares are re-calculated before booking.\n\n'
                    '3. Human-in-the-Loop: Bookings require explicit confirmation via POST /confirm.\n\n'
                    '4. Grounded RAG: Policies retrieved via FAISS embeddings.',
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Get.back(),
                      child: const Text('Got it'),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Chat message list
            Expanded(
              child: Obx(
                () => ListView.builder(
                  controller: controller.scrollController,
                  padding: const EdgeInsets.symmetric(vertical: 12.0),
                  itemCount: controller.messages.length,
                  itemBuilder: (context, index) {
                    final message = controller.messages[index];
                    return MessageBubble(message: message);
                  },
                ),
              ),
            ),

            // Quick suggestion chips
            Container(
              height: 40,
              margin: const EdgeInsets.symmetric(vertical: 4),
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: controller.quickSuggestions.length,
                separatorBuilder: (context, index) => const SizedBox(width: 8),
                itemBuilder: (context, index) {
                  final suggestion = controller.quickSuggestions[index];
                  return ActionChip(
                    label: Text(
                      suggestion,
                      style: const TextStyle(fontSize: 12),
                    ),
                    onPressed: () => controller.sendUserMessage(suggestion),
                  );
                },
              ),
            ),

            // Message Input Bar
            Container(
              padding: const EdgeInsets.all(12.0),
              decoration: const BoxDecoration(
                color: AppColors.surface,
                border: Border(top: BorderSide(color: AppColors.border)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: controller.textController,
                      decoration: const InputDecoration(
                        hintText: 'Ask for flights, cheaper options, or policies...',
                        border: InputBorder.none,
                        enabledBorder: InputBorder.none,
                        focusedBorder: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      onSubmitted: controller.sendUserMessage,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Obx(
                    () => IconButton(
                      style: IconButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                      ),
                      icon: controller.isProcessing.value
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                            )
                          : const Icon(Icons.arrow_upward, size: 20),
                      onPressed: controller.isProcessing.value
                          ? null
                          : () => controller.sendUserMessage(controller.textController.text),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
