import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App.tsx"
import "./globals.css"

/* ------------------------------------------------------------------ */
/*  Ensure a valid mount node even if "#root" is missing in preview   */
/* ------------------------------------------------------------------ */
const mountNode =
  document.getElementById("root") ??
  (() => {
    const div = document.createElement("div")
    document.body.appendChild(div)
    return div
  })()

ReactDOM.createRoot(mountNode).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
