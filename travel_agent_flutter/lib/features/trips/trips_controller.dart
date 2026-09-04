import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../models/booking_model.dart';
import '../../repositories/booking_repository.dart';

class TripsController extends GetxController {
  final BookingRepository bookingRepository = Get.find<BookingRepository>();

  final searchPnrController = TextEditingController();
  final currentBooking = Rxn<BookingModel>();
  final isLoading = false.obs;
  final errorMessage = RxnString();

  @override
  void onClose() {
    searchPnrController.dispose();
    super.onClose();
  }

  Future<void> lookupBooking(String idOrPnr) async {
    final clean = idOrPnr.trim();
    if (clean.isEmpty) return;

    try {
      isLoading.value = true;
      errorMessage.value = null;
      final booking = await bookingRepository.getBookingDetails(clean);
      currentBooking.value = booking;
    } catch (e) {
      errorMessage.value = e.toString();
      currentBooking.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> cancelCurrentBooking() async {
    if (currentBooking.value == null) return;

    try {
      isLoading.value = true;
      await bookingRepository.cancelBooking(currentBooking.value!.id);
      // Reload updated details
      await lookupBooking(currentBooking.value!.id);
      Get.snackbar(
        'Booking Cancelled',
        'Your reservation has been cancelled and seats released.',
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      Get.snackbar(
        'Cancellation Failed',
        e.toString(),
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      isLoading.value = false;
    }
  }
}
