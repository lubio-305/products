import { useMemo, useState } from 'react'
import { useAppState } from '../state/AppStateContext.jsx'
import Card from '../components/Card.jsx'

export default function Flashcards() {
  const { getDueFlashcards, reviewFlashcard, state, currentStage, stages } =
    useAppState()
  const dueCards = useMemo(() => getDueFlashcards(), [state.flashcards, currentStage])

  const [queue, setQueue] = useState(null)
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)

  const unlockedCount = useMemo(() => {
    const unlockedStageIds = new Set(
      stages.filter((s) => s.order <= currentStage.order).map((s) => s.id),
    )
    return state.flashcards.filter((c) => unlockedStageIds.has(c.stageId)).length
  }, [state.flashcards, stages, currentStage])

  function startSession() {
    setQueue(dueCards.map((c) => c.id))
    setIndex(0)
    setRevealed(false)
  }

  function answer(remembered) {
    reviewFlashcard(queue[index], remembered)
    setRevealed(false)
    if (index + 1 < queue.length) {
      setIndex(index + 1)
    } else {
      setQueue(null)
    }
  }

  const current = queue ? state.flashcards.find((c) => c.id === queue[index]) : null

  return (
    <div className="space-y-4">
      <Card title="單字卡間隔複習">
        <p className="text-sm text-black/60 dark:text-white/60">
          今日待複習：<strong>{dueCards.length}</strong> 張，目前已解鎖題庫共{' '}
          {unlockedCount} 張
        </p>
        {!queue && (
          <button
            disabled={dueCards.length === 0}
            onClick={startSession}
            className="mt-3 px-4 py-2 rounded-full bg-emerald-600 text-white text-sm disabled:opacity-40"
          >
            {dueCards.length === 0 ? '今天沒有待複習的卡片 🎉' : '開始複習'}
          </button>
        )}
      </Card>

      {current && (
        <Card>
          <p className="text-xs text-black/40 dark:text-white/40 mb-2">
            {index + 1} / {queue.length}
          </p>
          <div
            onClick={() => setRevealed(true)}
            className="min-h-40 flex flex-col items-center justify-center text-center cursor-pointer select-none"
          >
            <p className="text-2xl font-bold">{current.front}</p>
            {revealed && (
              <p className="text-lg text-emerald-600 mt-3">{current.back}</p>
            )}
            {!revealed && (
              <p className="text-xs text-black/30 dark:text-white/30 mt-4">
                點擊卡片顯示答案
              </p>
            )}
          </div>
          {revealed && (
            <div className="flex gap-2 mt-4">
              <button
                onClick={() => answer(false)}
                className="flex-1 py-2 rounded-full bg-rose-600 text-white text-sm"
              >
                不記得
              </button>
              <button
                onClick={() => answer(true)}
                className="flex-1 py-2 rounded-full bg-emerald-600 text-white text-sm"
              >
                記得
              </button>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
