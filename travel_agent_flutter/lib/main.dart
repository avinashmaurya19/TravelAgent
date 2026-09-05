import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'core/network/api_client.dart';
import 'core/routes/app_pages.dart';
import 'core/theme/app_theme.dart';
import 'repositories/agent_repository.dart';
import 'repositories/booking_repository.dart';
import 'repositories/flight_repository.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize core infrastructure & repositories
  final apiClient = ApiClient();
  Get.put<ApiClient>(apiClient, permanent: true);
  Get.put<FlightRepository>(FlightRepository(apiClient: apiClient), permanent: true);
  Get.put<BookingRepository>(BookingRepository(apiClient: apiClient), permanent: true);
  Get.put<AgentRepository>(AgentRepository(apiClient: apiClient), permanent: true);

  runApp(const TravelAgentApp());
}

class TravelAgentApp extends StatelessWidget {
  const TravelAgentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'TravelAgent AI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      initialRoute: AppPages.initial,
      getPages: AppPages.routes,
      defaultTransition: Transition.cupertino,
    );
  }
}
