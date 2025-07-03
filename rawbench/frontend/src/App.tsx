"use client"

import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import EvaluationsList from "./components/EvaluationsList"
import EvaluationDetail from "./components/EvaluationDetail"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<EvaluationsList />} />
        <Route path="/evaluation/:id" element={<EvaluationDetail />} />
      </Routes>
    </Router>
  )
}

export default App
