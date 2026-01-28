<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import Button from "@/components/ui/button.vue";
import Card from "@/components/ui/card.vue";
import EntityEditPopover from "@/components/EntityEditPopover.vue";
import type { AnonymizeResponse } from "@/lib/api";
import type { EditableEntity } from "@/composables/useAnonymizer";
import { Copy, Download, Check, Tag } from "lucide-vue-next";
import { save } from "@tauri-apps/plugin-dialog";
import { writeTextFile } from "@tauri-apps/plugin-fs";

interface Props {
  result: AnonymizeResponse;
  editedEntities: EditableEntity[];
  computedAnonymizedText: string;
  hasEdits: boolean;
  availableTypes: string[];
  getEntityColor: (entityType: string) => string;
}

const props = defineProps<Props>();

// Debug logging
console.log("[ResultViewer] Mounted with availableTypes:", props.availableTypes);
watch(
  () => props.availableTypes,
  (types) => console.log("[ResultViewer] availableTypes changed:", types),
  { immediate: true }
);

const emit = defineEmits<{
  exclude: [id: string];
  include: [id: string];
  reclassify: [id: string, newType: string];
  resetEdits: [];
  addManualEntity: [text: string, entityType: string];
}>();

const copied = ref(false);
const originalTextRef = ref<HTMLElement | null>(null);

// Selection state
const selectionText = ref("");
const selectionMenuPosition = ref({ x: 0, y: 0 });
const showSelectionMenu = ref(false);

const activeEntityCount = computed(() =>
  props.editedEntities.filter((e) => !e.excluded).length
);

const excludedCount = computed(() =>
  props.editedEntities.filter((e) => e.excluded).length
);

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(props.computedAnonymizedText);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (e) {
    console.error("Failed to copy:", e);
  }
}

async function downloadResult() {
  try {
    const filePath = await save({
      defaultPath: "anonymized.txt",
      filters: [
        { name: "Text Files", extensions: ["txt"] },
        { name: "All Files", extensions: ["*"] },
      ],
    });

    if (filePath) {
      await writeTextFile(filePath, props.computedAnonymizedText);
    }
  } catch (e) {
    console.error("Failed to save file:", e);
  }
}

// Handle text selection
function handleMouseUp() {
  // Small delay to ensure selection is complete
  setTimeout(() => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) {
      return;
    }

    const text = selection.toString().trim();
    if (!text || text.length < 2) {
      return;
    }

    selectionText.value = text;

    // Position menu near the selection
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    selectionMenuPosition.value = {
      x: rect.left + rect.width / 2,
      y: rect.bottom + 8,
    };
    showSelectionMenu.value = true;
  }, 10);
}

function handleClassifySelection(entityType: string) {
  if (selectionText.value) {
    emit("addManualEntity", selectionText.value, entityType);
    showSelectionMenu.value = false;
    selectionText.value = "";
    // Clear selection
    window.getSelection()?.removeAllRanges();
  }
}

function handleClickOutside(event: MouseEvent) {
  if (!showSelectionMenu.value) return;

  const menu = document.getElementById("selection-menu");
  const target = event.target as Node;

  // Don't close if clicking inside menu
  if (menu && menu.contains(target)) return;

  // Don't close if clicking inside original text area (might be starting new selection)
  if (originalTextRef.value?.contains(target)) return;

  showSelectionMenu.value = false;
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});

// Build segments for rendering original text with clickable entities
interface TextSegment {
  type: "text" | "entity";
  content: string;
  entity?: EditableEntity;
}

const originalTextSegments = computed((): TextSegment[] => {
  const text = props.result.original_text;
  const entities = [...props.editedEntities].sort((a, b) => a.start - b.start);

  if (entities.length === 0) {
    return [{ type: "text", content: text }];
  }

  const segments: TextSegment[] = [];
  let lastEnd = 0;

  for (const entity of entities) {
    // Add text before this entity
    if (entity.start > lastEnd) {
      segments.push({
        type: "text",
        content: text.slice(lastEnd, entity.start),
      });
    }
    // Add the entity
    segments.push({
      type: "entity",
      content: text.slice(entity.start, entity.end),
      entity,
    });
    lastEnd = entity.end;
  }

  // Add remaining text after last entity
  if (lastEnd < text.length) {
    segments.push({
      type: "text",
      content: text.slice(lastEnd),
    });
  }

  return segments;
});
</script>

