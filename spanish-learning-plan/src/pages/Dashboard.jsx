import { Link } from 'react-router-dom'
import { useAppState } from '../state/AppStateContext.jsx'
import Card from '../components/Card.jsx'
import ProgressBar from '../components/ProgressBar.jsx'
import Countdown from '../components/Countdown.jsx'
import { stageProgress, todayISO } from '../utils/dates'
import CheckpointBanner from '../components/CheckpointBanner.jsx'

export default function Dashboard() {
  const {
    currentStage,
    getTasksForDate,
    toggleTask,
    state,
    computeStreak,
    weeklySpeakingProgress,
  } = useAppState()

  const today = todayISO()
  const tasks = getTasksForDate(today)
  const doneIds = state.dailyLog[today]?.taskIds || []
  const streak = computeStreak(today)
  const progress = stageProgress(currentStage, today)
  const speaking = currentStage.speakingGoal
    ? weeklySpeakingProgress(today)
    : null

  return (
    <div className="space-y-4">
      <Card>
        <Countdown />
      </Card>

      <CheckpointBanner />

      <Card title={`目前階段：${currentStage.name}（目標 ${currentStage.targetLevel}）`}>
        <p className="text-sm text-black/60 dark:text-white/60 mb-3">
          {currentStage.focus}
        </p>
        <ProgressBar value={progress} />
        <p className="text-xs text-black/40 dark:text-white/40 mt-1">
          階段進度 {Math.round(progress * 100)}%
        </p>
      </Card>

      <Card title="今日任務">
        <ul className="space-y-2">
          {tasks.map((t) => {
            const checked = doneIds.includes(t.id)
            return (
              <li key={t.id}>
                <label className="flex items-center gap-3 p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleTask(t.id, today)}
                    className="h-5 w-5 accent-emerald-600"
                  />
                  <span className={checked ? 'line-through text-black/40 dark:text-white/40' : ''}>
                    {t.label}
                  </span>
                  <span className="ml-auto text-xs text-black/40 dark:text-white/40">
                    {t.minutes} 分
                  </span>
                </label>
              </li>
            )
          })}
        </ul>
        <div className="mt-4 flex items-center justify-between text-sm">
          <span>
            🔥 連續打卡 <strong>{streak.current}</strong> 天（最佳 {streak.longest} 天）
          </span>
          <Link to="/flashcards" className="text-emerald-600 hover:underline">
            去複習單字卡 →
          </Link>
        </div>
      </Card>

      {speaking && (
        <Card title="本週口說練習目標">
          <p className="text-sm text-black/60 dark:text-white/60 mb-2">
            目標：每週 {currentStage.speakingGoal.sessionsPerWeek} 次，每次約{' '}
            {currentStage.speakingGoal.minutesPerSession} 分鐘
          </p>
          <ProgressBar
            value={speaking.sessions / currentStage.speakingGoal.sessionsPerWeek}
            color="bg-sky-600"
          />
          <p className="text-xs text-black/40 dark:text-white/40 mt-1">
            本週已完成 {speaking.sessions} 次，共 {speaking.minutes} 分鐘
          </p>
          <Link to="/speaking" className="text-sky-600 hover:underline text-sm mt-2 inline-block">
            記錄口說練習 →
          </Link>
        </Card>
      )}
    </div>
  )
}
