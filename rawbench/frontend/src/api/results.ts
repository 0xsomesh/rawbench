// API calls for fetching results from the server

export interface ResultSummary {
  filename: string
  path: string
  summary: {
    total_results?: number
    total_tokens?: number
    avg_latency?: number
    [key: string]: any
  }
  created_at: string
  file_size: number
}

export interface ResultsListResponse {
  results: ResultSummary[]
}

export interface ResultDetail {
  summary?: {
    total_results?: number
    total_tokens?: number
    avg_latency?: number
    [key: string]: any
  }
  results?: any[]
  [key: string]: any
}

const API_BASE_URL = 'http://localhost:8001/api'

/**
 * Fetch list of all evaluation results
 */
export async function fetchResultsList(): Promise<ResultsListResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/results`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching results list:', error)
    throw error
  }
}

/**
 * Fetch specific evaluation result by filename
 */
export async function fetchResultDetail(filename: string): Promise<ResultDetail> {
  try {
    const response = await fetch(`${API_BASE_URL}/results/${encodeURIComponent(filename)}.json`)
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Result file not found: ${filename}`)
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching result detail:', error)
    throw error
  }
}

/**
 * Health check for the API server
 */
export async function checkApiHealth(): Promise<{ status: string; service: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error checking API health:', error)
    throw error
  }
}
