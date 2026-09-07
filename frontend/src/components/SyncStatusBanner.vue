<template>
  <div v-if="showPending" class="sync-banner">
    <strong>{{ online ? '等待同步' : '当前离线' }}</strong>
    <span>{{ pendingCount }} 条任务或计划变更已保存在本机。</span>
  </div>

  <div v-if="sync.issues.length > 0" class="sync-banner sync-banner--error sync-issues">
    <div class="sync-issues__summary">
      <strong>同步受阻</strong>
      <span>
        {{ sync.issues.length }} 条变更被服务器拒绝，仍保留在本机。
      </span>
      <button type="button" class="text-action" @click="sync.expanded = !sync.expanded">
        {{ sync.expanded ? '收起原因' : '查看原因' }}
      </button>
    </div>

    <template v-if="sync.expanded">
      <ul class="sync-issues__list">
        <li v-for="issue in sync.issues" :key="issue.id">
          <div>
            <strong>{{ issue.summary }}</strong>
            <span>{{ issue.reason }}</span>
          </div>
          <button
            type="button"
            class="text-action"
            :disabled="sync.busy"
            title="彻底丢弃这条变更；新建的内容会一并从本机移除"
            @click="discard(issue)"
          >
            丢弃
          </button>
        </li>
      </ul>

      <div class="sync-issues__actions">
        <button
          class="button button--primary button--small"
          type="button"
          :disabled="sync.busy"
          @click="retry"
        >
          {{ sync.busy ? '重试中…' : '全部重试' }}
        </button>
        <span v-if="sync.lastResult">{{ sync.lastResult }}</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'

import { useAuthStore } from '@/stores/auth'
import { useSyncIssueStore, type SyncIssue } from '@/stores/sync-issues'

const props = withDefaults(
  defineProps<{
    pendingCount: number
    failedCount: number
    online?: boolean
  }>(),
  { online: true },
)

const emit = defineEmits<{ (event: 'repaired'): void }>()

const auth = useAuthStore()
const sync = useSyncIssueStore()

const showPending = computed(() => !props.online || props.pendingCount > 0)

// The queue is shared by every page, so the details are loaded whenever the
// owning store reports a rejection rather than on a timer of our own.
watch(
  () => props.failedCount,
  () => {
    void refresh()
  },
)

onMounted(() => {
  void refresh()
})

async function refresh(): Promise<void> {
  const ownerId = auth.user?.profile.id
  if (!ownerId) return
  await sync.load(ownerId)
}

async function retry(): Promise<void> {
  await sync.retryAll()
  emit('repaired')
}

async function discard(issue: SyncIssue): Promise<void> {
  const confirmed = window.confirm(
    `丢弃「${issue.summary}」？${issue.action === 'create' ? '这条内容会同时从本机移除，且不会出现在服务器上。' : '本机的这次修改会在下次刷新时被服务器数据覆盖。'}`,
  )
  if (!confirmed) return
  await sync.discard(issue.id)
  emit('repaired')
}
</script>
