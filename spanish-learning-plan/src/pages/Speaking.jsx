import { useState } from 'react'
import { useAppState } from '../state/AppStateContext.jsx'
import Card from '../components/Card.jsx'
import ProgressBar from '../components/ProgressBar.jsx'
import { formatDate } from '../utils/dates'

export default function Speaking() {
  const {
    currentStage,
    weeklySpeakingProgress,
    addSpeakingSession,
    removeSpeakingSession,
    state,
  } = useAppState()
  const [minutes, setMinutes] = useState(15)
  const [note, setNote] = useState('')

  if (!currentStage.speakingGoal) {
    return (
      <Card title="口說練習追蹤">
        <p className="text-sm text-black/60 dark:text-white/60">
          口說追蹤會從「A1 → A2」階段開始。目前階段（{currentStage.name}
          ）先專注在發音與基礎句型，口說可以先用朗讀、自言自語練習，包含在每日任務裡就好。
        </p>
      </Card>
    )
  }

  const weekly = weeklySpeakingProgress()
  const goal = currentStage.speakingGoal

  function submit(e) {
    e.preventDefault()
    addSpeakingSession(Number(minutes), note)
    setNote('')
  }

  return (
    <div className="space-y-4">
      <Card title="本週口說練習">
        <p className="text-sm text-black/60 dark:text-white/60 mb-2">
          目標：每週 {goal.sessionsPerWeek} 次，每次約 {goal.minutesPerSession} 分鐘
        </p>
        <ProgressBar value={weekly.sessions / goal.sessionsPerWeek} color="bg-sky-600" />
        <p className="text-xs text-black/40 dark:text-white/40 mt-1">
          本週已完成 {weekly.sessions} 次，共 {weekly.minutes} 分鐘
        </p>
      </Card>

      <Card title="新增一次練習紀錄">
        <form onSubmit={submit} className="space-y-3">
          <label className="block text-sm">
            練習時長（分鐘）
            <input
              type="number"
              min="1"
              value={minutes}
              onChange={(e) => setMinutes(e.target.value)}
              className="mt-1 w-full rounded-lg border border-black/10 dark:border-white/20 bg-transparent px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            心得／對象（選填，例如：Tandem語伴、自言自語）
            <input
              type="text"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="mt-1 w-full rounded-lg border border-black/10 dark:border-white/20 bg-transparent px-3 py-2"
            />
          </label>
          <button
            type="submit"
            className="px-4 py-2 rounded-full bg-sky-600 text-white text-sm"
          >
            記錄練習
          </button>
        </form>
      </Card>

      <Card title="最近紀錄">
        {state.speakingLog.length === 0 && (
          <p className="text-sm text-black/40 dark:text-white/40">尚無紀錄</p>
        )}
        <ul className="space-y-2">
          {[...state.speakingLog]
            .reverse()
            .slice(0, 20)
            .map((s) => (
              <li
                key={s.id}
                className="flex items-center justify-between text-sm border-b border-black/5 dark:border-white/10 pb-2"
              >
                <span>
                  {formatDate(s.date)} ・ {s.minutes} 分鐘
                  {s.note && ` ・ ${s.note}`}
                </span>
                <button
                  onClick={() => removeSpeakingSession(s.id)}
                  className="text-black/30 hover:text-rose-600 text-xs"
                >
                  刪除
                </button>
              </li>
            ))}
        </ul>
      </Card>
    </div>
  )
}
