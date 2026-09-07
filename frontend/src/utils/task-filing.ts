import type { Task } from '@/types/task'

/**
 * The project quick 临时任务 are parked in. The server creates it on demand
 * and recognises it by this title, so the feature works on any database that
 * already allows a task under a project — no schema change required.
 */
export const INBOX_PROJECT_TITLE = '临时任务'

export function isInboxProject(task: Pick<Task, 'node_type' | 'title'>): boolean {
  return task.node_type === 'PROJECT' && task.title === INBOX_PROJECT_TITLE
}

export interface FilingTarget {
  id: string
  /** Display label; modules are indented under the project they belong to. */
  label: string
  /** Plain name without the indent marker, for confirmation messages. */
  name: string
  isModule: boolean
}

function compareForDisplay(left: Task, right: Task): number {
  if (left.sort_order !== right.sort_order) return left.sort_order - right.sort_order
  return left.created_at.localeCompare(right.created_at)
}

/**
 * The places a task can be filed under: every open project, each followed by
 * its own modules. Used both by the Today page (choosing where a newly
 * captured task belongs) and by the projects page (filing a 临时任务 later),
 * so the two lists can never drift apart.
 */
export function projectFilingTargets(tasks: Task[]): FilingTarget[] {
  const projects = tasks
    .filter(
      (task) =>
        task.node_type === 'PROJECT' &&
        task.status !== 'DONE' &&
        // 临时任务 is where a task waits to be filed, never a filing target.
        !isInboxProject(task),
    )
    .sort(compareForDisplay)
  const targets: FilingTarget[] = []
  for (const project of projects) {
    targets.push({
      id: project.id,
      label: project.title,
      name: project.title,
      isModule: false,
    })
    const modules = tasks
      .filter(
        (task) =>
          task.node_type === 'MODULE' &&
          task.parent_id === project.id &&
          task.status !== 'DONE',
      )
      .sort(compareForDisplay)
    for (const module of modules) {
      targets.push({
        id: module.id,
        label: `　└ ${module.title}`,
        name: module.title,
        isModule: true,
      })
    }
  }
  return targets
}
