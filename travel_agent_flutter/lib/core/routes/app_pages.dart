import 'package:get/get.dart';
import '../../features/assistant/assistant_binding.dart';
import '../../features/assistant/assistant_view.dart';
import '../../features/home/home_binding.dart';
import '../../features/home/home_view.dart';
import '../../features/trips/trips_binding.dart';
import '../../features/trips/trips_view.dart';
import 'app_routes.dart';

/// Centralized GetPage definitions connecting routes with views and bindings.
class AppPages {
  AppPages._();

  static const initial = AppRoutes.home;

  static final routes = [
    GetPage(
      name: AppRoutes.home,
      page: () => const HomeView(),
      binding: HomeBinding(),
      transition: Transition.fadeIn,
    ),
    GetPage(
      name: AppRoutes.assistant,
      page: () => const AssistantView(),
      binding: AssistantBinding(),
      transition: Transition.rightToLeft,
    ),
    GetPage(
      name: AppRoutes.trips,
      page: () => const TripsView(),
      binding: TripsBinding(),
      transition: Transition.rightToLeft,
    ),
  ];
}
