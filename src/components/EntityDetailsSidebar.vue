<script setup lang="ts">
import { computed } from "vue";
import Card from "@/components/ui/card.vue";
import Button from "@/components/ui/button.vue";
import Tooltip from "@/components/ui/tooltip.vue";
import type { EditableEntity } from "@/composables/useAnonymizer";
import { Check, X, RotateCcw, ChevronDown } from "lucide-vue-next";
import {
  PopoverRoot,
  PopoverTrigger,
  PopoverPortal,
  PopoverContent,
} from "radix-vue";

interface Props {
  editedEntities: EditableEntity[];
  availableTypes: string[];
  getEntityColor: (entityType: string) => string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  exclude: [id: string];
  include: [id: string];
  reclassify: [id: string, newType: string];
  resetEdits: [];
}>();

// Group entities by their text (case-insensitive)
const groupedEntities = computed(() => {
  const groups = new Map<string, EditableEntity[]>();

  for (const entity of props.editedEntities) {
    const key = entity.text.toLowerCase();
    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key)!.push(entity);
  }

  // Convert to array and sort by first occurrence
  return Array.from(groups.entries())
    .map(([key, entities]) => ({
      key,
      text: entities[0].text,
      entities,
      count: entities.length,
      // Use first entity as representative
      representative: entities[0],
      // Check if all are excluded
      allExcluded: entities.every(e => e.excluded),
      // Check if any were reclassified
      isReclassified: entities[0].entity_type !== entities[0].originalType,
    }))
    .sort((a, b) => a.entities[0].start - b.entities[0].start);
});

const stats = computed(() => {
  const total = props.editedEntities.length;
  const excluded = props.editedEntities.filter(e => e.excluded).length;
  const reclassified = props.editedEntities.filter(e => e.entity_type !== e.originalType).length;
  return { total, excluded, reclassified, active: total - excluded };
});

function handleToggleExclude(entity: EditableEntity) {
  if (entity.excluded) {
    emit("include", entity.id);
  } else {
    emit("exclude", entity.id);
  }
}

function handleReclassify(entity: EditableEntity, newType: string) {
  emit("reclassify", entity.id, newType);
}
</script>

<template>
  <Card class="p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="flex items-center gap-2 font-medium">
        Entity Details
        <Tooltip text="Review and adjust detected entities. Click an entity type to reclassify it, or use 'Keep original' to exclude it from anonymization." />
      </h3>
      <Button
        v-if="stats.excluded > 0 || stats.reclassified > 0"
        variant="ghost"
        size="sm"
        @click="emit('resetEdits')"
      >
        <RotateCcw class="h-4 w-4 mr-1" />
        Reset
      </Button>
    </div>

    <!-- Stats -->
    <div class="text-xs text-[hsl(var(--muted-foreground))] mb-4 space-y-1">
      <div>{{ stats.active }} of {{ stats.total }} entities will be anonymized</div>
      <div v-if="stats.excluded > 0" class="text-green-600">
        {{ stats.excluded }} excluded (keeping original)
      </div>
      <div v-if="stats.reclassified > 0" class="text-amber-600">
        {{ stats.reclassified }} reclassified
      </div>
    </div>

    <div class="h-px bg-[hsl(var(--border))] mb-4" />

    <!-- Entity list grouped by text -->
    <div class="space-y-2 max-h-[calc(100vh-300px)] overflow-y-auto">
      <div
        v-for="group in groupedEntities"
        :key="group.key"
        :class="[
          'rounded-lg border border-[hsl(var(--border))] p-3',
          group.allExcluded ? 'opacity-60' : ''
        ]"
      >
        <!-- Entity text and type -->
        <div class="flex items-start justify-between gap-2 mb-2">
          <code
            :class="[
              'text-sm break-all',
              group.allExcluded ? 'line-through' : ''
            ]"
          >
            {{ group.text }}
          </code>
          <span
            v-if="group.count > 1"
            class="text-xs text-[hsl(var(--muted-foreground))] shrink-0"
          >
            x{{ group.count }}
          </span>
        </div>

        <!-- Type badge with dropdown to reclassify -->
        <div class="flex items-center gap-2 mb-2">
          <PopoverRoot>
            <PopoverTrigger as-child>
              <button
                type="button"
                class="inline-flex items-center gap-1 rounded text-xs px-2 py-1 cursor-pointer hover:ring-2 hover:ring-offset-1 hover:ring-[hsl(var(--ring))]"
                :class="getEntityColor(group.representative.entity_type)"
              >
                {{ group.representative.entity_type }}
                <ChevronDown class="h-3 w-3" />
              </button>
            </PopoverTrigger>
            <PopoverPortal>
              <PopoverContent
                :side-offset="5"
                class="z-50 w-48 rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--popover))] p-1 text-[hsl(var(--popover-foreground))] shadow-md"
              >
                <div class="text-xs text-[hsl(var(--muted-foreground))] px-2 py-1 mb-1">
                  Reclassify as:
                </div>
                <button
                  v-for="type in availableTypes"
                  :key="type"
                  type="button"
                  :class="[
                    'flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm transition-colors',
                    type === group.representative.entity_type
                      ? 'bg-[hsl(var(--accent))]'
                      : 'hover:bg-[hsl(var(--accent))]'
                  ]"
                  @click="handleReclassify(group.representative, type)"
                >
                  <Check
                    v-if="type === group.representative.entity_type"
                    class="h-3 w-3"
                  />
                  <span v-else class="w-3" />
                  <span
                    :class="[
                      'inline-block rounded px-1.5 py-0.5 text-xs',
                      getEntityColor(type)
                    ]"
                  >
                    {{ type }}
                  </span>
                </button>
              </PopoverContent>
            </PopoverPortal>
          </PopoverRoot>

          <span
            v-if="group.isReclassified"
            class="text-xs text-amber-600"
          >
            was {{ group.representative.originalType }}
          </span>
        </div>

        <!-- Score -->
        <div class="text-xs text-[hsl(var(--muted-foreground))] mb-2">
          Confidence: {{ (group.representative.score * 100).toFixed(0) }}%
        </div>

        <!-- Actions -->
        <button
          type="button"
          :class="[
            'flex items-center gap-1 text-xs rounded px-2 py-1 transition-colors w-full',
            group.allExcluded
              ? 'bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-900 dark:text-green-200'
              : 'bg-[hsl(var(--muted))] hover:bg-[hsl(var(--accent))]'
          ]"
          @click="handleToggleExclude(group.representative)"
        >
          <Check v-if="group.allExcluded" class="h-3 w-3" />
          <X v-else class="h-3 w-3" />
          {{ group.allExcluded ? "Keeping original" : "Keep original" }}
        </button>
      </div>
    </div>
  </Card>
</template>
