<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import Card from "@/components/ui/card.vue";
import Button from "@/components/ui/button.vue";
import TextInput from "@/components/TextInput.vue";
import FileUpload from "@/components/FileUpload.vue";
import EntityToggle from "@/components/EntityToggle.vue";
import AnonymizationSettings from "@/components/AnonymizationSettings.vue";
import ModelSettings from "@/components/ModelSettings.vue";
import ResultViewer from "@/components/ResultViewer.vue";
import EntityDetailsSidebar from "@/components/EntityDetailsSidebar.vue";
import UpdateBanner from "@/components/UpdateBanner.vue";
import { useSidecar } from "@/composables/useSidecar";
import { useAnonymizer } from "@/composables/useAnonymizer";
import { useUpdater } from "@/composables/useUpdater";
import Tooltip from "@/components/ui/tooltip.vue";
import {
  Shield,
  AlertCircle,
  Loader2,
  CheckCircle2,
  XCircle,
  ArrowLeft,
} from "lucide-vue-next";

type ViewMode = "input" | "results";
const currentView = ref<ViewMode>("input");

const sidecar = useSidecar();
const anonymizer = useAnonymizer();
const updater = useUpdater();

// Load entities when backend becomes healthy
watch(
  () => sidecar.status.value.healthy,
  async (healthy) => {
    console.log("[App] Backend healthy changed:", healthy);
    if (healthy) {
      await anonymizer.loadEntities();
      console.log("[App] After loadEntities, entities count:", anonymizer.entities.value.length);
    }
  }
);

// Debug: watch entities changes
watch(
  () => anonymizer.entities.value,
  (newEntities) => {
    console.log("[App] Entities updated:", newEntities.length, newEntities.map(e => e.type));
  },
  { deep: true }
);

onMounted(async () => {
  console.log("[App] Mounted, backend healthy:", sidecar.status.value.healthy);
  if (sidecar.status.value.healthy) {
    await anonymizer.loadEntities();
  }

  // Check for updates on startup (silently in background)
  updater.checkForUpdates();
});

function handleFileLoaded(content: string) {
  anonymizer.setInputText(content);
}

async function handleAnonymize() {
  await anonymizer.anonymize();
  if (anonymizer.hasResult.value) {
    currentView.value = "results";
  }
}

function handleBack() {
  currentView.value = "input";
}

function handleStartOver() {
  anonymizer.clear();
  currentView.value = "input";
}
</script>

<template>
  <div class="min-h-screen bg-[hsl(var(--background))]">
    <!-- Header -->
    <header
      class="border-b border-[hsl(var(--border))] bg-[hsl(var(--card))] px-6 py-4"
    >
      <div class="mx-auto flex max-w-[1800px] items-center justify-between">
        <div class="flex items-center gap-3">
          <Shield class="h-8 w-8 text-[hsl(var(--primary))]" />
          <div>
            <h1 class="text-xl font-semibold">Anonymize</h1>
            <p class="text-sm text-[hsl(var(--muted-foreground))]">
              Swiss Document Anonymization
            </p>
          </div>
        </div>

        <!-- Backend status indicator -->
        <div class="flex items-center gap-2 text-sm">
          <span class="text-[hsl(var(--muted-foreground))]">Backend:</span>
          <!-- Ready state -->
          <div
            v-if="sidecar.status.value.healthy"
            class="flex items-center gap-1 text-green-600"
          >
            <CheckCircle2 class="h-4 w-4" />
            <span>Ready</span>
          </div>
          <!-- Starting state: loading OR running but not yet healthy -->
          <div
            v-else-if="sidecar.isLoading.value || sidecar.status.value.running"
            class="flex items-center gap-1 text-amber-600"
          >
            <Loader2 class="h-4 w-4 animate-spin" />
            <span>Starting...</span>
          </div>
          <!-- Offline state -->
          <div v-else class="flex items-center gap-1 text-red-600">
            <XCircle class="h-4 w-4" />
            <span>Offline</span>
            <Button variant="outline" size="sm" @click="sidecar.startBackend">
              Start
            </Button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="mx-auto max-w-[1800px] p-6">
      <!-- Update banner -->
      <UpdateBanner
        v-if="updater.updateAvailable.value && updater.updateInfo.value"
        :update-info="updater.updateInfo.value"
        :is-downloading="updater.isDownloading.value"
        :is-installing="updater.isInstalling.value"
        :download-progress="updater.downloadProgress.value"
        class="mb-6"
        @install="updater.downloadAndInstall"
        @dismiss="updater.dismissUpdate"
      />

      <!-- Error banner -->
      <div
        v-if="anonymizer.error.value"
        class="mb-6 flex items-center gap-2 rounded-lg border border-[hsl(var(--destructive))] bg-[hsl(var(--destructive))]/10 p-4 text-[hsl(var(--destructive))]"
      >
        <AlertCircle class="h-5 w-5" />
        <p>{{ anonymizer.error.value }}</p>
        <Button
          variant="ghost"
          size="sm"
          class="ml-auto"
          @click="anonymizer.error.value = null"
        >
          Dismiss
        </Button>
      </div>

      <!-- INPUT VIEW -->
      <div v-if="currentView === 'input'" class="grid gap-6 lg:grid-cols-[1fr_320px]">
        <!-- Left column: Input -->
        <div class="min-w-0 space-y-6">
          <Card class="p-6">
            <h2 class="mb-4 flex items-center gap-2 text-lg font-medium">
              Input Text
              <Tooltip text="Enter or upload German text containing personal information. The system will detect and anonymize names, addresses, phone numbers, AHV numbers, and other sensitive data." />
            </h2>

            <!-- File upload -->
            <FileUpload class="mb-4" @file-loaded="handleFileLoaded" />

            <!-- Text input -->
            <TextInput
              v-model="anonymizer.inputText.value"
              :disabled="!sidecar.status.value.healthy"
              placeholder="Or paste/type your German text here...

