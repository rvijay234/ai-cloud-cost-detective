import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import ProgressTracker from '../components/ProgressTracker'

const Dashboard: React.FC = () => {
  const [region, setRegion] = useState('us-east-1')
  const [regions, setRegions] = useState<string[]>([])
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchRegions()
  }, [])

  const fetchRegions = async () => {
    try {
      const response = await axios.get('/api/regions')
      setRegions(response.data.regions)
    } catch (error) {
      console.error('Failed to fetch regions:', error)
    }
  }

  const startAnalysis = async () => {
    setIsAnalyzing(true)
    try {
      const response = await axios.post('/api/analyze', { region })
      setAnalysisId(response.data.analysis_id)
    } catch (error: any) {
      console.error('Failed to start analysis:', error)
      alert(error.response?.data?.detail || 'Failed to start analysis')
      setIsAnalyzing(false)
    }
  }

  const handleAnalysisComplete = (id: string) => {
    setIsAnalyzing(false)
    navigate(`/report/${id}`)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">AI Cloud Cost Detective</h1>
        <p className="text-gray-400">Analyze your AWS resources for cost optimization opportunities</p>
      </div>

      <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700 mb-6">
        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-300 mb-2">AWS Region</label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white"
              disabled={isAnalyzing}
            >
              {regions.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={startAnalysis}
            disabled={isAnalyzing}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>
      </div>

      {isAnalyzing && analysisId && (
        <ProgressTracker
          analysisId={analysisId}
          onComplete={handleAnalysisComplete}
        />
      )}

      {!isAnalyzing && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
            </div>
            <p className="text-gray-400 text-sm">
              Powered by Groq AI to identify cost optimization opportunities
            </p>
          </div>

          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white">Real-time</h3>
            </div>
            <p className="text-gray-400 text-sm">
              Live progress updates via WebSocket during analysis
            </p>
          </div>

          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white">Actionable</h3>
            </div>
            <p className="text-gray-400 text-sm">
              Get specific AWS CLI commands to fix identified issues
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
