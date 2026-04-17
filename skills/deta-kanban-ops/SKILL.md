---
name: deta-kanban-ops
description: Convenciones compartidas de los Kanbans drag-drop en DETA Ops (LeadsKanban, TasksKanban, ProjectsList). Actívate con "kanban", "drag", "dnd", "dnd-kit", "drop", "optimistic", "columna", o cuando el usuario toque `components/leads/LeadsKanban.tsx`, `components/tasks/TasksKanban.tsx` o pida un nuevo Kanban en DETA Ops.
---

# DETA Ops — Kanbans drag-drop

Patrón unificado para todos los Kanbans del app. Basado en `@dnd-kit/core` (no sortable, sólo draggable + droppable).

## Stack

- `@dnd-kit/core`: `DndContext`, `useDraggable`, `useDroppable`, `DragEndEvent`, `PointerSensor` con `activationConstraint: { distance: 6 }` para permitir click.
- `useOptimistic` de React 19 para reflejar el movimiento instantáneo.
- `useTransition` + server action + `router.refresh()` para persistir.

## Estructura estándar

```tsx
'use client'
// imports...

export function XKanban({ items }: Props) {
  const [optimistic, setOptimistic] = useOptimistic(items, (state, update: { id; stage }) =>
    state.map((it) => (it.id === update.id ? { ...it, stage: update.stage } : it))
  )
  const [, startTransition] = useTransition()
  const router = useRouter()
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }))

  function onDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (!over) return
    const newStage = over.id as Stage
    const id = active.id as string
    const current = optimistic.find((i) => i.id === id)
    if (!current || current.stage === newStage) return
    startTransition(async () => {
      setOptimistic({ id, stage: newStage })
      const res = await updateStageAction(id, newStage)
      if (res.ok) router.refresh()
    })
  }

  return (
    <DndContext sensors={sensors} onDragEnd={onDragEnd}>
      <div className="grid grid-cols-N gap-4">
        {STAGES.map((s) => (
          <Column key={s} stage={s} items={optimistic.filter((i) => i.stage === s)} />
        ))}
      </div>
    </DndContext>
  )
}
```

## Column + Card (evita button-in-button)

- Card usa `<div>` con `tabIndex={0}` + `role="button"` (no `<button>`) porque dnd-kit listeners capturan clicks.
- Para navegar a la ficha, usar `<Link>` hijo con `onClick={(e) => e.stopPropagation()}` si hace falta.
- `useDraggable({ id: item.id })` aplica `listeners` + `attributes` al Card.
- `useDroppable({ id: stage })` en la Column.

## Convenciones DETA

- **Labels** como objeto `STAGE_LABEL: Record<Stage, string>` en el mismo archivo del Kanban (no en schema).
- **Colores** de prioridad/stage: usar tokens (`--color-navy-900`, `--color-cyan-600`) o clases Tailwind (`bg-amber-100 text-amber-800`). No hardcodear hex.
- **Transform** del Card mientras drag: `style={{ transform: CSS.Translate.toString(transform) }}`.
- Al soltar fuera de una droppable, `over` es `null` → no hacer nada (no revertir manualmente, optimistic ya estaba en el stage original).

## Server action requerida

```ts
export async function updateXStageAction(id: string, stage: Stage): Promise<Result> {
  const session = await auth()
  if (!session?.user) return { ok: false, error: 'unauthorized' }
  try {
    await db.update(table).set({ stage, updatedAt: new Date() }).where(eq(table.id, id))
    revalidatePath('/ruta')
    return { ok: true, data: null }
  } catch (e) {
    return { ok: false, error: 'server_error' }
  }
}
```

Para tasks: `updateTaskStatusAction` setea `completedAt = status === 'done' ? new Date() : null`.

## Checklist al crear un nuevo Kanban

- [ ] Server component fetchea items y los pasa serializados (ISO dates)
- [ ] Client component con `'use client'`, `useOptimistic`, `useTransition`
- [ ] Enum de stages/status exportado desde `lib/<module>/schema.ts` como `const`
- [ ] Action `update<Entity>StageAction(id, stage)` en `lib/<module>/actions.ts`
- [ ] `revalidatePath` en la action
- [ ] Columns renderizadas por `STAGES.map`, no hardcoded
- [ ] Card con `<div>` + tabIndex, NO `<button>`
- [ ] Link a ficha con `stopPropagation` si hay conflicto de listeners

## Si el usuario pide…

- **"Ordenar dentro de la columna"** → migrar a `@dnd-kit/sortable`. Requiere `SortableContext` + `useSortable` (reemplaza `useDraggable`). Los items ganan campo `position int`.
- **"Multi-select drag"** → no soportado actualmente, requiere patrón distinto con `DragOverlay`.
- **"Que muestre cuántos items por columna"** → header de Column con `items.length`.
