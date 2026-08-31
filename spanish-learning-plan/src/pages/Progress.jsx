import { useAppState } from '../state/AppStateContext.jsx'
import Card from '../components/Card.jsx'
import ProgressBar from '../components/ProgressBar.jsx'
import { formatDate, stageProgress, overallProgress, todayISO } from '../utils/dates'

export default function Progress() {
  const { stages, currentStage, state } = useAppState()
  const today = todayISO()

  return (
    <div className="space-y-4">
      <Card title="整體進度（2026/09 → 2030/06）">
        <ProgressBar value={overallProgress(stages, today)} color="bg-emerald-600" />
        {state.scheduleShiftDays > 0 && (
          <p className="text-xs text-amber-600 mt-2">
            ⚠️ 目前計畫已因檢核點順延共 {state.scheduleShiftDays} 天，世界盃的時間不會變，
            代表後期的緩衝時間變少了，建議之後盡量維持每日進度。
          </p>
        )}
      </Card>

      <div className="space-y-3">
        {stages.map((stage) => {
          const status =
            today > stage.end ? 'done' : today < stage.start ? 'future' : 'active'
          return (
            <Card
              key={stage.id}
              className={status === 'future' ? 'opacity-50' : ''}
            >
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold">
                  {status === 'done' ? '✅ ' : status === 'active' ? '▶️ ' : '🔒 '}
                  {stage.order}. {stage.name}
                </h3>
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-600/10 text-emerald-700 dark:text-emerald-400">
                  目標 {stage.targetLevel}
                </span>
              </div>
              <p className="text-xs text-black/40 dark:text-white/40 mb-2">
                {formatDate(stage.start)} - {formatDate(stage.end)}
              </p>
              <p className="text-sm text-black/60 dark:text-white/60 mb-2">
                {stage.focus}
              </p>
              {status === 'active' && (
                <ProgressBar value={stageProgress(stage, today)} />
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}
