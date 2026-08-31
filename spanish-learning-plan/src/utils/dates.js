const DAY_MS = 24 * 60 * 60 * 1000

export function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export function parseISO(iso) {
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y, m - 1, d)
}

export function daysBetween(fromISO, toISO) {
  const from = parseISO(fromISO)
  const to = parseISO(toISO)
  return Math.round((to - from) / DAY_MS)
}

export function addDays(iso, days) {
  const d = parseISO(iso)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

export function formatDate(iso) {
  const d = parseISO(iso)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(
    d.getDate(),
  ).padStart(2, '0')}`
}

export function monthsBetween(fromISO, toISO) {
  const from = parseISO(fromISO)
  const to = parseISO(toISO)
  return (
    (to.getFullYear() - from.getFullYear()) * 12 +
    (to.getMonth() - from.getMonth())
  )
}

export function getCurrentStage(stages, todayIso = todayISO()) {
  const found = stages.find((s) => todayIso >= s.start && todayIso <= s.end)
  if (found) return found
  if (todayIso < stages[0].start) return stages[0]
  return stages[stages.length - 1]
}

export function stageProgress(stage, todayIso = todayISO()) {
  const total = daysBetween(stage.start, stage.end)
  const done = Math.min(Math.max(daysBetween(stage.start, todayIso), 0), total)
  return total <= 0 ? 1 : done / total
}

export function overallProgress(stages, todayIso = todayISO()) {
  const total = daysBetween(stages[0].start, stages[stages.length - 1].end)
  const done = Math.min(
    Math.max(daysBetween(stages[0].start, todayIso), 0),
    total,
  )
  return total <= 0 ? 1 : done / total
}

export function isoWeek(iso) {
  const d = parseISO(iso)
  const day = (d.getDay() + 6) % 7
  d.setDate(d.getDate() - day)
  return d.toISOString().slice(0, 10)
}
