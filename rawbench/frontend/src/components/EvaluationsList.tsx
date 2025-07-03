"use client"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Calendar, TestTube, TrendingUp, Loader2 } from "lucide-react"
import { fetchResultsList, type ResultSummary } from "../api/results"

export default function EvaluationsList() {
  const navigate = useNavigate()
  const [evaluations, setEvaluations] = useState<ResultSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadEvaluations = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await fetchResultsList()
        setEvaluations(response.results)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load evaluations')
        console.error('Error loading evaluations:', err)
      } finally {
        setLoading(false)
      }
    }

    loadEvaluations()
  }, [])

  const handleSelectEvaluation = (evaluation: ResultSummary) => {
    navigate(`/evaluation/${encodeURIComponent(evaluation.filename.slice(0, -5))}`)
  }

  // Transform API data to match the expected format
  const transformedEvaluations = evaluations.map(evaluation => ({
    id: evaluation.filename,
    name: evaluation.filename.replace(/\.json$/, '').replace(/_/g, ' '),
    description: `Evaluation results from ${evaluation.filename}`,
    count_models: evaluation.summary.count_models,
    count_prompts: evaluation.summary.count_prompts,
    status: "completed" as const,
    created_at: evaluation.created_at,
    duration: "N/A", // Not available in API response
    total_results: evaluation.summary.total_results || 0,
    avg_latency: evaluation.summary.avg_latency || 0,
    summary: evaluation.summary,
    results: [] // Will be loaded when viewing details
  }))

  const filteredEvaluations = transformedEvaluations.filter(
    (evaluation) =>
      evaluation.name.toLowerCase() ||
      evaluation.description.toLowerCase(),
  )

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-500 mb-2">Loading evaluations...</h3>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <TestTube className="w-16 h-16 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-500 mb-2">Error loading evaluations</h3>
            <p className="text-gray-400 mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl mb-2">rawbench</h1>
          <p className="text-gray-600">
            View and analyze AI model evaluation results across different benchmarks and tests.
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center gap-3">
              <TestTube className="w-8 h-8 text-blue-600" />
              <div>
                <div className="text-2xl font-bold text-blue-600">{evaluations.length}</div>
                <div className="text-xs text-gray-500">Evaluation results</div>
              </div>
            </div>
          </div>
          {/* <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center gap-3">
              <Users className="w-8 h-8 text-green-600" />
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {evaluations.length}
                </div>
                <div className="text-xs text-gray-500">Evaluation files</div>
              </div>
            </div>
          </div> */}
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-8 h-8 text-purple-600" />
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {evaluations.reduce((sum, e) => sum + (e.summary.total_results || 0), 0)}
                </div>
                <div className="text-xs text-gray-500">Test cases</div>
              </div>
            </div>
          </div>
        </div>

        {/* Evaluations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEvaluations.map((evaluation) => (
            <button
              key={evaluation.id}
              onClick={() => handleSelectEvaluation(evaluations.find(e => e.filename === evaluation.id)!)}
              className="block bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-200 hover:shadow-lg hover:shadow-gray-200/50 text-left w-full"
            >
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">{evaluation.name}</h3>
                    {/* <p className="text-sm text-gray-600 line-clamp-2">{evaluation.description}</p> */}
                  </div>
                </div>

                {/* Models */}
                <div className="mb-4">
                  <div className="text-xs text-gray-500 mb-2">Models : {evaluation.count_models} | Prompts : {evaluation.count_prompts} | Tests : {evaluation.total_results}</div>
                  <div className="flex flex-wrap gap-1">
                    {/* {evaluation.models.slice(0, 3).map((model) => (
                      <span
                        key={model}
                        className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded border border-gray-200"
                      >
                        {model.split("-").pop()}
                      </span>
                    ))} */}
                    {/* {evaluation.models.length > 3 && (
                      <span className="px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded border border-gray-200">
                        +{evaluation.models.length - 3} more
                      </span>
                    )} */}
                  </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-lg font-bold text-blue-600">{evaluation.total_results}</div>
                    <div className="text-xs text-gray-500">Results</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-blue-600">{evaluation.avg_latency.toFixed(0)}ms</div>
                    <div className="text-xs text-gray-500">Avg Latency</div>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-gray-200">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(evaluation.created_at).toLocaleDateString()}
                  </div>
                  {/* <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {evaluation.duration}
                  </div> */}
                </div>
              </div>
            </button>
          ))}
        </div>

        {filteredEvaluations.length === 0 && (
          <div className="text-center py-12">
            <TestTube className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-500 mb-2">No evaluations found</h3>
            <p className="text-gray-400">Try adjusting your search query.</p>
          </div>
        )}
      </div>
    </div>
  )
}
