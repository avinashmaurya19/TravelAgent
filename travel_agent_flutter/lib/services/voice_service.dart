import 'package:flutter/foundation.dart';
import 'package:get/get.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';

/// Service managing Speech-to-Text (Voice Commands) and Text-to-Speech (Agent Voice).
class VoiceService extends GetxService {
  final stt.SpeechToText _speech = stt.SpeechToText();
  final FlutterTts _tts = FlutterTts();

  // Reactive state
  final RxBool isListening = false.obs;
  final RxBool isSpeaking = false.obs;
  final RxBool isMuted = false.obs;
  final RxString recognizedText = ''.obs;
  final RxDouble soundLevel = 0.0.obs;
  final RxBool isAvailable = false.obs;

  @override
  void onInit() {
    super.onInit();
    _initSpeech();
    _initTts();
  }

  Future<void> _initSpeech() async {
    try {
      final available = await _speech.initialize(
        onStatus: (status) {
          debugPrint('[VoiceService STT Status] $status');
          if (status == 'listening') {
            isListening.value = true;
          } else if (status == 'notListening' || status == 'done') {
            isListening.value = false;
          }
        },
        onError: (error) {
          debugPrint('[VoiceService STT Error] ${error.errorMsg}');
          isListening.value = false;
        },
      );
      isAvailable.value = available;
    } catch (e) {
      debugPrint('[VoiceService STT Init Failed] $e');
      isAvailable.value = false;
    }
  }

  Future<void> _initTts() async {
    try {
      await _tts.setLanguage('en-IN');
      await _tts.setPitch(1.0);
      await _tts.setSpeechRate(0.5);

      _tts.setStartHandler(() {
        isSpeaking.value = true;
      });

      _tts.setCompletionHandler(() {
        isSpeaking.value = false;
      });

      _tts.setCancelHandler(() {
        isSpeaking.value = false;
      });

      _tts.setErrorHandler((msg) {
        debugPrint('[VoiceService TTS Error] $msg');
        isSpeaking.value = false;
      });
    } catch (e) {
      debugPrint('[VoiceService TTS Init Failed] $e');
    }
  }

  /// Start listening for voice commands from microphone.
  Future<void> startListening({Function(String finalResult)? onCompleted}) async {
    if (isSpeaking.value) {
      await stopSpeaking();
    }

    recognizedText.value = '';
    if (!isAvailable.value) {
      await _initSpeech();
    }

    if (!isAvailable.value) {
      debugPrint('[VoiceService] SpeechToText not available or permission not granted.');
      isListening.value = false;
      return;
    }

    try {
      isListening.value = true;
      await _speech.listen(
        onResult: (result) {
          recognizedText.value = result.recognizedWords;
          if (result.finalResult && result.recognizedWords.trim().isNotEmpty) {
            isListening.value = false;
            onCompleted?.call(result.recognizedWords.trim());
          }
        },
        onSoundLevelChange: (level) {
          soundLevel.value = level;
        },
        listenOptions: stt.SpeechListenOptions(
          listenMode: stt.ListenMode.confirmation,
          partialResults: true,
        ),
      );
    } catch (e) {
      debugPrint('[VoiceService] Listen error: $e');
      isListening.value = false;
    }
  }

  /// Stop microphone listening.
  Future<void> stopListening() async {
    try {
      await _speech.stop();
    } catch (_) {}
    isListening.value = false;
  }

  /// Speak synthesized agent text through speaker/headphones.
  Future<void> speak(String text) async {
    if (isMuted.value || text.trim().isEmpty) return;

    // Clean markdown symbols for cleaner pronunciation
    final clean = text
        .replaceAll(RegExp(r'\*\*|__|\*|_|#|`'), '')
        .replaceAll(RegExp(r'\[.*?\]\(.*?\)'), '')
        .trim();

    // Limit voice readout to first 2-3 sentences to keep voice punchy & conversational like ixigo Tara
    final sentences = clean.split(RegExp(r'(?<=[.!?])\s+'));
    final spokenPart = sentences.take(2).join(' ');

    try {
      isSpeaking.value = true;
      await _tts.speak(spokenPart);
    } catch (e) {
      debugPrint('[VoiceService] Speak error: $e');
      isSpeaking.value = false;
    }
  }

  /// Stop current audio playback.
  Future<void> stopSpeaking() async {
    try {
      await _tts.stop();
    } catch (_) {}
    isSpeaking.value = false;
  }

  /// Toggle mute state.
  void toggleMute() {
    isMuted.value = !isMuted.value;
    if (isMuted.value) {
      stopSpeaking();
    }
  }

  @override
  void onClose() {
    stopListening();
    stopSpeaking();
    super.onClose();
  }
}
