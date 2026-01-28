<script setup lang="ts">
import Switch from "@/components/ui/switch.vue";
import Button from "@/components/ui/button.vue";
import Badge from "@/components/ui/badge.vue";
import type { EntityInfo } from "@/lib/api";
import {
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  CreditCard,
  Shield,
  Building,
} from "lucide-vue-next";

interface Props {
  entities: EntityInfo[];
  enabledEntities: Set<string>;
  isLoading?: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  toggle: [entityType: string];
  "enable-all": [];
  "disable-all": [];
}>();

function getEntityIcon(entityType: string) {
  const icons: Record<string, typeof User> = {
    PERSON: User,
    EMAIL_ADDRESS: Mail,
    PHONE_NUMBER: Phone,
    CH_PHONE: Phone,
    LOCATION: MapPin,
    DATE_TIME: Calendar,
    CH_AHV: Shield,
    CH_IBAN: CreditCard,
    IBAN_CODE: CreditCard,
    CH_POSTAL_CODE: Building,
  };
  return icons[entityType] || Shield;
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-medium">Entity Types</h3>
      <div class="flex gap-2">
        <Button variant="outline" size="sm" @click="emit('enable-all')">
          Select All
        </Button>
        <Button variant="outline" size="sm" @click="emit('disable-all')">
          Deselect All
        </Button>
      </div>
    </div>

    <div v-if="isLoading" class="text-sm text-[hsl(var(--muted-foreground))]">
      Loading entities...
    </div>

    <div v-else class="space-y-4">
      <!-- Swiss-specific entities -->
      <div v-if="entities.some((e) => e.is_swiss)">
        <div class="mb-2 flex items-center gap-2">
          <Badge variant="secondary" class="text-xs">Swiss</Badge>
        </div>
        <div class="grid gap-2">
          <div
            v-for="entity in entities.filter((e) => e.is_swiss)"
            :key="entity.type"
            class="flex items-center justify-between rounded-md border border-[hsl(var(--border))] p-3"
          >
            <div class="flex items-center gap-3">
              <component
                :is="getEntityIcon(entity.type)"
                class="h-4 w-4 text-[hsl(var(--muted-foreground))]"
              />
              <div>
                <p class="text-sm font-medium">{{ entity.type }}</p>
                <p class="text-xs text-[hsl(var(--muted-foreground))]">
                  {{ entity.description }}
                </p>
              </div>
            </div>
            <Switch
              :model-value="enabledEntities.has(entity.type)"
              @update:model-value="emit('toggle', entity.type)"
            />
          </div>
        </div>
      </div>

      <!-- Standard entities -->
      <div>
        <div class="mb-2 flex items-center gap-2">
          <Badge variant="outline" class="text-xs">Standard</Badge>
        </div>
        <div class="grid gap-2">
          <div
            v-for="entity in entities.filter((e) => !e.is_swiss)"
            :key="entity.type"
            class="flex items-center justify-between rounded-md border border-[hsl(var(--border))] p-3"
          >
            <div class="flex items-center gap-3">
              <component
                :is="getEntityIcon(entity.type)"
                class="h-4 w-4 text-[hsl(var(--muted-foreground))]"
              />
              <div>
                <p class="text-sm font-medium">{{ entity.type }}</p>
                <p class="text-xs text-[hsl(var(--muted-foreground))]">
                  {{ entity.description }}
                </p>
              </div>
            </div>
            <Switch
              :model-value="enabledEntities.has(entity.type)"
              @update:model-value="emit('toggle', entity.type)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
