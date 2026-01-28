/**
 * Composable for anonymization functionality.
 */

import { ref, computed, watch } from "vue";
import api, {
  type AnonymizeResponse,
  type EntityInfo,
  type DetectedEntity,
} from "@/lib/api";
import { useEntityConfig } from "./useEntityConfig";

export type AnonymizationStyle = "replace" | "mask" | "hash" | "redact";

export interface EditableEntity extends DetectedEntity {
  id: string;
  excluded: boolean;
  originalType: string;
}

let entityIdCounter = 0;
function generateEntityId(): string {
  return `entity-${++entityIdCounter}`;
}

export function useAnonymizer() {
  const entityConfig = useEntityConfig();

  const inputText = ref("");
  const result = ref<AnonymizeResponse | null>(null);
  const allEntities = ref<EntityInfo[]>([]); // All entities from API
  const enabledEntities = ref<Set<string>>(new Set());
  const anonymizationStyle = ref<AnonymizationStyle>("replace");
  const scoreThreshold = ref(0.5);
  const isLoading = ref(false);
  const isLoadingEntities = ref(false);
  const error = ref<string | null>(null);

  // Editable entities state
  const editedEntities = ref<EditableEntity[]>([]);

  // Filtered entities (excluding hidden ones)
  const entities = computed(() =>
    allEntities.value.filter((e) => !entityConfig.isEntityHidden(e.type))
  );

  const hasInput = computed(() => inputText.value.trim().length > 0);
  const hasResult = computed(() => result.value !== null);
  const hasEdits = computed(() =>
    editedEntities.value.some(
      (e) => e.excluded || e.entity_type !== e.originalType
    )
  );

  // Initialize editedEntities when result changes
  watch(result, (newResult) => {
    if (newResult) {
      editedEntities.value = newResult.entities.map((e) => ({
        ...e,
        id: generateEntityId(),
        excluded: false,
        originalType: e.entity_type,
      }));
    } else {
      editedEntities.value = [];
    }
  });

  // Generate anonymized text client-side based on edits
  const computedAnonymizedText = computed(() => {
    if (!result.value) return "";

    const activeEntities = editedEntities.value
      .filter((e) => !e.excluded)
      .sort((a, b) => b.start - a.start); // Process from end to start

    let text = result.value.original_text;
    for (const entity of activeEntities) {
      const replacement = getReplacementText(
        entity.entity_type,
        anonymizationStyle.value
      );
      text = text.slice(0, entity.start) + replacement + text.slice(entity.end);
    }
    return text;
  });

  function getReplacementText(
    entityType: string,
    style: AnonymizationStyle
  ): string {
    switch (style) {
      case "replace":
        return `<${entityType}>`;
      case "mask":
        return "*".repeat(8);
      case "hash":
        // Simple deterministic hash for display
        return `#${entityType.slice(0, 4).toUpperCase()}`;
      case "redact":
        return "[REDACTED]";
      default:
        return `<${entityType}>`;
    }
  }

  const swissEntities = computed(() =>
    entities.value.filter((e) => e.is_swiss)
  );

  const standardEntities = computed(() =>
    entities.value.filter((e) => !e.is_swiss)
  );

  async function loadEntities() {
    console.log("[useAnonymizer] loadEntities called");
    isLoadingEntities.value = true;
    try {
      // Load entity config first
      await entityConfig.loadConfig();

      const response = await api.getEntities();
      console.log("[useAnonymizer] Entities loaded:", response.entities.length, response.entities.map(e => e.type));
      allEntities.value = response.entities;

      // Enable entities that are not in the disabled list
      const enabledSet = new Set<string>();
      for (const entity of response.entities) {
        if (!entityConfig.isEntityDisabled(entity.type) && !entityConfig.isEntityHidden(entity.type)) {
          enabledSet.add(entity.type);
        }
      }
      enabledEntities.value = enabledSet;
      console.log("[useAnonymizer] Enabled entities:", Array.from(enabledEntities.value));
      console.log("[useAnonymizer] Hidden entities:", Array.from(entityConfig.hiddenEntities.value));
      console.log("[useAnonymizer] Disabled entities:", Array.from(entityConfig.disabledEntities.value));
    } catch (e) {
      console.error("[useAnonymizer] Failed to load entities:", e);
      error.value = e instanceof Error ? e.message : String(e);
    } finally {
      isLoadingEntities.value = false;
    }
  }

  async function toggleEntity(entityType: string) {
    const isCurrentlyEnabled = enabledEntities.value.has(entityType);

    if (isCurrentlyEnabled) {
      enabledEntities.value.delete(entityType);
    } else {
      enabledEntities.value.add(entityType);
    }
    // Trigger reactivity
    enabledEntities.value = new Set(enabledEntities.value);

    // Save to config (disabled = not enabled)
    await entityConfig.setEntityDisabled(entityType, isCurrentlyEnabled);
  }

  async function enableAllEntities() {
    enabledEntities.value = new Set(entities.value.map((e) => e.type));
    // Clear all disabled in config
    for (const entity of entities.value) {
      await entityConfig.setEntityDisabled(entity.type, false);
    }
  }

  async function disableAllEntities() {
    enabledEntities.value = new Set();
    // Mark all as disabled in config
    for (const entity of entities.value) {
      await entityConfig.setEntityDisabled(entity.type, true);
    }
  }

  function isEntityEnabled(entityType: string): boolean {
    return enabledEntities.value.has(entityType);
  }

  async function anonymize() {
    if (!hasInput.value) {
      error.value = "Please enter some text to anonymize";
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.anonymize({
        text: inputText.value,
        enabled_entities: Array.from(enabledEntities.value),
        anonymization_style: anonymizationStyle.value,
        score_threshold: scoreThreshold.value,
      });
      result.value = response;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
      result.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  function clear() {
    inputText.value = "";
    result.value = null;
    error.value = null;
    editedEntities.value = [];
  }

  function excludeEntity(id: string) {
    const entity = editedEntities.value.find((e) => e.id === id);
    if (entity) {
      // Apply to all entities with the same text
      const textToMatch = entity.text.toLowerCase();
      for (const e of editedEntities.value) {
        if (e.text.toLowerCase() === textToMatch) {
          e.excluded = true;
        }
      }
    }
  }

  function includeEntity(id: string) {
    const entity = editedEntities.value.find((e) => e.id === id);
    if (entity) {
      // Apply to all entities with the same text
      const textToMatch = entity.text.toLowerCase();
      for (const e of editedEntities.value) {
        if (e.text.toLowerCase() === textToMatch) {
          e.excluded = false;
        }
      }
    }
  }

  function reclassifyEntity(id: string, newType: string) {
    const entity = editedEntities.value.find((e) => e.id === id);
    if (entity) {
      // Apply to all entities with the same text
      const textToMatch = entity.text.toLowerCase();
      for (const e of editedEntities.value) {
        if (e.text.toLowerCase() === textToMatch) {
          e.entity_type = newType;
        }
      }
    }
  }

  function resetEdits() {
    if (result.value) {
      editedEntities.value = result.value.entities.map((e) => ({
        ...e,
        id: generateEntityId(),
        excluded: false,
        originalType: e.entity_type,
      }));
    }
  }

  function addManualEntity(selectedText: string, entityType: string) {
    if (!result.value || !selectedText.trim()) return;

    const originalText = result.value.original_text;
    const searchText = selectedText.toLowerCase();

    // Find all occurrences of the selected text
    const occurrences: Array<{ start: number; end: number }> = [];
    let searchStart = 0;

    while (true) {
      const index = originalText.toLowerCase().indexOf(searchText, searchStart);
      if (index === -1) break;

      occurrences.push({
        start: index,
        end: index + selectedText.length,
      });
      searchStart = index + 1;
    }

    // Filter out occurrences that overlap with existing entities
    const newOccurrences = occurrences.filter((occ) => {
      return !editedEntities.value.some(
        (e) =>
          (occ.start >= e.start && occ.start < e.end) ||
          (occ.end > e.start && occ.end <= e.end) ||
          (occ.start <= e.start && occ.end >= e.end)
      );
    });

    // Create new entities for each occurrence
    const newEntities: EditableEntity[] = newOccurrences.map((occ) => ({
      entity_type: entityType,
      text: originalText.slice(occ.start, occ.end),
      start: occ.start,
      end: occ.end,
      score: 1.0, // Manual classification has full confidence
      id: generateEntityId(),
      excluded: false,
      originalType: entityType,
    }));

    // Add to editedEntities and re-sort by position
    editedEntities.value = [...editedEntities.value, ...newEntities].sort(
      (a, b) => a.start - b.start
    );

    return newEntities.length;
  }

  function setInputText(text: string) {
    inputText.value = text;
    result.value = null;
    error.value = null;
  }

  function getEntityColor(entityType: string): string {
    const colors: Record<string, string> = {
      PERSON: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
      EMAIL_ADDRESS:
        "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
      PHONE_NUMBER:
        "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
      LOCATION:
        "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
      DATE_TIME:
        "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
      CH_AHV: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
      CH_PHONE:
        "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
      CH_POSTAL_CODE:
        "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
      CH_IBAN: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
      IBAN_CODE:
        "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
    };
    return (
      colors[entityType] ||
      "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
    );
  }

  return {
    // State
    inputText,
    result,
    entities,
    enabledEntities,
    anonymizationStyle,
    scoreThreshold,
    isLoading,
    isLoadingEntities,
    error,
    editedEntities,

    // Computed
    hasInput,
    hasResult,
    hasEdits,
    swissEntities,
    standardEntities,
    computedAnonymizedText,

    // Methods
    loadEntities,
    toggleEntity,
    enableAllEntities,
    disableAllEntities,
    isEntityEnabled,
    anonymize,
    clear,
    setInputText,
    getEntityColor,
    excludeEntity,
    includeEntity,
    reclassifyEntity,
    resetEdits,
    addManualEntity,
  };
}
