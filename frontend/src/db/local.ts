import Dexie, { type EntityTable } from 'dexie'

import type {
  LocalMetadata,
  LocalTimerState,
  SessionOutboxItem,
  SessionSnapshot,
} from '@/types/session'
import type { DailyPlan } from '@/types/daily-plan'
import type { SyncOperation } from '@/types/offline'
import type { Task } from '@/types/task'

class TrackerDatabase extends Dexie {
  timerStates!: EntityTable<LocalTimerState, 'id'>
  sessionOutbox!: EntityTable<SessionOutboxItem, 'session_id'>
  metadata!: EntityTable<LocalMetadata, 'key'>
  cachedTasks!: EntityTable<Task, 'id'>
  cachedDailyPlans!: EntityTable<DailyPlan, 'id'>
  syncOperations!: EntityTable<SyncOperation, 'id'>

  constructor() {
    super('time-budget-learning-tracker')
    this.version(1).stores({
      timerStates: 'id, owner_id',
      sessionOutbox: 'session_id, owner_id, snapshot.client_updated_at',
      metadata: 'key',
    })
    this.version(2).stores({
      timerStates: 'id, owner_id',
      sessionOutbox: 'session_id, owner_id, snapshot.client_updated_at',
      metadata: 'key',
      cachedTasks: 'id, owner_id, updated_at',
      cachedDailyPlans: 'id, owner_id, &[owner_id+plan_date], updated_at',
      syncOperations:
        'id, owner_id, [owner_id+created_at], created_at, entity_type, entity_id',
    })
  }
}

export const localDb = new TrackerDatabase()

function cloneForStorage<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

export async function getClientId(): Promise<string> {
  const stored = await localDb.metadata.get('client_id')
  if (stored) return stored.value

  const value = crypto.randomUUID()
  await localDb.metadata.put({ key: 'client_id', value })
  return value
}

/**
 * A stored timer state is only usable if it still carries a whole snapshot.
 * A truncated record — an interrupted unload write, or a row left by an older
 * version of the app — otherwise reaches the timer face as `NaN:NaN:NaN`
 * along with working pause and finish buttons for a session that is not there.
 */
function isUsableTimerState(state: LocalTimerState | undefined): state is LocalTimerState {
  if (!state || typeof state.session_id !== 'string' || !state.snapshot) return false
  const { status, started_at: startedAt, client_updated_at: updatedAt } = state.snapshot
  return (
    (status === 'RUNNING' || status === 'PAUSED' || status === 'COMPLETED') &&
    Number.isFinite(state.snapshot.duration_seconds) &&
    Number.isFinite(Date.parse(startedAt)) &&
    Number.isFinite(Date.parse(updatedAt))
  )
}

export async function loadActiveTimer(
  ownerId: string,
): Promise<LocalTimerState | undefined> {
  const stored = await localDb.timerStates.get(ownerId)
  if (stored && !isUsableTimerState(stored)) {
    await localDb.timerStates.delete(ownerId)
    return undefined
  }
  return stored
}

export async function saveActiveTimer(
  ownerId: string,
  sessionId: string,
  snapshot: SessionSnapshot,
  targetSeconds: number | null = null,
  baseSeconds: number | null = null,
): Promise<void> {
  const storedSnapshot = cloneForStorage(snapshot)
  await localDb.timerStates.put({
    id: ownerId,
    owner_id: ownerId,
    session_id: sessionId,
    snapshot: storedSnapshot,
    target_seconds: targetSeconds,
    base_seconds: baseSeconds,
  })
}

export async function clearActiveTimer(ownerId: string): Promise<void> {
  await localDb.timerStates.delete(ownerId)
}

export async function enqueueSessionSnapshot(
  ownerId: string,
  sessionId: string,
  snapshot: SessionSnapshot,
): Promise<void> {
  const existing = await localDb.sessionOutbox.get(sessionId)
  await localDb.sessionOutbox.put({
    session_id: sessionId,
    owner_id: ownerId,
    snapshot: cloneForStorage(snapshot),
    retry_count: existing?.retry_count ?? 0,
    last_error: null,
  })
}

let lastOperationTimestamp = 0

function nextOperationTimestamp(): string {
  const timestamp = Math.max(Date.now(), lastOperationTimestamp + 1)
  lastOperationTimestamp = timestamp
  return new Date(timestamp).toISOString()
}

export async function enqueueSyncOperation(
  ownerId: string,
  entityType: SyncOperation['entity_type'],
  entityId: string,
  action: SyncOperation['action'],
  payload: Record<string, unknown>,
): Promise<void> {
  await localDb.syncOperations.put({
    id: crypto.randomUUID(),
    owner_id: ownerId,
    entity_type: entityType,
    entity_id: entityId,
    action,
    payload: cloneForStorage(payload),
    created_at: nextOperationTimestamp(),
    retry_count: 0,
    last_error: null,
  })
}

export async function saveCachedDailyPlan(plan: DailyPlan): Promise<void> {
  await localDb.cachedDailyPlans.put(cloneForStorage(plan))
}

export async function saveCachedTask(task: Task): Promise<void> {
  await localDb.cachedTasks.put(cloneForStorage(task))
}

export async function saveCachedTasks(tasks: Task[]): Promise<void> {
  if (tasks.length === 0) return
  await localDb.cachedTasks.bulkPut(cloneForStorage(tasks))
}

export async function pendingSyncCount(ownerId: string): Promise<number> {
  return localDb.syncOperations.where('owner_id').equals(ownerId).count()
}

export async function readCachedDailyPlan(
  ownerId: string,
  planDate: string,
): Promise<DailyPlan | undefined> {
  return localDb.cachedDailyPlans
    .where('[owner_id+plan_date]')
    .equals([ownerId, planDate])
    .first()
}
