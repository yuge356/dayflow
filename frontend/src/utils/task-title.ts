import type { Task } from '@/types/task'
import { isInboxProject } from './task-filing'

export function projectPrefixedTaskTitle(task: Task, tasks: Task[]): string {
  if (task.node_type === 'PROJECT') return task.title

  const tasksById = new Map(tasks.map((candidate) => [candidate.id, candidate]))
  const visited = new Set<string>()
  let current: Task | undefined = task
  while (current.parent_id && !visited.has(current.id)) {
    visited.add(current.id)
    const parent: Task | undefined = tasksById.get(current.parent_id)
    if (!parent) break
    if (parent.node_type === 'PROJECT') {
      // 临时任务 is a holding area, not a project the user named.
      if (isInboxProject(parent)) return task.title
      return `${parent.title}/${task.title}`.slice(0, 200)
    }
    current = parent
  }
  return task.title
}