<template>
  <div class="space-y-4">
    <!-- Summary -->
    <div class="flex flex-wrap items-center gap-2">
      <span class="text-sm text-[hsl(var(--muted-foreground))]">
        {{ activeEntityCount }} of {{ editedEntities.length }} entities will be anonymized
      </span>
      <span
        v-if="excludedCount > 0"
        class="text-sm text-[hsl(var(--muted-foreground))]"
      >
        ({{ excludedCount }} excluded)
      </span>
    </div>

    <!-- Actions -->
    <div class="flex gap-2">
      <Button variant="outline" size="sm" @click="copyToClipboard">
        <component :is="copied ? Check : Copy" class="mr-2 h-4 w-4" />
        {{ copied ? "Copied!" : "Copy" }}
      </Button>
      <Button variant="outline" size="sm" @click="downloadResult">
        <Download class="mr-2 h-4 w-4" />
        Download
      </Button>
    </div>

    <!-- Side-by-side display -->
    <div class="grid gap-4 md:grid-cols-2">
      <!-- Original with clickable entities -->
      <Card class="p-4">
        <h4 class="mb-2 text-sm font-medium text-[hsl(var(--muted-foreground))]">
          Original (click entity to edit, select text to classify)
        </h4>
        <div
          ref="originalTextRef"
          class="whitespace-pre-wrap break-words text-sm select-text cursor-text"
          @mouseup="handleMouseUp"
        >
          <template v-for="(segment, index) in originalTextSegments" :key="index">
            <span v-if="segment.type === 'text'">{{ segment.content }}</span>
            <EntityEditPopover
              v-else-if="segment.entity"
              :entity="segment.entity"
              :available-types="availableTypes"
              :get-entity-color="getEntityColor"
              @exclude="emit('exclude', $event)"
              @include="emit('include', $event)"
              @reclassify="(id, newType) => emit('reclassify', id, newType)"
            >
              {{ segment.content }}
            </EntityEditPopover>
          </template>
        </div>
      </Card>

      <!-- Anonymized (live preview) -->
      <Card class="p-4">
        <h4 class="mb-2 text-sm font-medium text-[hsl(var(--muted-foreground))]">
          Anonymized ({{ result.anonymization_style }})
          <span v-if="hasEdits" class="text-amber-600 text-xs ml-2">
            (modified)
          </span>
        </h4>
        <div class="whitespace-pre-wrap break-words text-sm">
          {{ computedAnonymizedText }}
        </div>
      </Card>
    </div>

    <!-- Selection classification menu -->
    <Teleport to="body">
      <div
        v-if="showSelectionMenu"
        id="selection-menu"
        class="fixed z-50 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--popover))] p-2 shadow-lg"
        :style="{
          left: `${selectionMenuPosition.x}px`,
          top: `${selectionMenuPosition.y}px`,
          transform: 'translateX(-50%)',
        }"
      >
        <div class="text-xs text-[hsl(var(--muted-foreground))] px-2 py-1 mb-1 flex items-center gap-1">
          <Tag class="h-3 w-3" />
          Classify "{{ selectionText.slice(0, 20) }}{{ selectionText.length > 20 ? '...' : '' }}" as:
        </div>
        <div class="max-h-48 overflow-y-auto space-y-0.5">
          <button
            v-for="type in availableTypes"
            :key="type"
            type="button"
            class="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm hover:bg-[hsl(var(--accent))] transition-colors"
            @click="handleClassifySelection(type)"
          >
            <span
              :class="[
                'inline-block rounded px-1.5 py-0.5 text-xs',
                getEntityColor(type)
              ]"
            >
              {{ type }}
            </span>
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>
