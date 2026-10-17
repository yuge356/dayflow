import type { SessionSnapshot } from '@/types/session'

export function snapshotDuration(
  snapshot: SessionSnapshot,
  now = new Date(),
): number {
  const recorded = Number.isFinite(snapshot.duration_seconds) ? snapshot.duration_seconds : 0
  if (snapshot.status !== 'RUNNING' || !snapshot.last_resumed_at) {
    return recorded
  }
  const elapsed = Math.max(
    0,
    Math.floor((now.getTime() - new Date(snapshot.last_resumed_at).getTime()) / 1000),
  )
  return recorded + elapsed
}

export function formatTimer(totalSeconds: number): string {
  // Guard the display itself too: one malformed input must not turn the whole
  // timer into "NaN:NaN:NaN".
  const safeSeconds = Number.isFinite(totalSeconds) ? Math.max(0, Math.floor(totalSeconds)) : 0
  const hours = Math.floor(safeSeconds / 3600)
  const minutes = Math.floor((safeSeconds % 3600) / 60)
  const seconds = safeSeconds % 60
  return [hours, minutes, seconds].map((value) => String(value).padStart(2, '0')).join(':')
}

