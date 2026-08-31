export default function Card({ title, children, className = '' }) {
  return (
    <section
      className={`bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-2xl p-4 shadow-sm ${className}`}
    >
      {title && <h2 className="font-semibold mb-3">{title}</h2>}
      {children}
    </section>
  )
}
