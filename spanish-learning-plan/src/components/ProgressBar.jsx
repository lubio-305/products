export default function ProgressBar({ value, className = '', color = 'bg-emerald-600' }) {
  const pct = Math.round(Math.min(Math.max(value, 0), 1) * 100)
  return (
    <div
      className={`w-full h-2.5 rounded-full bg-black/10 dark:bg-white/10 overflow-hidden ${className}`}
    >
      <div
        className={`h-full ${color} transition-all`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}
