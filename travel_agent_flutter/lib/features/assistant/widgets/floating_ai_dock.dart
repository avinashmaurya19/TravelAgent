import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../assistant_controller.dart';

/// Floating AI Co-Pilot Dock featuring the glowing AI Orb and voice/keyboard interaction matching ixigo.
class FloatingAiDock extends StatefulWidget {
  final AssistantController controller;
  final VoidCallback onToggleChatSheet;

  const FloatingAiDock({
    super.key,
    required this.controller,
    required this.onToggleChatSheet,
  });

  @override
  State<FloatingAiDock> createState() => _FloatingAiDockState();
}

class _FloatingAiDockState extends State<FloatingAiDock> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  final List<String> _quickChips = [
    'Sort-by Cheapest',
    'IndiGo Only',
    'Non-Stop Only',
    'Air India Only',
    'Morning Departure',
    'Cheaper Options',
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.92, end: 1.10).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = widget.controller;

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.transparent,
            const Color(0xFF0C0E14).withOpacity(0.85),
            const Color(0xFF0C0E14),
          ],
          stops: const [0.0, 0.25, 1.0],
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 1. Quick Action Suggestion Chips
          SizedBox(
            height: 38,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 14),
              itemCount: _quickChips.length,
              itemBuilder: (context, index) {
                final label = _quickChips[index];
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: InkWell(
                    onTap: () => c.sendMessage(label),
                    borderRadius: BorderRadius.circular(20),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1B1F2A),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFF2E3547), width: 1),
                      ),
                      child: Center(
                        child: Text(
                          label,
                          style: const TextStyle(
                            color: Color(0xFFD6DFEB),
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 10),

          // 2. Main Dock Surface: Mic, Glowing AI Orb, Keyboard
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Left: Voice Input Button
                Obx(() {
                  final isListening = c.voiceService.isListening.value;
                  return IconButton(
                    onPressed: () => c.toggleVoiceListening(),
                    icon: Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isListening
                            ? const Color(0xFFFF5252).withOpacity(0.2)
                            : const Color(0xFF1E222B),
                        border: Border.all(
                          color: isListening ? const Color(0xFFFF5252) : const Color(0xFF333B4D),
                        ),
                      ),
                      child: Icon(
                        isListening ? Icons.mic_rounded : Icons.mic_none_rounded,
                        color: isListening ? const Color(0xFFFF5252) : Colors.white,
                        size: 24,
                      ),
                    ),
                  );
                }),

                // Center: Glowing Animated AI Orb & Status Text
                Obx(() {
                  final isThinking = c.isProcessing.value;
                  final isListening = c.voiceService.isListening.value;
                  final isSpeaking = c.voiceService.isSpeaking.value;

                  String statusText = 'Tap Orb to talk';
                  if (isListening) {
                    statusText = 'Listening...';
                  } else if (isThinking) {
                    statusText = 'Thinking';
                  } else if (isSpeaking) {
                    statusText = 'Speaking...';
                  }

                  return InkWell(
                    onTap: () => c.toggleVoiceListening(),
                    borderRadius: BorderRadius.circular(40),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        AnimatedBuilder(
                          animation: _pulseAnimation,
                          builder: (context, child) {
                            final scale = (isThinking || isListening || isSpeaking)
                                ? _pulseAnimation.value
                                : 1.0;

                            return Transform.scale(
                              scale: scale,
                              child: Container(
                                width: 56,
                                height: 56,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  gradient: RadialGradient(
                                    colors: isListening
                                        ? const [
                                            Color(0xFFFF7A00),
                                            Color(0xFFFF007A),
                                            Color(0xFF7A00FF),
                                          ]
                                        : (isSpeaking
                                            ? const [
                                                Color(0xFF00E5FF),
                                                Color(0xFF00E676),
                                                Color(0xFF1A237E),
                                              ]
                                            : const [
                                                Color(0xFFFF9E80),
                                                Color(0xFFFF4081),
                                                Color(0xFF7C4DFF),
                                                Color(0xFF00E5FF),
                                              ]),
                                    center: const Alignment(-0.2, -0.3),
                                    radius: 0.85,
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: isListening
                                          ? const Color(0xFFFF007A).withOpacity(0.5)
                                          : const Color(0xFF7C4DFF).withOpacity(0.45),
                                      blurRadius: 18,
                                      spreadRadius: 2,
                                    ),
                                  ],
                                ),
                                child: Container(
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    gradient: LinearGradient(
                                      begin: Alignment.topLeft,
                                      end: Alignment.bottomRight,
                                      colors: [
                                        Colors.white.withOpacity(0.35),
                                        Colors.transparent,
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                        const SizedBox(height: 6),
                        Text(
                          statusText,
                          style: TextStyle(
                            color: (isListening || isThinking || isSpeaking)
                                ? Colors.white
                                : const Color(0xFF8E9BAE),
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 0.3,
                          ),
                        ),
                      ],
                    ),
                  );
                }),

                // Right: Keyboard / Chat Input Toggle
                IconButton(
                  onPressed: widget.onToggleChatSheet,
                  icon: Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: const Color(0xFF1E222B),
                      border: Border.all(color: const Color(0xFF333B4D)),
                    ),
                    child: const Icon(
                      Icons.keyboard_alt_outlined,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),

          // 3. Sub-dock Controls: CC Transcript and Speaker Mute
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // CC Transcript Toggle
                TextButton.icon(
                  onPressed: widget.onToggleChatSheet,
                  icon: const Icon(Icons.subtitles_rounded, size: 16, color: Color(0xFF8E9BAE)),
                  label: const Text(
                    'Chat & Logs',
                    style: TextStyle(fontSize: 11, color: Color(0xFF8E9BAE)),
                  ),
                ),

                // Audio Mute Toggle
                Obx(() {
                  final isMuted = c.voiceService.isMuted.value;
                  return IconButton(
                    icon: Icon(
                      isMuted ? Icons.volume_off_rounded : Icons.volume_up_rounded,
                      color: isMuted ? const Color(0xFFFF5252) : const Color(0xFF8E9BAE),
                      size: 18,
                    ),
                    onPressed: () => c.voiceService.toggleMute(),
                  );
                }),
              ],
            ),
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}
