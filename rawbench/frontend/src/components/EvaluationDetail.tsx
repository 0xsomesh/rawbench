"use client"

import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { fetchResultDetail, type ResultDetail } from "../api/results"
import { Loader2 } from "lucide-react"
import EvalResultsViewer from "./EvalResultsViewer"

// Transform API result to match the expected EvaluationData format
function transformResultToEvaluationData(result: ResultDetail, filename: string) {
  return {
    id: filename,
    name: filename.replace(/\.json$/, '').replace(/_/g, ' '),
    description: `Evaluation results from ${filename}.json`,
    models: [], // Will be populated from actual results if needed
    status: "completed" as const,
    created_at: new Date().toISOString(), // Not available in API response
    duration: "N/A", // Not available in API response
    total_results: result.summary?.total_results || 0,
    avg_latency: result.summary?.avg_latency || 0,
    summary: result.summary || {},
    results: result.results || []
  }
}

export default function EvaluationDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [evaluation, setEvaluation] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const loadEvaluation = async () => {
      if (!id) {
        setError('Evaluation ID not provided')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        const result = await fetchResultDetail(decodeURIComponent(id))
        const transformedEvaluation = transformResultToEvaluationData(result, decodeURIComponent(id))
        setEvaluation(transformedEvaluation)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load evaluation')
        console.error('Error loading evaluation:', err)
      } finally {
        setLoading(false)
      }
    }

    loadEvaluation()
  }, [id])
  
  if (!id) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold text-gray-600 mb-2">Evaluation not found</h1>
            <p className="text-gray-500 mb-4">No evaluation ID provided.</p>
            <button
              onClick={() => navigate("/")}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Back to Evaluations
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-500 mb-2">Loading evaluation...</h3>
          </div>
        </div>
      </div>
    )
  }

  if (error || !evaluation) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold text-gray-600 mb-2">Evaluation not found</h1>
            <p className="text-gray-500 mb-4">{error || `The evaluation with ID "${id}" could not be found.`}</p>
            <button
              onClick={() => navigate("/")}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Back to Evaluations
            </button>
          </div>
        </div>
      </div>
    )
  }

  const handleBack = () => {
    navigate("/")
  }

  return <EvalResultsViewer evaluation={evaluation} onBack={handleBack} />
}
