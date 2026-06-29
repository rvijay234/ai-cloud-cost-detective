import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

interface Analysis {
  id: number
  region: string
  resources_scanned: number
  issues_found: number
  estimated_savings: number
  status: string
  created_at: string
  summary: string | null
}

const History: React.FC = () => {
  const navigate = useNavigate()
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await axios.get('/api/history')
      setAnalyses(response.data.analyses)
    } catch (error) {
      console.error('Failed to fetch history:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400'
      case 'failed':
        return 'bg-red-500/20 text-red-400'
      case 'running':
        return 'bg-blue-500/20 text-blue-400'
      default:
        return 'bg-gray-500/20 text-gray-400'
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

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Analysis History</h1>
        <p className="text-gray-400">View your past cost analysis reports</p>
      </div>

      {analyses.length === 0 ? (
        <div className="bg-gray-800 rounded-xl p-8 border border-gray-700 text-center">
          <p className="text-gray-400 mb-4">No analyses yet</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Run Your First Analysis
          </button>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-700/50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Region</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Date</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Resources</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Issues</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Savings</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {analyses.map((analysis) => (
                <tr key={analysis.id} className="hover:bg-gray-700/30 transition-colors">
                  <td className="px-6 py-4 text-white">{analysis.region}</td>
                  <td className="px-6 py-4 text-gray-300">
                    {new Date(analysis.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-gray-300">{analysis.resources_scanned}</td>
                  <td className="px-6 py-4 text-gray-300">{analysis.issues_found}</td>
                  <td className="px-6 py-4 text-green-400 font-semibold">
                    ${analysis.estimated_savings.toFixed(2)}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(analysis.status)}`}>
                      {analysis.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {analysis.status === 'completed' && (
                      <button
                        onClick={() => navigate(`/report/${analysis.id}`)}
                        className="text-blue-400 hover:text-blue-300 font-medium"
                      >
                        View Report
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default History
