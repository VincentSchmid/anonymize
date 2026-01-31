<script setup lang="ts">
import type { NlpEngineInfo } from "@/lib/api";
import Tooltip from "@/components/ui/tooltip.vue";
import { Cpu, Sparkles, Loader2 } from "lucide-vue-next";

interface Props {
  modelValue: string;
  engines: NlpEngineInfo[];
  isLoading?: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const iconMap: Record<string, typeof Cpu> = {
  spacy: Cpu,
  transformers: Sparkles,
};

const getIcon = (engineId: string) => iconMap[engineId] || Cpu;
</script>

<template>
  <div class="space-y-3">
    <h3 class="flex items-center gap-2 text-sm font-medium">
      Detection Model
      <Tooltip
        text="Choose the NLP model for entity detection. spaCy is faster and better for organizations. EU PII Safeguard detects more PII types like passwords and titles."
      />
    </h3>
    <div v-if="isLoading" class="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
      <Loader2 class="h-4 w-4 animate-spin" />
      <span>Loading engines...</span>
    </div>
    <div v-else class="space-y-2">
      <button
        v-for="engine in engines"
        :key="engine.id"
        class="flex w-full flex-col items-start rounded-md border p-3 text-left transition-colors"
        :class="[
          modelValue === engine.id
            ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5'
            : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--accent))]',
        ]"
        @click="emit('update:modelValue', engine.id)"
      >
        <div class="flex items-center gap-2">
          <component
            :is="getIcon(engine.id)"
            class="h-4 w-4"
            :class="[
              modelValue === engine.id
                ? 'text-[hsl(var(--primary))]'
                : 'text-[hsl(var(--muted-foreground))]',
            ]"
          />
          <span class="text-sm font-medium">{{ engine.name }}</span>
        </div>
        <p class="mt-1 text-xs text-[hsl(var(--muted-foreground))]">
          {{ engine.description }}
        </p>
      </button>
    </div>
  </div>
</template>
