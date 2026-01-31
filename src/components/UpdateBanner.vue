<script setup lang="ts">
import type { UpdateInfo } from "@/composables/useUpdater";
import Button from "@/components/ui/button.vue";
import { Download, X, Loader2, RefreshCw } from "lucide-vue-next";

interface Props {
  updateInfo: UpdateInfo;
  isDownloading: boolean;
  isInstalling: boolean;
  downloadProgress: number;
}

defineProps<Props>();

const emit = defineEmits<{
  install: [];
  dismiss: [];
}>();
</script>

<template>
  <div
    class="flex items-center justify-between gap-4 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950"
  >
    <div class="flex items-center gap-3">
      <RefreshCw class="h-5 w-5 text-blue-600 dark:text-blue-400" />
      <div>
        <p class="font-medium text-blue-900 dark:text-blue-100">
          Update Available
        </p>
        <p class="text-sm text-blue-700 dark:text-blue-300">
          Version {{ updateInfo.version }} is available (current:
          {{ updateInfo.currentVersion }})
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      <div v-if="isDownloading || isInstalling" class="flex items-center gap-2">
        <Loader2 class="h-4 w-4 animate-spin text-blue-600" />
        <span class="text-sm text-blue-700 dark:text-blue-300">
          {{ isInstalling ? "Installing..." : `Downloading... ${downloadProgress}%` }}
        </span>
      </div>
      <template v-else>
        <Button size="sm" @click="emit('install')">
          <Download class="mr-2 h-4 w-4" />
          Update Now
        </Button>
        <Button variant="ghost" size="sm" @click="emit('dismiss')">
          <X class="h-4 w-4" />
        </Button>
      </template>
    </div>
  </div>
</template>
