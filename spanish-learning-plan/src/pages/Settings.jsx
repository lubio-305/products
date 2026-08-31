import { useRef, useState } from 'react'
import { useAppState } from '../state/AppStateContext.jsx'
import Card from '../components/Card.jsx'

function requestNotificationPermission() {
  if (!('Notification' in window)) return Promise.resolve('unsupported')
  return Notification.requestPermission()
}

export default function Settings() {
  const { state, updateSettings, exportBackup, importBackup } = useAppState()
  const fileRef = useRef(null)
  const [message, setMessage] = useState('')

  async function toggleNotifications(e) {
    const enabled = e.target.checked
    if (enabled) {
      const perm = await requestNotificationPermission()
      if (perm !== 'granted') {
        setMessage('瀏覽器未授權通知權限，請至瀏覽器設定允許通知。')
        updateSettings({ notificationsEnabled: false })
        return
      }
    }
    updateSettings({ notificationsEnabled: enabled })
    setMessage('')
  }

  function download() {
    const text = exportBackup()
    const blob = new Blob([text], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `spanish-plan-backup-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  function handleImport(e) {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        importBackup(reader.result)
        setMessage('匯入成功！')
      } catch {
        setMessage('匯入失敗，檔案格式不正確。')
      }
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  return (
    <div className="space-y-4">
      <Card title="每日提醒通知">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={state.settings.notificationsEnabled}
            onChange={toggleNotifications}
            className="h-4 w-4 accent-emerald-600"
          />
          啟用瀏覽器提醒（需授權，且僅在此分頁開啟時觸發）
        </label>
        {state.settings.notificationsEnabled && (
          <label className="block text-sm mt-3">
            提醒時間
            <input
              type="time"
              value={state.settings.reminderTime}
              onChange={(e) => updateSettings({ reminderTime: e.target.value })}
              className="mt-1 block rounded-lg border border-black/10 dark:border-white/20 bg-transparent px-3 py-2"
            />
          </label>
        )}
        <p className="text-xs text-black/40 dark:text-white/40 mt-2">
          由於這是免登入的純前端工具，瀏覽器關閉時無法推播通知，建議把此頁面加到手機主畫面
          （分享 → 加入主畫面），開啟分頁時就會依提醒時間跳出通知。
        </p>
      </Card>

      <Card title="資料備份">
        <p className="text-sm text-black/60 dark:text-white/60 mb-3">
          進度只存在這個瀏覽器裡，清除瀏覽器資料或換裝置會遺失，建議定期匯出備份。
        </p>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={download}
            className="px-4 py-2 rounded-full bg-emerald-600 text-white text-sm"
          >
            匯出備份檔案
          </button>
          <button
            onClick={() => fileRef.current?.click()}
            className="px-4 py-2 rounded-full border border-black/20 dark:border-white/20 text-sm"
          >
            匯入備份檔案
          </button>
          <input
            ref={fileRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={handleImport}
          />
        </div>
        {message && <p className="text-sm text-emerald-600 mt-2">{message}</p>}
      </Card>
    </div>
  )
}
