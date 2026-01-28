<script setup lang="ts">
import { computed } from "vue";
import {
  PopoverRoot,
  PopoverTrigger,
  PopoverPortal,
  PopoverContent,
  PopoverArrow,
} from "radix-vue";
import { cn } from "@/lib/utils";

interface Props {
  align?: "start" | "center" | "end";
  side?: "top" | "right" | "bottom" | "left";
  sideOffset?: number;
  class?: string;
}

const props = withDefaults(defineProps<Props>(), {
  align: "center",
  side: "bottom",
  sideOffset: 4,
});

const contentClass = computed(() =>
  cn(
    "z-50 w-72 rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--popover))] p-4 text-[hsl(var(--popover-foreground))] shadow-md outline-none",
    "data-[state=open]:animate-in data-[state=closed]:animate-out",
    "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
    "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
    "data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2",
    "data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
    props.class
  )
);
</script>

<template>
  <PopoverRoot>
    <PopoverTrigger as-child>
      <slot name="trigger" />
    </PopoverTrigger>
    <PopoverPortal>
      <PopoverContent
        :class="contentClass"
        :align="align"
        :side="side"
        :side-offset="sideOffset"
      >
        <slot />
        <PopoverArrow class="fill-[hsl(var(--border))]" />
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
