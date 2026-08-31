import { daysBetween, todayISO, formatDate } from '../utils/dates'
import { WORLD_CUP_DATE } from '../data/stages'

export default function Countdown() {
  const days = daysBetween(todayISO(), WORLD_CUP_DATE)

  return (
    <div className="text-center">
      <p className="text-xs uppercase tracking-wide text-black/40 dark:text-white/40">
        距離 2030 世界盃（預估 {formatDate(WORLD_CUP_DATE)}）
      </p>
      <p className="text-4xl font-bold text-emerald-600 mt-1">
        {days.toLocaleString()} 天
      </p>
    </div>
  )
}
