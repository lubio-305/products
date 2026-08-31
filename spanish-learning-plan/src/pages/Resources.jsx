import { useState } from 'react'
import { useAppState } from '../state/AppStateContext.jsx'
import { resources } from '../data/resources'
import Card from '../components/Card.jsx'

export default function Resources() {
  const { currentStage } = useAppState()
  const [onlyCurrent, setOnlyCurrent] = useState(true)

  const list = resources.filter(
    (r) => !onlyCurrent || r.stages.includes(currentStage.id),
  )

  return (
    <div className="space-y-4">
      <Card title="免費學習資源庫">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={onlyCurrent}
            onChange={(e) => setOnlyCurrent(e.target.checked)}
            className="h-4 w-4 accent-emerald-600"
          />
          只顯示適合目前階段（{currentStage.name}）的資源
        </label>
      </Card>

      <div className="space-y-3">
        {list.map((r) => (
          <Card key={r.id}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <a
                  href={r.url}
                  target="_blank"
                  rel="noreferrer"
                  className="font-semibold text-emerald-700 dark:text-emerald-400 hover:underline"
                >
                  {r.name}
                </a>
                <p className="text-xs text-black/40 dark:text-white/40 mt-0.5">
                  {r.type} ・ {r.skill}
                </p>
                <p className="text-sm text-black/60 dark:text-white/60 mt-2">
                  {r.note}
                </p>
              </div>
            </div>
          </Card>
        ))}
        {list.length === 0 && (
          <p className="text-sm text-black/40 dark:text-white/40 text-center py-6">
            此階段暫無標記資源，取消勾選以查看全部資源。
          </p>
        )}
      </div>
    </div>
  )
}
