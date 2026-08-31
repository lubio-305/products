import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { stages as stageDefs } from '../data/stages'
import { flashcardSeeds } from '../data/flashcards'
import { loadState, saveState, serializeForExport, parseImport } from '../utils/storage'
import { initCardState, reviewCard, dueCards } from '../utils/srs'
import { addDays, todayISO, isoWeek, getCurrentStage, monthsBetween } from '../utils/dates'

const AppStateContext = createContext(null)

function defaultState() {
  return {
    dailyLog: {},
    flashcards: flashcardSeeds.map(initCardState),
    speakingLog: [],
    checkpointsReviewed: {},
    scheduleShiftDays: 0,
    settings: {
      notificationsEnabled: false,
      reminderTime: '19:00',
    },
  }
}

function mergeWithDefaults(loaded) {
  const base = defaultState()
  if (!loaded) return base
  return {
    ...base,
    ...loaded,
    flashcards:
      Array.isArray(loaded.flashcards) && loaded.flashcards.length > 0
        ? loaded.flashcards
        : base.flashcards,
    settings: { ...base.settings, ...(loaded.settings || {}) },
  }
}

export function AppStateProvider({ children }) {
  const [state, setState] = useState(() => mergeWithDefaults(loadState()))

  useEffect(() => {
    saveState(state)
  }, [state])

  function getEffectiveStages() {
    const shift = state.scheduleShiftDays || 0
    if (!shift) return stageDefs
    return stageDefs.map((s) => ({
      ...s,
      start: addDays(s.start, shift),
      end: addDays(s.end, shift),
    }))
  }

  const effectiveStages = useMemo(getEffectiveStages, [state.scheduleShiftDays])
  const currentStage = useMemo(
    () => getCurrentStage(effectiveStages),
    [effectiveStages],
  )

  function getTasksForDate(dateIso = todayISO()) {
    const stage = getCurrentStage(effectiveStages, dateIso)
    return stage.dailyTasks
  }

  function toggleTask(taskId, dateIso = todayISO()) {
    setState((prev) => {
      const stage = getCurrentStage(effectiveStages, dateIso)
      const entry = prev.dailyLog[dateIso] || { taskIds: [], done: false }
      const has = entry.taskIds.includes(taskId)
      const taskIds = has
        ? entry.taskIds.filter((id) => id !== taskId)
        : [...entry.taskIds, taskId]
      const done = taskIds.length >= stage.dailyTasks.length
      return {
        ...prev,
        dailyLog: {
          ...prev.dailyLog,
          [dateIso]: { taskIds, done },
        },
      }
    })
  }

  function computeStreak(todayIso = todayISO()) {
    const log = state.dailyLog
    let cursor = todayIso
    if (!log[cursor]?.done) {
      cursor = addDays(cursor, -1)
    }
    let current = 0
    while (log[cursor]?.done) {
      current++
      cursor = addDays(cursor, -1)
    }
    const doneDates = Object.keys(log)
      .filter((d) => log[d].done)
      .sort()
    let longest = 0
    let run = 0
    let prev = null
    for (const d of doneDates) {
      run = prev && addDays(prev, 1) === d ? run + 1 : 1
      longest = Math.max(longest, run)
      prev = d
    }
    return { current, longest: Math.max(longest, current) }
  }

  function addSpeakingSession(minutes, note = '') {
    setState((prev) => ({
      ...prev,
      speakingLog: [
        ...prev.speakingLog,
        { id: `sp-${Date.now()}`, date: todayISO(), minutes, note },
      ],
    }))
  }

  function removeSpeakingSession(id) {
    setState((prev) => ({
      ...prev,
      speakingLog: prev.speakingLog.filter((s) => s.id !== id),
    }))
  }

  function weeklySpeakingProgress(todayIso = todayISO()) {
    const week = isoWeek(todayIso)
    const entries = state.speakingLog.filter((s) => isoWeek(s.date) === week)
    return {
      sessions: entries.length,
      minutes: entries.reduce((sum, e) => sum + e.minutes, 0),
      entries,
    }
  }

  function getDueFlashcards(todayIso = todayISO()) {
    const unlockedStageIds = effectiveStages
      .filter((s) => s.order <= currentStage.order)
      .map((s) => s.id)
    const unlocked = state.flashcards.filter((c) =>
      unlockedStageIds.includes(c.stageId),
    )
    return dueCards(unlocked, todayIso)
  }

  function reviewFlashcard(cardId, remembered) {
    setState((prev) => ({
      ...prev,
      flashcards: prev.flashcards.map((c) =>
        c.id === cardId ? reviewCard(c, remembered) : c,
      ),
    }))
  }

  function pendingCheckpoint(todayIso = todayISO()) {
    const months = monthsBetween(currentStage.start, todayIso)
    const reviewed = state.checkpointsReviewed[currentStage.id] || []
    const due = (currentStage.checkpointMonths || []).find(
      (m) => months >= m && !reviewed.includes(m),
    )
    return due ? { stageId: currentStage.id, month: due } : null
  }

  function resolveCheckpoint(stageId, month, extendDays = 0) {
    setState((prev) => ({
      ...prev,
      checkpointsReviewed: {
        ...prev.checkpointsReviewed,
        [stageId]: [...(prev.checkpointsReviewed[stageId] || []), month],
      },
      scheduleShiftDays: (prev.scheduleShiftDays || 0) + extendDays,
    }))
  }

  function updateSettings(partial) {
    setState((prev) => ({ ...prev, settings: { ...prev.settings, ...partial } }))
  }

  function exportBackup() {
    return serializeForExport(state)
  }

  function importBackup(text) {
    const data = parseImport(text)
    setState(mergeWithDefaults(data))
  }

  const value = {
    state,
    stages: effectiveStages,
    currentStage,
    getTasksForDate,
    toggleTask,
    computeStreak,
    addSpeakingSession,
    removeSpeakingSession,
    weeklySpeakingProgress,
    getDueFlashcards,
    reviewFlashcard,
    pendingCheckpoint,
    resolveCheckpoint,
    updateSettings,
    exportBackup,
    importBackup,
  }

  return (
    <AppStateContext.Provider value={value}>
      {children}
    </AppStateContext.Provider>
  )
}

export function useAppState() {
  const ctx = useContext(AppStateContext)
  if (!ctx) throw new Error('useAppState must be used within AppStateProvider')
  return ctx
}
