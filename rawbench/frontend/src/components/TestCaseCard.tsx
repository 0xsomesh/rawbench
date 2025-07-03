"use client"

import { useState } from "react"
import { ChevronRight, Code } from "lucide-react"
import JsonModal from "./JsonModal"

interface TestCaseCardProps {
  result: any
  isExpanded: boolean
  onToggle: () => void
}

function ModelBadge({ modelId, size = "sm" }: { modelId: string; size?: "sm" | "xs" }) {
  const getModelColor = (modelId: string): string => {
    const colors: Record<string, string> = {
      "gpt-4o-mini-conservative": "bg-blue-500",
      "gpt-4o-mini-creative": "bg-purple-500",
      "gpt-4o": "bg-green-500",
      "claude-3": "bg-orange-500",
      gemini: "bg-red-500",
    }
    return colors[modelId] || "bg-gray-500"
  }

  const sizeClass = size === "xs" ? "w-2 h-2" : "w-3 h-3"
  return (
    <span className={`inline-block ${sizeClass} rounded-full ${getModelColor(modelId)} mr-2`} title={modelId}></span>
  )
}

export default function TestCaseCard({ result, isExpanded, onToggle }: TestCaseCardProps) {
  const [showJsonModal, setShowJsonModal] = useState(false)

  const handleJsonClick = (e: React.MouseEvent) => {
    e.stopPropagation() // Prevent card expansion when clicking JSON button
    setShowJsonModal(true)
  }

  return (
    <>
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
        <div className="p-4 cursor-pointer hover:bg-gray-50 transition-colors" onClick={onToggle}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <ModelBadge modelId={result.model_id} />
              <span className="font-mono text-sm">{result.model_id}</span>
              <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-700 border border-gray-200">{result.prompt_id}</span>
              <span className="text-xs text-gray-500">{result.test_id}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <button
                onClick={handleJsonClick}
                className="p-1.5 hover:bg-gray-200 rounded transition-colors text-gray-500 hover:text-gray-700"
                title="View raw JSON"
              >
                <Code className="w-3 h-3" />
              </button>
              <span>{result.latency_ms}ms</span>
              <span>{result.total_tokens}t</span>
              <ChevronRight className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-90" : ""}`} />
            </div>
          </div>
          <div className="text-sm text-gray-700">{result.output_content || "No output"}</div>
        </div>

        {isExpanded && (
          <div className="px-4 pb-4 border-t border-gray-200 bg-gray-50">
            <div className="pt-4 space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Input Messages</h4>
                {result.input_messages?.map((msg: any, index: number) => (
                  <div key={index} className="border-l-2 border-l-blue-400 bg-blue-50 pl-3 py-2 mb-3">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">{msg.role}</div>
                    <div className="text-sm font-mono whitespace-pre-wrap text-gray-700">{msg.content || "No content"}</div>
                  </div>
                ))}
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Output Messages</h4>
                {result.output_messages?.map((msg: any, index: number) => (
                  <div key={index} className="border-l-2 border-l-green-400 bg-green-50 pl-3 py-2 mb-3">
                    <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">{msg.role}</div>
                    <div className="text-sm font-mono whitespace-pre-wrap text-gray-700">{msg.content || "No content"}</div>
                    {msg.tool_calls && msg.tool_calls.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {msg.tool_calls.map((call: any, callIndex: number) => (
                          <div key={callIndex} className="bg-gray-100 p-2 rounded text-xs font-mono">
                            <span className="text-yellow-600 font-semibold">{call.function.name}</span>
                            <span className="text-gray-600 ml-2">{call.function.arguments}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t border-gray-200">
                <div className="text-center">
                  <div className="text-xs text-gray-500">Completion Tokens</div>
                  <div className="font-mono text-sm text-gray-700">{result.completion_tokens}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500">Prompt Tokens</div>
                  <div className="font-mono text-sm text-gray-700">{result.prompt_tokens}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500">Total Tokens</div>
                  <div className="font-mono text-sm text-gray-700">{result.total_tokens}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-500">Created At</div>
                  <div className="font-mono text-xs text-gray-700">
                    {new Date(result.created_at).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <JsonModal
        isOpen={showJsonModal}
        onClose={() => setShowJsonModal(false)}
        data={result}
        title={`Raw JSON - ${result.test_id}`}
      />
    </>
  )
}
