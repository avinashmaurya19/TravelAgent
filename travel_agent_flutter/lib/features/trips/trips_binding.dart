import 'package:get/get.dart';
import 'trips_controller.dart';

class TripsBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<TripsController>(() => TripsController());
  }
}
