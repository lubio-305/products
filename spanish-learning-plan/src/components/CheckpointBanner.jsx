import { useState } from 'react'
import { useAppState } from '../state/AppStateContext.jsx'
import Card from './Card.jsx'

export default function CheckpointBanner() {
  const { pendingCheckpoint, resolveCheckpoint, currentStage } = useAppState()
  const [open, setOpen] = useState(true)
  const checkpoint = pendingCheckpoint()

  if (!checkpoint || !open) return null

  function handle(choice) {
    if (choice === 'ontrack') {
      resolveCheckpoint(checkpoint.stageId, checkpoint.month, 0)
    } else {
      resolveCheckpoint(checkpoint.stageId, checkpoint.month, 30)
    }
    setOpen(false)
  }

  return (
    <Card className="border-amber-400/60 bg-amber-50 dark:bg-amber-900/20">
      <p className="font-semibold text-amber-700 dark:text-amber-300">
        📋 階段檢核點：{currentStage.name}（第 {checkpoint.month} 個月）
      </p>
      <p className="text-sm text-black/60 dark:text-white/70 mt-1 mb-3">
        建議去 Instituto Cervantes 或其他免費資源做一次程度自我檢測，確認目前是否跟上進度。
      </p>
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => handle('ontrack')}
          className="px-3 py-1.5 rounded-full bg-emerald-600 text-white text-sm"
        >
          進度符合預期，繼續
        </button>
        <button
          onClick={() => handle('delay')}
          className="px-3 py-1.5 rounded-full bg-amber-600 text-white text-sm"
        >
          需要多一點時間，順延整體計畫約1個月
        </button>
      </div>
    </Card>
  )
}
