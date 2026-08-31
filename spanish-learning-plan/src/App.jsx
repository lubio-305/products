import { Routes, Route } from 'react-router-dom'
import Nav from './components/Nav.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Progress from './pages/Progress.jsx'
import Flashcards from './pages/Flashcards.jsx'
import Speaking from './pages/Speaking.jsx'
import Resources from './pages/Resources.jsx'
import Settings from './pages/Settings.jsx'
import useReminder from './hooks/useReminder.js'

export default function App() {
  useReminder()

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-black/10 dark:border-white/10 bg-white/70 dark:bg-black/20 backdrop-blur sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
          <h1 className="text-lg font-semibold flex items-center gap-2">
            <span>⚽</span>
            <span>2030 世界盃西語計畫</span>
          </h1>
        </div>
        <Nav />
      </header>

      <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/flashcards" element={<Flashcards />} />
          <Route path="/speaking" element={<Speaking />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>

      <footer className="text-center text-xs text-black/40 dark:text-white/30 py-4">
        資料僅儲存在此瀏覽器裝置上，記得定期到「設定」匯出備份。
      </footer>
    </div>
  )
}
