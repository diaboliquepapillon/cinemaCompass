import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Suppress browser extension connection errors (harmless)
const originalError = console.error
console.error = (...args: any[]) => {
  if (args[0]?.includes?.('Receiving end does not exist') || 
      args[0]?.includes?.('Could not establish connection')) {
    // Ignore browser extension errors
    return
  }
  originalError(...args)
}

createRoot(document.getElementById("root")!).render(<App />);
