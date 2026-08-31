import { useEffect, useRef } from 'react'
import { useAppState } from '../state/AppStateContext.jsx'
import { todayISO } from '../utils/dates'

export default function useReminder() {
  const { state } = useAppState()
  const lastFired = useRef(null)

  useEffect(() => {
    const { notificationsEnabled, reminderTime } = state.settings
    if (!notificationsEnabled || !('Notification' in window)) return

    const check = () => {
      if (Notification.permission !== 'granted') return
      const today = todayISO()
      const done = state.dailyLog[today]?.done
      if (done) return

      const now = new Date()
      const current = `${String(now.getHours()).padStart(2, '0')}:${String(
        now.getMinutes(),
      ).padStart(2, '0')}`
      if (current === reminderTime && lastFired.current !== today) {
        lastFired.current = today
        new Notification('西班牙語學習提醒 ⚽', {
          body: '今天的 30-60 分鐘還沒完成，來複習一下吧！',
        })
      }
    }

    const id = setInterval(check, 30 * 1000)
    return () => clearInterval(id)
  }, [state.settings, state.dailyLog])
}
