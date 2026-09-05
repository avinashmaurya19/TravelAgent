import 'package:get/get.dart';
import '../../core/network/api_client.dart';
import '../../repositories/agent_repository.dart';
import 'assistant_controller.dart';

class AssistantBinding extends Bindings {
  @override
  void dependencies() {
    if (!Get.isRegistered<AgentRepository>()) {
      Get.lazyPut<AgentRepository>(() => AgentRepository(apiClient: Get.find<ApiClient>()));
    }
    Get.lazyPut<AssistantController>(() => AssistantController());
  }
}