Example:
Hans Muller wohnt in der Bahnhofstrasse 42, 8001 Zurich.
Seine AHV-Nummer ist 756.1234.5678.90.
Kontakt: hans.muller@example.com oder +41 79 123 45 67"
            />

            <!-- Anonymize button -->
            <div class="mt-4 flex gap-2">
              <Button
                :disabled="
                  !anonymizer.hasInput.value ||
                  anonymizer.isLoading.value ||
                  !sidecar.status.value.healthy
                "
                @click="handleAnonymize"
              >
                <Loader2
                  v-if="anonymizer.isLoading.value"
                  class="mr-2 h-4 w-4 animate-spin"
                />
                {{ anonymizer.isLoading.value ? "Processing..." : "Anonymize" }}
              </Button>
              <Button
                v-if="anonymizer.hasInput.value"
                variant="outline"
                @click="anonymizer.clear"
              >
                Clear
              </Button>
            </div>
          </Card>
        </div>

        <!-- Right column: Settings -->
        <div class="space-y-6">
          <Card class="p-6">
            <ModelSettings
              :model-value="anonymizer.currentEngine.value"
              :engines="anonymizer.availableEngines.value"
              :is-loading="anonymizer.isLoadingEngineInfo.value || anonymizer.isLoadingEngine.value"
              @update:model-value="anonymizer.setEngine"
            />
          </Card>

          <Card class="p-6">
            <AnonymizationSettings v-model="anonymizer.anonymizationStyle.value" />
          </Card>

          <Card class="max-h-[400px] overflow-y-auto p-6">
            <EntityToggle
              :entities="anonymizer.entities.value"
              :enabled-entities="anonymizer.enabledEntities.value"
              :is-loading="anonymizer.isLoadingEntities.value"
              @toggle="anonymizer.toggleEntity"
              @enable-all="anonymizer.enableAllEntities"
              @disable-all="anonymizer.disableAllEntities"
            />
          </Card>
        </div>
      </div>

      <!-- RESULTS VIEW -->
      <div v-else-if="currentView === 'results'" class="grid gap-6 lg:grid-cols-[1fr_320px]">
        <!-- Left column: Results -->
        <div class="min-w-0 space-y-6">
          <!-- Navigation -->
          <div class="flex items-center gap-4">
            <Button variant="outline" size="sm" @click="handleBack">
              <ArrowLeft class="mr-2 h-4 w-4" />
              Back to Input
            </Button>
            <Button variant="outline" size="sm" @click="handleStartOver">
              Start Over
            </Button>
          </div>

          <Card class="p-6">
            <h2 class="mb-4 flex items-center gap-2 text-lg font-medium">
              Results
              <Tooltip text="View the anonymized text with highlighted entities. Click on highlighted text to exclude it from anonymization or change its type." />
            </h2>
            <ResultViewer
              v-if="anonymizer.result.value"
              :result="anonymizer.result.value"
              :edited-entities="anonymizer.editedEntities.value"
              :computed-anonymized-text="anonymizer.computedAnonymizedText.value"
              :has-edits="anonymizer.hasEdits.value"
              :available-types="anonymizer.entities.value.map(e => e.type)"
              :get-entity-color="anonymizer.getEntityColor"
              @exclude="anonymizer.excludeEntity"
              @include="anonymizer.includeEntity"
              @reclassify="anonymizer.reclassifyEntity"
              @reset-edits="anonymizer.resetEdits"
              @add-manual-entity="anonymizer.addManualEntity"
            />
          </Card>
        </div>

        <!-- Right column: Entity Details -->
        <div class="space-y-6">
          <EntityDetailsSidebar
            v-if="anonymizer.result.value"
            :edited-entities="anonymizer.editedEntities.value"
            :available-types="anonymizer.entities.value.map(e => e.type)"
            :get-entity-color="anonymizer.getEntityColor"
            @exclude="anonymizer.excludeEntity"
            @include="anonymizer.includeEntity"
            @reclassify="anonymizer.reclassifyEntity"
            @reset-edits="anonymizer.resetEdits"
          />
        </div>
      </div>
    </main>
  </div>
</template>
