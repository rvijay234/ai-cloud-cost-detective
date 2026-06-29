import React, { useState, useEffect } from 'react'
import axios from 'axios'

interface ProgressTrackerProps {
  analysisId: string
  onComplete: (id: string) => void
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ analysisId, onComplete }) => {
  const [status, setStatus] = useState('pending')
  const [messages, setMessages] = useState<string[]>(['Starting analysis...'])

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get(`/api/analysis/${analysisId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        const data = response.data
        setStatus(data.status)

        if (data.status === 'running') {
          setMessages(['Connecting to AWS...', 'Scanning resources...', 'Analyzing with Groq AI...'])
        } else if (data.status === 'completed') {
          setMessages(prev => [...prev, 'Analysis complete!'])
          clearInterval(interval)
          setTimeout(() => onComplete(analysisId), 1500)
        } else if (data.status === 'failed') {
          setMessages(prev => [...prev, 'Analysis failed. Please try again.'])
          clearInterval(interval)
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [analysisId, onComplete])

  return (
    <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
      <h2 className="text-xl font-semibold text-white mb-4">Analysis Progress</h2>
      <div className="space-y-3">
        {messages.map((msg, index) => (
          <div key={index} className="flex items-center gap-3 text-gray-300">
            {status === 'completed' && index === messages.length - 1 ? (
              <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            ) : (
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            )}
            <span>{msg}</span>
          </div>
        ))}
      </div>
      {status === 'completed' && (
        <div className="mt-4 p-3 bg-green-500/20 border border-green-500 rounded-lg text-green-400 text-sm">
          Analysis complete! Redirecting to report...
        </div>
      )}
      {status === 'failed' && (
        <div className="mt-4 p-3 bg-red-500/20 border border-red-500 rounded-lg text-red-400 text-sm">
          Analysis failed. Please try again.
        </div>
      )}
    </div>
  )
}

export default ProgressTracker
