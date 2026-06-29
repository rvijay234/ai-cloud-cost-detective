import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

interface Issue {
  severity: string
  resource_type: string
  resource_id: string
  resource_name: string
  issue: string
  recommendation: string
  fix_command: string
  estimated_savings: number
}

interface AnalysisResult {
  summary: string
  total_estimated_monthly_savings: number
  issues: Issue[]
}

const Report: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchAnalysis()
  }, [id])

  const fetchAnalysis = async () => {
    try {
      const response = await axios.get(`/api/analysis/${id}`)
      setAnalysis(response.data.analysis_result)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analysis')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500/20 text-red-400 border-red-500'
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500'
      case 'low':
        return 'bg-green-500/20 text-green-400 border-green-500'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="bg-red-500/20 border border-red-500 rounded-lg p-4 text-red-400">
          {error}
        </div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-gray-400">No analysis data available</div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="text-gray-400 hover:text-white mb-4 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold text-white mb-2">Cost Analysis Report</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-2">Summary</h3>
          <p className="text-gray-400">{analysis.summary}</p>
        </div>

        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-2">Estimated Monthly Savings</h3>
          <p className="text-4xl font-bold text-green-400">
            ${analysis.total_estimated_monthly_savings.toFixed(2)}
          </p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-2xl font-semibold text-white mb-6">
          Issues Found ({analysis.issues.length})
        </h2>

        {analysis.issues.length === 0 ? (
          <p className="text-gray-400">No issues found. Great job!</p>
        ) : (
          <div className="space-y-6">
            {analysis.issues.map((issue, index) => (
              <div key={index} className="bg-gray-700/50 rounded-lg p-5 border border-gray-600">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(issue.severity)}`}>
                        {issue.severity.toUpperCase()}
                      </span>
                      <span className="text-gray-400 text-sm">{issue.resource_type}</span>
                    </div>
                    <h4 className="text-lg font-semibold text-white mb-1">{issue.resource_name || issue.resource_id}</h4>
                    <p className="text-gray-300">{issue.issue}</p>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-green-400 font-semibold">
                      ${issue.estimated_savings.toFixed(2)}/mo
                    </p>
                  </div>
                </div>

                <div className="mb-4">
                  <h5 className="text-sm font-medium text-gray-300 mb-2">Recommendation</h5>
                  <p className="text-gray-400 text-sm">{issue.recommendation}</p>
                </div>

                <div>
                  <h5 className="text-sm font-medium text-gray-300 mb-2">Fix Command</h5>
                  <div className="relative">
                    <pre className="bg-gray-900 rounded-lg p-4 text-sm text-gray-300 overflow-x-auto">
                      <code>{issue.fix_command}</code>
                    </pre>
                    <button
                      onClick={() => copyToClipboard(issue.fix_command)}
                      className="absolute top-2 right-2 p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                      title="Copy to clipboard"
                    >
                      <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Report
