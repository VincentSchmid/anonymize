/**
 * Composable for managing the sidecar backend status.
 */

import { ref, onMounted, onUnmounted } from "vue";
import { invoke } from "@tauri-apps/api/core";

export interface BackendStatus {
  running: boolean;
  healthy: boolean;
  url: string;
}

export function useSidecar() {
  const status = ref<BackendStatus>({
    running: false,
    healthy: false,
    url: "http://127.0.0.1:14200",
  });
  const isLoading = ref(true);
  const error = ref<string | null>(null);

  let healthCheckInterval: ReturnType<typeof setInterval> | null = null;

  async function checkHealth() {
    try {
      const result = await invoke<BackendStatus>("check_backend_health");
      status.value = result;
      error.value = null;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
      status.value.healthy = false;
    }
  }

  async function startBackend() {
    isLoading.value = true;
    error.value = null;
    try {
      const result = await invoke<BackendStatus>("start_backend");
      status.value = result;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
    } finally {
      isLoading.value = false;
    }
  }

  async function stopBackend() {
    try {
      await invoke("stop_backend");
      status.value.running = false;
      status.value.healthy = false;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
    }
  }

  function getBackendUrl(): string {
    return status.value.url;
  }

  onMounted(async () => {
    // Initial health check
    await checkHealth();
    isLoading.value = false;

    // Set up periodic health checks
    healthCheckInterval = setInterval(checkHealth, 5000);
  });

  onUnmounted(() => {
    if (healthCheckInterval) {
      clearInterval(healthCheckInterval);
    }
  });

  return {
    status,
    isLoading,
    error,
    startBackend,
    stopBackend,
    checkHealth,
    getBackendUrl,
  };
}
