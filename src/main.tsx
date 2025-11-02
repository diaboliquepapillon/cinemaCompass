import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Suppress harmless browser extension connection errors
const isExtensionError = (error: any): boolean => {
  const errorString = error?.toString?.() || String(error || '')
  return errorString.includes('Receiving end does not exist') ||
         errorString.includes('Could not establish connection') ||
         errorString.includes('Extension context invalidated')
}

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  if (isExtensionError(event.reason)) {
    event.preventDefault()
    event.stopPropagation()
    return false
  }
})

// Handle general errors
window.addEventListener('error', (event) => {
  if (isExtensionError(event.error || event.message)) {
    event.preventDefault()
    event.stopPropagation()
    return false
  }
})

// Suppress console errors from extensions
const originalError = console.error
console.error = (...args: any[]) => {
  if (args.some(arg => isExtensionError(arg))) {
    return // Ignore extension errors
  }
  originalError.apply(console, args)
}

createRoot(document.getElementById("root")!).render(<App />);
