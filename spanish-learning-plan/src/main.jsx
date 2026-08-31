import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import { AppStateProvider } from './state/AppStateContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HashRouter>
      <AppStateProvider>
        <App />
      </AppStateProvider>
    </HashRouter>
  </StrictMode>,
)
