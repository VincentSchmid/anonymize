/**
 * Composable for managing entity configuration.
 * Handles loading/saving disabled and hidden entity types.
 */

import { ref, computed } from "vue";
import {
  readTextFile,
  writeTextFile,
  exists,
  mkdir,
  BaseDirectory,
} from "@tauri-apps/plugin-fs";
import { resourceDir } from "@tauri-apps/api/path";

export interface EntityConfig {
  disabled: string[];
  hidden: string[];
}

const CONFIG_FILENAME = "entity-config.json";

// Singleton state
const config = ref<EntityConfig>({ disabled: [], hidden: [] });
const isLoaded = ref(false);
const isLoading = ref(false);
const error = ref<string | null>(null);

export function useEntityConfig() {
  const disabledEntities = computed(() => new Set(config.value.disabled));
  const hiddenEntities = computed(() => new Set(config.value.hidden));

  async function loadConfig(): Promise<void> {
    if (isLoaded.value || isLoading.value) return;

    isLoading.value = true;
    error.value = null;

    try {
      // Check if user config exists in app data
      const userConfigExists = await exists(CONFIG_FILENAME, {
        baseDir: BaseDirectory.AppData,
      }).catch(() => false);

      if (userConfigExists) {
        // Load user config
        console.log("[EntityConfig] Loading user config from AppData");
        const content = await readTextFile(CONFIG_FILENAME, {
          baseDir: BaseDirectory.AppData,
        });
        config.value = JSON.parse(content);
      } else {
        // Load default config from resources
        console.log("[EntityConfig] Loading default config from resources");
        try {
          const resourcePath = await resourceDir();
          const content = await readTextFile(
            `${resourcePath}entity-config.json`
          );
          config.value = JSON.parse(content);
        } catch (e) {
          // Fallback to hardcoded defaults if resource not available (dev mode)
          console.log("[EntityConfig] Using hardcoded defaults");
          config.value = {
            disabled: [],
            hidden: [
              "CRYPTO",
              "IP_ADDRESS",
              "URL",
              "MEDICAL_LICENSE",
              "NRP",
              "ID",
              "AGE",
              "EMAIL",
            ],
          };
        }

        // Save to app data for future use
        await saveConfig();
      }

      console.log("[EntityConfig] Config loaded:", config.value);
      isLoaded.value = true;
    } catch (e) {
      console.error("[EntityConfig] Failed to load config:", e);
      error.value = e instanceof Error ? e.message : String(e);
      // Use empty defaults on error
      config.value = { disabled: [], hidden: [] };
    } finally {
      isLoading.value = false;
    }
  }

  async function saveConfig(): Promise<void> {
    try {
      // Ensure app data directory exists
      const appDataExists = await exists("", {
        baseDir: BaseDirectory.AppData,
      }).catch(() => false);

      if (!appDataExists) {
        await mkdir("", { baseDir: BaseDirectory.AppData, recursive: true });
      }

      await writeTextFile(CONFIG_FILENAME, JSON.stringify(config.value, null, 2), {
        baseDir: BaseDirectory.AppData,
      });
      console.log("[EntityConfig] Config saved");
    } catch (e) {
      console.error("[EntityConfig] Failed to save config:", e);
      error.value = e instanceof Error ? e.message : String(e);
    }
  }

  function isEntityDisabled(entityType: string): boolean {
    return disabledEntities.value.has(entityType);
  }

  function isEntityHidden(entityType: string): boolean {
    return hiddenEntities.value.has(entityType);
  }

  async function setEntityDisabled(
    entityType: string,
    disabled: boolean
  ): Promise<void> {
    const currentDisabled = new Set(config.value.disabled);

    if (disabled) {
      currentDisabled.add(entityType);
    } else {
      currentDisabled.delete(entityType);
    }

    config.value.disabled = Array.from(currentDisabled);
    await saveConfig();
  }

  async function toggleEntityDisabled(entityType: string): Promise<void> {
    const isCurrentlyDisabled = isEntityDisabled(entityType);
    await setEntityDisabled(entityType, !isCurrentlyDisabled);
  }

  return {
    // State
    config,
    isLoaded,
    isLoading,
    error,

    // Computed
    disabledEntities,
    hiddenEntities,

    // Methods
    loadConfig,
    saveConfig,
    isEntityDisabled,
    isEntityHidden,
    setEntityDisabled,
    toggleEntityDisabled,
  };
}
