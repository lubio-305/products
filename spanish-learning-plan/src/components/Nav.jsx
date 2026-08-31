import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: '今日', end: true },
  { to: '/progress', label: '進度' },
  { to: '/flashcards', label: '單字卡' },
  { to: '/speaking', label: '口說' },
  { to: '/resources', label: '資源庫' },
  { to: '/settings', label: '設定' },
]

export default function Nav() {
  return (
    <nav className="max-w-3xl mx-auto px-2 flex gap-1 overflow-x-auto pb-2 text-sm">
      {links.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          end={l.end}
          className={({ isActive }) =>
            `px-3 py-1.5 rounded-full whitespace-nowrap transition-colors ${
              isActive
                ? 'bg-emerald-600 text-white'
                : 'text-black/60 dark:text-white/60 hover:bg-black/5 dark:hover:bg-white/10'
            }`
          }
        >
          {l.label}
        </NavLink>
      ))}
    </nav>
  )
}
