<script setup lang="ts">
import {
  TooltipRoot,
  TooltipTrigger,
  TooltipPortal,
  TooltipContent,
  TooltipProvider,
} from "radix-vue";
import { HelpCircle } from "lucide-vue-next";

interface Props {
  text: string;
  side?: "top" | "right" | "bottom" | "left";
  sideOffset?: number;
}

withDefaults(defineProps<Props>(), {
  side: "top",
  sideOffset: 4,
});
</script>

<template>
  <TooltipProvider :delay-duration="200">
    <TooltipRoot>
      <TooltipTrigger as-child>
        <button type="button" class="inline-flex cursor-help">
          <slot>
            <HelpCircle class="h-4 w-4 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]" />
          </slot>
        </button>
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent
          :side="side"
          :side-offset="sideOffset"
          class="z-50 max-w-xs rounded-md bg-[hsl(var(--popover))] px-3 py-2 text-sm text-[hsl(var(--popover-foreground))] shadow-md ring-1 ring-[hsl(var(--border))] animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2"
        >
          {{ text }}
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>
