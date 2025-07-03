"use client"

import { useState, useMemo } from "react"
import { Grid3X3, List, TrendingUp, Eye, ArrowLeft } from "lucide-react"
import TestCaseCard from "./TestCaseCard"
// Define the EvaluationData interface locally since we're no longer using data.ts
interface EvaluationData {
  id: string
  name: string
  description: string
  models: string[]
  status: "completed" | "running" | "failed"
  created_at: string
  duration: string
  total_results: number
  avg_latency: number
  summary: {
    total_results: number
    total_tokens: number
    avg_latency: number
    [key: string]: any
  }
  results: any[]
}

type TestStatus = "success" | "incomplete" | "error"
type ViewMode = "overview" | "heatmap" | "focused" | "list"

interface Props {
  evaluation: EvaluationData
  onBack: () => void
}

function getTestStatus(test: any): TestStatus {
  if (!test.output_content || test.output_content.trim() === "") {
    return "incomplete"
  }
  if (test.output_content.includes("error") || test.output_content.includes("Error")) {
    return "error"
  }
  return "success"
}

function getModelColor(modelId: string): string {
  const colors: Record<string, string> = {
    "gpt-4o-mini-conservative": "bg-blue-500",
    "gpt-4o-mini-creative": "bg-purple-500",
    "gpt-4o": "bg-green-500",
    "claude-3": "bg-orange-500",
    gemini: "bg-red-500",
  }
  return colors[modelId] || "bg-gray-500"
}

function ModelBadge({ modelId, size = "sm" }: { modelId: string; size?: "sm" | "xs" }) {
  const sizeClass = size === "xs" ? "w-2 h-2" : "w-3 h-3"
  return (
    <span className={`inline-block ${sizeClass} rounded-full ${getModelColor(modelId)} mr-2`} title={modelId}></span>
  )
}

