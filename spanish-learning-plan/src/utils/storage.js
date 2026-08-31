const STORAGE_KEY = 'spanish-plan-state-v1'

export function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    return true
  } catch {
    return false
  }
}

export function serializeForExport(state) {
  return JSON.stringify(
    { ...state, exportedAt: new Date().toISOString() },
    null,
    2,
  )
}

export function parseImport(text) {
  const data = JSON.parse(text)
  if (typeof data !== 'object' || data === null) {
    throw new Error('備份檔案格式錯誤')
  }
  return data
}
