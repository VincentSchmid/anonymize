<script setup lang="ts">
import { computed } from "vue";
import Button from "@/components/ui/button.vue";
import { X } from "lucide-vue-next";

interface Props {
  modelValue: string;
  placeholder?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: "Paste or type your text here...",
  disabled: false,
});

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const charCount = computed(() => props.modelValue.length);

function clear() {
  emit("update:modelValue", "");
}

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement;
  emit("update:modelValue", target.value);
}
</script>

<template>
  <div class="relative">
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      class="min-h-[200px] w-full resize-y rounded-md border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-3 py-2 text-sm ring-offset-[hsl(var(--background))] placeholder:text-[hsl(var(--muted-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      @input="handleInput"
    />
    <div
      class="absolute bottom-2 right-2 flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]"
    >
      <span>{{ charCount }} characters</span>
      <Button
        v-if="modelValue.length > 0"
        variant="ghost"
        size="icon"
        class="h-6 w-6"
        @click="clear"
      >
        <X class="h-4 w-4" />
      </Button>
    </div>
  </div>
</template>
