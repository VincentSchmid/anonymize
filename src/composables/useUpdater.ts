/**
 * Composable for checking and installing app updates.
 */

import { ref } from "vue";
import { check } from "@tauri-apps/plugin-updater";
import { relaunch } from "@tauri-apps/plugin-process";
import { getVersion } from "@tauri-apps/api/app";

export interface UpdateInfo {
  version: string;
  currentVersion: string;
  body?: string;
  date?: string;
}

export function useUpdater() {
  const isChecking = ref(false);
  const isDownloading = ref(false);
  const isInstalling = ref(false);
  const downloadProgress = ref(0);
  const updateAvailable = ref(false);
  const updateInfo = ref<UpdateInfo | null>(null);
  const error = ref<string | null>(null);

  async function checkForUpdates(): Promise<boolean> {
    isChecking.value = true;
    error.value = null;
    updateAvailable.value = false;
    updateInfo.value = null;

    try {
      const currentVersion = await getVersion();
      console.log("[Updater] Current version:", currentVersion);

      const update = await check();

      if (update) {
        console.log("[Updater] Update available:", update.version);
        updateAvailable.value = true;
        updateInfo.value = {
          version: update.version,
          currentVersion,
          body: update.body,
          date: update.date,
        };
        return true;
      } else {
        console.log("[Updater] No update available");
        return false;
      }
    } catch (e) {
      console.error("[Updater] Failed to check for updates:", e);
      error.value = e instanceof Error ? e.message : String(e);
      return false;
    } finally {
      isChecking.value = false;
    }
  }

  async function downloadAndInstall(): Promise<void> {
    if (!updateAvailable.value) {
      error.value = "No update available";
      return;
    }

    isDownloading.value = true;
    downloadProgress.value = 0;
    error.value = null;

    try {
      const update = await check();
      if (!update) {
        error.value = "Update no longer available";
        return;
      }

      let totalSize = 0;
      let downloadedSize = 0;

      // Download with progress tracking
      await update.downloadAndInstall((event) => {
        switch (event.event) {
          case "Started":
            totalSize = (event.data as { contentLength?: number }).contentLength || 0;
            console.log("[Updater] Download started, size:", totalSize);
            break;
          case "Progress":
            downloadedSize += (event.data as { chunkLength: number }).chunkLength;
            if (totalSize > 0) {
              downloadProgress.value = Math.round((downloadedSize / totalSize) * 100);
            }
            break;
          case "Finished":
            console.log("[Updater] Download finished");
            isDownloading.value = false;
            isInstalling.value = true;
            break;
        }
      });

      console.log("[Updater] Update installed, relaunching...");
      await relaunch();
    } catch (e) {
      console.error("[Updater] Failed to download/install update:", e);
      error.value = e instanceof Error ? e.message : String(e);
    } finally {
      isDownloading.value = false;
      isInstalling.value = false;
    }
  }

  function dismissUpdate() {
    updateAvailable.value = false;
    updateInfo.value = null;
  }

  return {
    // State
    isChecking,
    isDownloading,
    isInstalling,
    downloadProgress,
    updateAvailable,
    updateInfo,
    error,

    // Methods
    checkForUpdates,
    downloadAndInstall,
    dismissUpdate,
  };
}
