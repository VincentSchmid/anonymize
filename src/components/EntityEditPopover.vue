<script setup lang="ts">
import { computed } from "vue";
import {
  PopoverRoot,
  PopoverTrigger,
  PopoverPortal,
  PopoverContent,
} from "radix-vue";
import { Check, RotateCcw, Tag } from "lucide-vue-next";
import type { EditableEntity } from "@/composables/useAnonymizer";

interface Props {
  entity: EditableEntity;
  availableTypes: string[];
  getEntityColor: (entityType: string) => string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  exclude: [id: string];
  include: [id: string];
  reclassify: [id: string, newType: string];
}>();

const isModified = computed(
  () => props.entity.excluded || props.entity.entity_type !== props.entity.originalType
);

function handleToggleExclude() {
  if (props.entity.excluded) {
    emit("include", props.entity.id);
  } else {
    emit("exclude", props.entity.id);
  }
}

function handleReclassify(newType: string) {
  if (newType !== props.entity.entity_type) {
    emit("reclassify", props.entity.id, newType);
  }
}
</script>

<template>
  <PopoverRoot>
    <PopoverTrigger as-child>
      <button
        type="button"
        :class="[
          'inline rounded px-0.5 cursor-pointer transition-all',
          getEntityColor(entity.entity_type),
          entity.excluded ? 'opacity-50 line-through' : '',
          isModified && !entity.excluded ? 'ring-2 ring-offset-1 ring-amber-400' : ''
        ]"
      >
        <slot />
      </button>
    </PopoverTrigger>
    <PopoverPortal>
      <PopoverContent
        :side-offset="5"
        class="z-50 w-56 rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--popover))] p-2 text-[hsl(var(--popover-foreground))] shadow-md outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
      >
        <!-- Header -->
        <div class="mb-2 px-2 py-1">
          <div class="text-xs text-[hsl(var(--muted-foreground))]">
            Detected as
          </div>
          <div class="font-medium text-sm">
            {{ entity.originalType }}
            <span v-if="entity.entity_type !== entity.originalType" class="text-amber-600">
              → {{ entity.entity_type }}
            </span>
          </div>
          <div class="text-xs text-[hsl(var(--muted-foreground))] mt-1">
            Score: {{ (entity.score * 100).toFixed(0) }}%
          </div>
        </div>

        <div class="h-px bg-[hsl(var(--border))] my-1" />

        <!-- Keep original toggle -->
        <button
          type="button"
          class="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm hover:bg-[hsl(var(--accent))] transition-colors"
          @click="handleToggleExclude"
        >
          <Check v-if="entity.excluded" class="h-4 w-4 text-green-600" />
          <RotateCcw v-else class="h-4 w-4" />
          <span>{{ entity.excluded ? "Will keep original" : "Keep original" }}</span>
        </button>

        <div class="h-px bg-[hsl(var(--border))] my-1" />

        <!-- Entity type selector -->
        <div class="px-2 py-1 text-xs text-[hsl(var(--muted-foreground))]">
          <Tag class="inline h-3 w-3 mr-1" />
          Reclassify as:
        </div>
        <div class="max-h-40 overflow-y-auto">
          <button
            v-for="type in availableTypes"
            :key="type"
            type="button"
            :class="[
              'flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm transition-colors',
              type === entity.entity_type
                ? 'bg-[hsl(var(--accent))] font-medium'
                : 'hover:bg-[hsl(var(--accent))]'
            ]"
            @click="handleReclassify(type)"
          >
            <Check
              v-if="type === entity.entity_type"
              class="h-4 w-4"
            />
            <span v-else class="w-4" />
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
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
