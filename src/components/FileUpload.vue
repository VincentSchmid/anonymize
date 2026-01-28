<script setup lang="ts">
import { ref } from "vue";
import Button from "@/components/ui/button.vue";
import { Upload, File, X } from "lucide-vue-next";

const emit = defineEmits<{
  "file-loaded": [content: string];
}>();

const isDragging = ref(false);
const selectedFile = ref<File | null>(null);
const error = ref<string | null>(null);

function handleDragOver(event: DragEvent) {
  event.preventDefault();
  isDragging.value = true;
}

function handleDragLeave() {
  isDragging.value = false;
}

function handleDrop(event: DragEvent) {
  event.preventDefault();
  isDragging.value = false;

  const files = event.dataTransfer?.files;
  if (files && files.length > 0) {
    processFile(files[0]);
  }
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    processFile(input.files[0]);
  }
}

function processFile(file: File) {
  error.value = null;

  if (!file.name.endsWith(".txt")) {
    error.value = "Only .txt files are supported";
    return;
  }

  if (file.size > 1024 * 1024) {
    error.value = "File size must be less than 1MB";
    return;
  }

  selectedFile.value = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target?.result as string;
    emit("file-loaded", content);
  };
  reader.onerror = () => {
    error.value = "Failed to read file";
  };
  reader.readAsText(file);
}

function clearFile() {
  selectedFile.value = null;
  error.value = null;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
</script>

<template>
  <div>
    <div
      class="relative rounded-lg border-2 border-dashed p-6 text-center transition-colors"
      :class="[
        isDragging
          ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5'
          : 'border-[hsl(var(--border))]',
      ]"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <input
        type="file"
        accept=".txt"
        class="absolute inset-0 cursor-pointer opacity-0"
        @change="handleFileSelect"
      />

      <div v-if="!selectedFile" class="space-y-2">
        <Upload
          class="mx-auto h-10 w-10 text-[hsl(var(--muted-foreground))]"
        />
        <p class="text-sm text-[hsl(var(--muted-foreground))]">
          Drag and drop a .txt file here, or click to select
        </p>
      </div>

      <div v-else class="flex items-center justify-center gap-3">
        <File class="h-6 w-6 text-[hsl(var(--primary))]" />
        <div class="text-left">
          <p class="text-sm font-medium">{{ selectedFile.name }}</p>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">
            {{ formatFileSize(selectedFile.size) }}
          </p>
        </div>
        <Button variant="ghost" size="icon" class="h-8 w-8" @click.stop="clearFile">
          <X class="h-4 w-4" />
        </Button>
      </div>
    </div>

    <p v-if="error" class="mt-2 text-sm text-[hsl(var(--destructive))]">
      {{ error }}
    </p>
  </div>
</template>
