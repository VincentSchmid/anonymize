<script setup lang="ts">
import { computed } from "vue";
import { cn } from "@/lib/utils";

interface Props {
  variant?: "default" | "secondary" | "destructive" | "outline";
  class?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "default",
});

const variantClasses = {
  default: "border-transparent bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:bg-[hsl(var(--primary))]/80",
  secondary: "border-transparent bg-[hsl(var(--secondary))] text-[hsl(var(--secondary-foreground))] hover:bg-[hsl(var(--secondary))]/80",
  destructive: "border-transparent bg-[hsl(var(--destructive))] text-[hsl(var(--destructive-foreground))] hover:bg-[hsl(var(--destructive))]/80",
  outline: "text-[hsl(var(--foreground))]",
};

const badgeClass = computed(() =>
  cn(
    "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
    variantClasses[props.variant],
    props.class
  )
);
</script>

<template>
  <div :class="badgeClass">
    <slot />
  </div>
</template>
