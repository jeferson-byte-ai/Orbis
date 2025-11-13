import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './AppWithAuth.tsx'
import './index.css'

// Note: StrictMode disabled to prevent double OAuth callback execution in development
// Re-enable for production builds
ReactDOM.createRoot(document.getElementById('root')!).render(
  <App />
)