// Scalable Overview - Shows aggregated metrics first
function OverviewDashboard({ results }: { results: any[] }) {
  const models = [...new Set(results.map((r) => r.model_id))]
  const tests = [...new Set(results.map((r) => r.test_id))]

  const modelStats = models.map((modelId) => {
    const modelResults = results.filter((r) => r.model_id === modelId)
    const avgLatency = modelResults.reduce((sum, r) => sum + r.latency_ms, 0) / modelResults.length
    const avgTokens = modelResults.reduce((sum, r) => sum + r.total_tokens, 0) / modelResults.length
    const successRate = (modelResults.filter((r) => getTestStatus(r) === "success").length / modelResults.length) * 100

    return { modelId, avgLatency, avgTokens, successRate, count: modelResults.length }
  })

  return (
    <div className="space-y-6">
      {/* Model Performance Ranking */}
      <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Model Performance Ranking
        </h3>
        <div className="space-y-3">
          {modelStats
            .sort((a, b) => b.successRate - a.successRate || a.avgLatency - b.avgLatency)
            .map((stat, index) => (
              <div key={stat.modelId} className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-gray-500">#{index + 1}</span>
                  <ModelBadge modelId={stat.modelId} />
                  <span className="font-mono text-sm">{stat.modelId}</span>
                </div>
                <div className="flex gap-6 text-xs">
                  <div className="text-center">
                    <div className="text-gray-500">Latency</div>
                    <div className="font-bold text-blue-600">{stat.avgLatency.toFixed(0)}ms</div>
                  </div>
                  <div className="text-center">
                    <div className="text-gray-500">Tokens</div>
                    <div className="font-bold text-purple-600">{stat.avgTokens.toFixed(0)}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-gray-500">Tests</div>
                    <div className="font-bold text-gray-700">{stat.count}</div>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Test Coverage Matrix */}
      <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Test Coverage</h3>
        <div className="grid gap-2" style={{ gridTemplateColumns: `120px repeat(${Math.min(models.length, 6)}, 1fr)` }}>
          <div></div>
          {models.slice(0, 6).map((model) => (
            <div key={model} className="text-center text-xs">
              <ModelBadge modelId={model} size="xs" />
              {model.split("-").pop()}
            </div>
          ))}
          {models.length > 6 && <div className="text-center text-xs text-gray-500">+{models.length - 6} more</div>}

          {tests.map((testId) => (
            <div key={testId} className="contents">
              <div className="text-xs text-gray-700 py-1">{testId}</div>
              {models.slice(0, 6).map((modelId) => {
                const hasResult = results.some((r) => r.model_id === modelId && r.test_id === testId)
                return (
                  <div
                    key={`${modelId}-${testId}`}
                    className={`h-6 rounded ${hasResult ? "bg-green-500" : "bg-gray-300"}`}
                    title={`${modelId} - ${testId}: ${hasResult ? "✓" : "✗"}`}
                  ></div>
                )
              })}
              {models.length > 6 && <div className="h-6 bg-gray-300 rounded opacity-50"></div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Heatmap View - Shows performance metrics as colors
function HeatmapView({ results }: { results: any[] }) {
  const models = [...new Set(results.map((r) => r.model_id))]
  const tests = [...new Set(results.map((r) => r.test_id))]
  const [metric, setMetric] = useState<"latency" | "tokens" | "success">("latency")

  const getMetricValue = (result: any) => {
    switch (metric) {
      case "latency":
        return result.latency_ms
      case "tokens":
        return result.total_tokens
      case "success":
        return getTestStatus(result) === "success" ? 100 : 0
      default:
        return 0
    }
  }

  const getMetricColor = (value: number, allValues: number[]) => {
    const min = Math.min(...allValues)
    const max = Math.max(...allValues)
    const normalized = (value - min) / (max - min)

    if (metric === "latency") {
      // Lower is better for latency
      const intensity = Math.round((1 - normalized) * 255)
      return `rgb(${255 - intensity}, ${intensity}, 0)`
    } else {
      // Higher is better for tokens and success
      const intensity = Math.round(normalized * 255)
      return `rgb(${255 - intensity}, ${intensity}, 0)`
    }
  }

  const allValues = results.map(getMetricValue)

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <span className="text-sm text-gray-600">Metric:</span>
        {(["latency", "tokens", "success"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMetric(m)}
            className={`px-3 py-1 text-xs rounded ${
              metric === m ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm overflow-x-auto">
        <div className="min-w-max">
          <div className="grid gap-1" style={{ gridTemplateColumns: `120px repeat(${models.length}, 80px)` }}>
            <div></div>
            {models.map((model) => (
              <div key={model} className="text-center text-xs p-2">
                <ModelBadge modelId={model} size="xs" />
                <div>{model.split("-").pop()}</div>
              </div>
            ))}

            {tests.map((testId) => (
              <div key={testId} className="contents">
                <div className="text-xs text-gray-700 py-2 pr-2">{testId}</div>
                {models.map((modelId) => {
                  const result = results.find((r) => r.model_id === modelId && r.test_id === testId)
                  const value = result ? getMetricValue(result) : 0
                  const color = result ? getMetricColor(value, allValues) : "#D1D5DB"

                  return (
                    <div
                      key={`${modelId}-${testId}`}
                      className="h-12 rounded flex items-center justify-center text-xs font-bold text-white"
                      style={{ backgroundColor: color }}
                      title={
                        result
                          ? `${modelId} - ${testId}: ${value}${metric === "latency" ? "ms" : metric === "tokens" ? "t" : "%"}`
                          : "No result"
                      }
                    >
                      {result ? (metric === "success" ? (value === 100 ? "✓" : "✗") : value.toFixed(0)) : "-"}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Focused Comparison - Select specific items to compare
function FocusedComparison({
  results,
  expandedTests,
  toggleTest,
}: {
  results: any[]
  expandedTests: Set<string>
  toggleTest: (testId: string) => void
}) {
  const [selectedModels, setSelectedModels] = useState<string[]>([])
  const [selectedTest, setSelectedTest] = useState<string>("")

  const models = [...new Set(results.map((r) => r.model_id))]
  const tests = [...new Set(results.map((r) => r.test_id))]

  const comparisonResults = selectedTest
    ? results.filter(
        (r) => r.test_id === selectedTest && (selectedModels.length === 0 || selectedModels.includes(r.model_id)),
      )
    : []

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <h3 className="text-lg font-semibold mb-4">Select Items to Compare</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-600 mb-2">Test:</label>
            <select
              value={selectedTest}
              onChange={(e) => setSelectedTest(e.target.value)}
              className="bg-gray-100 border border-gray-300 rounded px-3 py-2 text-sm text-gray-700 w-full max-w-xs"
            >
              <option value="">Select a test</option>
              {tests.map((test) => (
                <option key={test} value={test}>
                  {test}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-2">Models (optional - leave empty for all):</label>
            <div className="flex flex-wrap gap-2">
              {models.map((modelId) => (
                <button
                  key={modelId}
                  onClick={() => {
                    if (selectedModels.includes(modelId)) {
                      setSelectedModels(selectedModels.filter((m) => m !== modelId))
                    } else {
                      setSelectedModels([...selectedModels, modelId])
                    }
                  }}
                  className={`flex items-center gap-1 px-3 py-1 text-xs rounded border transition-colors ${
                    selectedModels.includes(modelId)
                      ? "bg-blue-600 border-blue-600 text-white"
                      : "bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  <ModelBadge modelId={modelId} size="xs" />
                  {modelId.split("-").pop()}
                </button>
              ))}
            </div>
            {selectedModels.length > 0 && (
              <button
                onClick={() => setSelectedModels([])}
                className="mt-2 text-xs text-gray-500 hover:text-gray-700 underline"
              >
                Clear selection (show all models)
              </button>
            )}
          </div>
        </div>
      </div>

      {selectedTest && comparisonResults.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            {/* <h3 className="text-lg font-semibold">
              Comparing: <span className="text-blue-600">{selectedTest}</span>
            </h3> */}
            <div className="text-sm text-gray-600">
              {comparisonResults.length} result{comparisonResults.length !== 1 ? "s" : ""}
            </div>
          </div>

          {/* Use the same expandable component structure as list view */}
          <div className="space-y-4">
            {comparisonResults
              .sort((a, b) => a.latency_ms - b.latency_ms) // Sort by latency for easy comparison
              .map((result) => (
                <TestCaseCard
                  key={result.id}
                  result={result}
                  isExpanded={expandedTests.has(result.id)}
                  onToggle={() => toggleTest(result.id)}
                />
              ))}
          </div>
        </div>
      )}

      {selectedTest && comparisonResults.length === 0 && (
        <div className="text-center py-12 text-gray-600">
          No results found for the selected test and model filters.
        </div>
      )}
    </div>
  )
}

export default function EvalResultsViewer({ evaluation, onBack }: Props) {
  const [viewMode, setViewMode] = useState<ViewMode>("overview")
  const [selectedModelsFilter, setSelectedModelsFilter] = useState<string[]>([])
  const [selectedPromptsFilter, setSelectedPromptsFilter] = useState<string[]>([])
  const [selectedTestsFilter, setSelectedTestsFilter] = useState<string[]>([])
  const [searchQuery, _] = useState("")
  const [expandedTests, setExpandedTests] = useState<Set<string>>(new Set())

  // Add toggle function
  const toggleTest = (testId: string) => {
    const newExpanded = new Set(expandedTests)
    if (newExpanded.has(testId)) {
      newExpanded.delete(testId)
    } else {
      newExpanded.add(testId)
    }
    setExpandedTests(newExpanded)
  }

  const models = [...new Set(evaluation.results.map((r) => r.model_id))]
  const prompts = [...new Set(evaluation.results.map((r) => r.prompt_id))]
  const tests = [...new Set(evaluation.results.map((r) => r.test_id))]

  const filteredResults = useMemo(() => {
    return evaluation.results.filter((result) => {
      if (viewMode === "list") {
        // Use multi-select filters for list view
        const modelMatch = selectedModelsFilter.length === 0 || selectedModelsFilter.includes(result.model_id)
        const promptMatch = selectedPromptsFilter.length === 0 || selectedPromptsFilter.includes(result.prompt_id)
        const testMatch = selectedTestsFilter.length === 0 || selectedTestsFilter.includes(result.test_id)
        return modelMatch && promptMatch && testMatch
      } else {
        // Use search for other views
        const searchMatch =
          searchQuery === "" ||
          result.test_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          result.model_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          result.prompt_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          result.output_content?.toLowerCase().includes(searchQuery.toLowerCase())
        return searchMatch
      }
    })
  }, [viewMode, selectedModelsFilter, selectedPromptsFilter, selectedTestsFilter, searchQuery, evaluation.results])

  // Calculate summary statistics
  const results = evaluation.results
  const avgLatency = results.reduce((sum, r) => sum + r.latency_ms, 0) / results.length
  const avgTokens = results.reduce((sum, r) => sum + r.total_tokens, 0) / results.length

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 p-6 bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded border border-gray-300 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Dashboard
            </button>
          </div>
          <h1 className="text-2xl font-bold mb-2">{evaluation.name}</h1>
          <p className="text-gray-600 mb-4">{evaluation.description}</p>
          <p className="text-gray-600">
            {models.length} models • {prompts.length} prompts • {tests.length} tests •{" "}
            {new Date(evaluation.created_at).toLocaleString()}
          </p>
        </div>

        {/* Summary Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="text-2xl font-bold text-blue-600">{results.length}</div>
            <div className="text-sm text-gray-600">Total Results</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="text-2xl font-bold text-purple-600">{avgLatency.toFixed(0)}ms</div>
            <div className="text-sm text-gray-600">Avg Latency</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
            <div className="text-2xl font-bold text-orange-600">{avgTokens.toFixed(0)}</div>
            <div className="text-sm text-gray-600">Avg Tokens</div>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="mb-6 space-y-4">
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setViewMode("overview")}
              className={`flex items-center gap-2 px-3 py-2 text-sm rounded border transition-colors ${
                viewMode === "overview"
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              Overview
            </button>
            <button
              onClick={() => setViewMode("heatmap")}
              className={`flex items-center gap-2 px-3 py-2 text-sm rounded border transition-colors ${
                viewMode === "heatmap"
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <Grid3X3 className="w-4 h-4" />
              Heatmap
            </button>
            <button
              onClick={() => setViewMode("focused")}
              className={`flex items-center gap-2 px-3 py-2 text-sm rounded border transition-colors ${
                viewMode === "focused"
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <Eye className="w-4 h-4" />
              Focused
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`flex items-center gap-2 px-3 py-2 text-sm rounded border transition-colors ${
                viewMode === "list"
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200"
              }`}
            >
              <List className="w-4 h-4" />
              List
            </button>
          </div>

          {/* Filters for List View */}
          {viewMode === "list" && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-2">Models:</label>
                <div className="space-y-2">
                  <div className="flex flex-wrap gap-2">
                    {selectedModelsFilter.map((modelId) => (
                      <span
                        key={modelId}
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-600 text-white rounded"
                      >
                        <ModelBadge modelId={modelId} size="xs" />
                        {modelId.split("-").pop()}
                        <button
                          onClick={() => setSelectedModelsFilter(selectedModelsFilter.filter((m) => m !== modelId))}
                          className="ml-1 hover:bg-blue-700 rounded px-1"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {models
                      .filter((model) => !selectedModelsFilter.includes(model))
                      .map((model) => (
                        <button
                          key={model}
                          onClick={() => setSelectedModelsFilter([...selectedModelsFilter, model])}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded border border-gray-300 hover:bg-gray-200"
                        >
                          <ModelBadge modelId={model} size="xs" />
                          {model.split("-").pop()}
                        </button>
                      ))}
                  </div>
                  {selectedModelsFilter.length > 0 && (
                    <button
                      onClick={() => setSelectedModelsFilter([])}
                      className="text-xs text-gray-500 hover:text-gray-700 underline"
                    >
                      Clear all models
                    </button>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-2">Prompts:</label>
                <div className="space-y-2">
                  <div className="flex flex-wrap gap-2">
                    {selectedPromptsFilter.map((promptId) => (
                      <span
                        key={promptId}
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-green-600 text-white rounded"
                      >
                        {promptId}
                        <button
                          onClick={() => setSelectedPromptsFilter(selectedPromptsFilter.filter((p) => p !== promptId))}
                          className="ml-1 hover:bg-green-700 rounded px-1"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {prompts
                      .filter((prompt) => !selectedPromptsFilter.includes(prompt))
                      .map((prompt) => (
                        <button
                          key={prompt}
                          onClick={() => setSelectedPromptsFilter([...selectedPromptsFilter, prompt])}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded border border-gray-300 hover:bg-gray-200"
                        >
                          {prompt}
                        </button>
                      ))}
                  </div>
                  {selectedPromptsFilter.length > 0 && (
                    <button
                      onClick={() => setSelectedPromptsFilter([])}
                      className="text-xs text-gray-500 hover:text-gray-700 underline"
                    >
                      Clear all prompts
                    </button>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-2">Tests:</label>
                <div className="space-y-2">
                  <div className="flex flex-wrap gap-2">
                    {selectedTestsFilter.map((testId) => (
                      <span
                        key={testId}
                        className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-purple-600 text-white rounded"
                      >
                        {testId}
                        <button
                          onClick={() => setSelectedTestsFilter(selectedTestsFilter.filter((t) => t !== testId))}
                          className="ml-1 hover:bg-purple-700 rounded px-1"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {tests
                      .filter((test) => !selectedTestsFilter.includes(test))
                      .map((test) => (
                        <button
                          key={test}
                          onClick={() => setSelectedTestsFilter([...selectedTestsFilter, test])}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded border border-gray-300 hover:bg-gray-200"
                        >
                          {test}
                        </button>
                      ))}
                  </div>
                  {selectedTestsFilter.length > 0 && (
                    <button
                      onClick={() => setSelectedTestsFilter([])}
                      className="text-xs text-gray-500 hover:text-gray-700 underline"
                    >
                      Clear all tests
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="space-y-6">
          {viewMode === "overview" && <OverviewDashboard results={filteredResults} />}
          {viewMode === "heatmap" && <HeatmapView results={filteredResults} />}
          {viewMode === "focused" && <FocusedComparison results={filteredResults} expandedTests={expandedTests} toggleTest={toggleTest} />}
          {viewMode === "list" && (
            <div className="space-y-4">
              {filteredResults.map((result) => (
                <TestCaseCard
                  key={result.id}
                  result={result}
                  isExpanded={expandedTests.has(result.id)}
                  onToggle={() => toggleTest(result.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
