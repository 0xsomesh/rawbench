"use client"

import type React from "react"

import { useState } from "react"
import { X, Copy, Check } from "lucide-react"

interface JsonModalProps {
  isOpen: boolean
  onClose: () => void
  data: any
  title: string
}

export default function JsonModal({ isOpen, onClose, data, title }: JsonModalProps) {
  const [copied, setCopied] = useState(false)

  if (!isOpen) return null

  const jsonString = JSON.stringify(data, null, 2)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(jsonString)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy JSON:", err)
    }
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg border border-gray-200 w-full max-w-4xl max-h-[80vh] flex flex-col shadow-lg">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 rounded border border-gray-300 transition-colors"
              title="Copy JSON to clipboard"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-green-600" />
                  <span className="text-green-600">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-gray-100 rounded transition-colors"
              title="Close modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          <pre className="p-4 text-xs font-mono text-gray-700 bg-gray-50 whitespace-pre-wrap break-words">
            <code>{jsonString}</code>
          </pre>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
          <div className="flex items-center justify-between">
            <span>Press Escape to close</span>
            <span>
              {jsonString.split("\n").length} lines • {(jsonString.length / 1024).toFixed(1)}KB
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
