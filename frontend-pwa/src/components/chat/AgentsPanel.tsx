import React, { useState } from 'react'
import { useChat } from '../../contexts/ChatContext'
import { X, Search, Globe, Code, Newspaper } from 'lucide-react'

const AgentsPanel: React.FC = () => {
  const { showAgents, setShowAgents } = useChat()
  const [query, setQuery] = useState('')
  const [url, setUrl] = useState('')
  const [code, setCode] = useState('')
  const [taskType, setTaskType] = useState<'analyze' | 'debug' | 'explain'>('analyze')
  const [activeTab, setActiveTab] = useState<'search' | 'scrape' | 'code' | 'news'>('search')

  const tabs = [
    { id: 'search' as const, label: 'Web Search', icon: Search },
    { id: 'scrape' as const, label: 'Web Scrape', icon: Globe },
    { id: 'code' as const, label: 'Code Helper', icon: Code },
    { id: 'news' as const, label: 'News', icon: Newspaper },
  ]

  if (!showAgents) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end justify-center p-4 z-50">
      <div className="bg-surface rounded-t-2xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-accent">AI Agents</h3>
          <button
            onClick={() => setShowAgents(false)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-4 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'pill-btn-active'
                    : 'pill-btn-inactive'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>

        {/* Tab Content */}
        <div className="bg-background rounded-xl p-4">
          {activeTab === 'search' && (
            <div>
              <label className="block text-sm text-gray-300 mb-2">Search Query</label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter search query..."
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-accent"
              />
              <button className="w-full btn-primary mt-4 flex items-center justify-center gap-2">
                <Search className="w-4 h-4" />
                Search
              </button>
            </div>
          )}

          {activeTab === 'scrape' && (
            <div>
              <label className="block text-sm text-gray-300 mb-2">URL</label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-accent"
              />
              <button className="w-full btn-primary mt-4 flex items-center justify-center gap-2">
                <Globe className="w-4 h-4" />
                Scrape
              </button>
            </div>
          )}

          {activeTab === 'code' && (
            <div>
              <label className="block text-sm text-gray-300 mb-2">Code</label>
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Paste code here..."
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-accent resize-none"
                rows={8}
              />
              <label className="block text-sm text-gray-300 mt-4 mb-2">Task Type</label>
              <select
                value={taskType}
                onChange={(e) => setTaskType(e.target.value as any)}
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-accent"
              >
                <option value="analyze">Analyze</option>
                <option value="debug">Debug</option>
                <option value="explain">Explain</option>
              </select>
              <button className="w-full btn-primary mt-4 flex items-center justify-center gap-2">
                <Code className="w-4 h-4" />
                {taskType.charAt(0).toUpperCase() + taskType.slice(1)} Code
              </button>
            </div>
          )}

          {activeTab === 'news' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-300">Latest News</span>
                <button className="text-accent text-sm hover:underline">Refresh</button>
              </div>
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-surface rounded-lg p-3">
                  <h5 className="font-medium text-white text-sm">News Headline {i}</h5>
                  <p className="text-xs text-gray-400 mt-1">Summary of the news article...</p>
                  <p className="text-xs text-accent mt-2">Source • {new Date().toLocaleString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={() => setShowAgents(false)}
          className="w-full btn-secondary mt-4"
        >
          Close
        </button>
      </div>
    </div>
  )
}

export default AgentsPanel
