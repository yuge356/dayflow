import { defineStore } from 'pinia'

import { localDb } from '@/db/local'
import { getPendingOperations, syncPendingChanges } from '@/services/offline-sync'
import type { SyncOperation } from '@/types/offline'
import { translateApiDetail } from '@/utils/api-error'

export interface SyncIssue {
  id: string
  /** What the change was about, e.g. 新建任务「读文献」. */
  summary: string
  /** Why the server refused it, in Chinese where the message is known. */
  reason: string
  retryCount: number
  entityType: SyncOperation['entity_type']
  action: SyncOperation['action']
}

interface SyncIssueState {
  ownerId: string | null
  issues: SyncIssue[]
  busy: boolean
  expanded: boolean
  lastResult: string
}

const ENTITY_LABELS: Record<SyncOperation['entity_type'], string> = {
  task: '任务',
  daily_plan: '每日计划',
  daily_plan_item: '今日任务',
}

const ACTION_LABELS: Record<SyncOperation['action'], string> = {
  create: '新建',
  update: '修改',
  delete: '删除',
}

function operationTitle(operation: SyncOperation): string {
  const title = operation.payload.title
  return typeof title === 'string' && title.length > 0 ? title : ''
}

function describe(operation: SyncOperation): string {
  const noun = ENTITY_LABELS[operation.entity_type]
  const verb = ACTION_LABELS[operation.action]
  const title = operationTitle(operation)
  return title ? `${verb}${noun}「${title}」` : `${verb}${noun}`
}

export const useSyncIssueStore = defineStore('sync-issues', {
  state: (): SyncIssueState => ({
    ownerId: null,
    issues: [],
    busy: false,
    expanded: false,
    lastResult: '',
  }),

  actions: {
    /**
     * Read the rejected entries out of the shared outbox. The queue already
     * records the server's reason for each one; without this the banner could
     * only report a count, which left "请检查数据后重试" with nothing to check.
     */
    async load(ownerId: string): Promise<void> {
      this.ownerId = ownerId
      const operations = await getPendingOperations(ownerId)
      this.issues = operations
        .filter((operation) => operation.retry_count > 0)
        .sort((left, right) => left.created_at.localeCompare(right.created_at))
        .map((operation) => ({
          id: operation.id,
          summary: describe(operation),
          reason: translateApiDetail(operation.last_error) || '服务器拒绝了该操作。',
          retryCount: operation.retry_count,
          entityType: operation.entity_type,
          action: operation.action,
        }))
    },

    /**
     * Clear the quarantine marks and replay. Used after the cause is fixed —
     * a pending database migration, a renamed project, a restored connection.
     */
    async retryAll(): Promise<void> {
      if (!this.ownerId || this.busy) return
      const ownerId = this.ownerId
      this.busy = true
      this.lastResult = ''
      try {
        const failed = (await getPendingOperations(ownerId)).filter(
          (operation) => operation.retry_count > 0,
        )
        for (const operation of failed) {
          // Clearing retry_count is enough to make it due again: the backoff
          // in the replay only applies to operations still marked as failed.
          await localDb.syncOperations.update(operation.id, {
            retry_count: 0,
            last_error: null,
          })
        }
        await syncPendingChanges(ownerId)
        await this.load(ownerId)
        this.lastResult = this.issues.length === 0
          ? '全部变更已同步。'
          : `仍有 ${this.issues.length} 条被拒绝，请查看下方原因。`
      } catch {
        await this.load(ownerId)
        this.lastResult = '网络暂时不可用，稍后会自动重试。'
      } finally {
        this.busy = false
      }
    },

    /**
     * Forget one change for good. A rejected creation also takes its local
     * row with it: keeping a task the server will never accept would leave it
     * on screen forever and let repair paths queue it again.
     */
    async discard(issueId: string): Promise<void> {
      if (!this.ownerId || this.busy) return
      const ownerId = this.ownerId
      this.busy = true
      try {
        const operation = await localDb.syncOperations.get(issueId)
        if (!operation) {
          await this.load(ownerId)
          this.lastResult = '该变更已经不在队列里了。'
          return
        }
        if (operation.action === 'create') {
          if (operation.entity_type === 'task') {
            await localDb.cachedTasks.delete(operation.entity_id)
          } else if (operation.entity_type === 'daily_plan_item') {
            const plans = await localDb.cachedDailyPlans
              .where('owner_id')
              .equals(ownerId)
              .toArray()
            for (const plan of plans) {
              if (!plan.items.some((item) => item.id === operation.entity_id)) continue
              await localDb.cachedDailyPlans.put({
                ...plan,
                items: plan.items.filter((item) => item.id !== operation.entity_id),
              })
            }
          }
        }
        await localDb.syncOperations.delete(issueId)
        await this.load(ownerId)
        this.lastResult = '已丢弃该变更。'
      } finally {
        this.busy = false
      }
    },
  },
})
