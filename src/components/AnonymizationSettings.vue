<script setup lang="ts">
import type { AnonymizationStyle } from "@/composables/useAnonymizer";
import Tooltip from "@/components/ui/tooltip.vue";
import { Replace, EyeOff, Hash, Eraser } from "lucide-vue-next";

interface Props {
  modelValue: AnonymizationStyle;
}

defineProps<Props>();

const emit = defineEmits<{
  "update:modelValue": [value: AnonymizationStyle];
}>();

const styles: {
  value: AnonymizationStyle;
  label: string;
  description: string;
  example: string;
  icon: typeof Replace;
}[] = [
  {
    value: "replace",
    label: "Replace",
    description: "Replace with entity type label",
    example: "Hans Muller -> <PERSON>",
    icon: Replace,
  },
  {
    value: "mask",
    label: "Mask",
    description: "Replace characters with asterisks",
    example: "Hans Muller -> ***********",
    icon: EyeOff,
  },
  {
    value: "hash",
    label: "Hash",
    description: "Replace with SHA-256 hash",
    example: "Hans Muller -> a1b2c3d4...",
    icon: Hash,
  },
  {
    value: "redact",
    label: "Redact",
    description: "Remove completely",
    example: "Hans Muller -> (removed)",
    icon: Eraser,
  },
];
</script>

<template>
  <div class="space-y-3">
    <h3 class="flex items-center gap-2 text-sm font-medium">
      Anonymization Style
      <Tooltip text="Choose how detected entities are anonymized in the output. Replace shows the entity type, Mask uses asterisks, Hash creates a unique identifier, and Redact removes the text completely." />
    </h3>
    <div class="grid grid-cols-2 gap-2">
      <button
        v-for="style in styles"
        :key="style.value"
        class="flex flex-col items-start rounded-md border p-3 text-left transition-colors"
        :class="[
          modelValue === style.value
            ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5'
            : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--accent))]',
        ]"
        @click="emit('update:modelValue', style.value)"
      >
        <div class="flex items-center gap-2">
          <component
            :is="style.icon"
            class="h-4 w-4"
            :class="[
              modelValue === style.value
                ? 'text-[hsl(var(--primary))]'
                : 'text-[hsl(var(--muted-foreground))]',
            ]"
          />
          <span class="text-sm font-medium">{{ style.label }}</span>
        </div>
        <p class="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
          {{ style.description }}
        </p>
        <code
          class="mt-2 rounded bg-[hsl(var(--muted))] px-1.5 py-0.5 text-xs"
        >
          {{ style.example }}
        </code>
      </button>
    </div>
  </div>
</template>
