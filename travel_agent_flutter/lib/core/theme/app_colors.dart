import 'package:flutter/material.dart';

/// Design tokens and semantic colors for TravelAgent AI.
class AppColors {
  AppColors._();

  // Primary Branding
  static const Color primary = Color(0xFF1E3A8A); // Deep Indigo
  static const Color primaryLight = Color(0xFF3B82F6);
  static const Color primaryDark = Color(0xFF0F172A);

  // Accent & CTA
  static const Color accent = Color(0xFF0284C7); // Sky Blue
  static const Color secondary = Color(0xFFF97316); // Vibrant Orange (ixigo style)

  // Status Colors
  static const Color success = Color(0xFF059669); // Emerald
  static const Color warning = Color(0xFFD97706); // Amber
  static const Color error = Color(0xFFDC2626); // Crimson

  // Neutral Backgrounds & Surfaces
  static const Color background = Color(0xFFF8FAFC);
  static const Color surface = Colors.white;
  static const Color surfaceElevated = Color(0xFFFFFFFF);
  static const Color border = Color(0xFFE2E8F0);

  // Dark Theme Surfaces
  static const Color darkBackground = Color(0xFF0F172A);
  static const Color darkSurface = Color(0xFF1E293B);
  static const Color darkBorder = Color(0xFF334155);

  // Typography
  static const Color textPrimary = Color(0xFF0F172A);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textMuted = Color(0xFF94A3B8);

  // Assistant & Chat
  static const Color userBubble = Color(0xFF1E3A8A);
  static const Color assistantBubble = Color(0xFFF1F5F9);
  static const Color toolBadge = Color(0xFFEEF2FF);
  static const Color toolBadgeText = Color(0xFF4F46E5);
}
