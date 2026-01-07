import React, { useState } from 'react'
import { useChat } from '../../contexts/ChatContext'
import { X, Search, Globe, Code, Newspaper, Upload } from 'lucide-react'

const AgentsPanel: React.FC = () => {
  const { showAgents, setShowAgents } = useChat()
  const [query, setQuery] = useState('')
  const [url, setUrl] = useState('')
  const [code, setCode] = useState('')
  const [taskType, setTaskType] = useState<'analyze' | 'debug' | 'explain'>('analyze')
  const [activeTab, setActiveTab] = useState<'search' | 'scrape' | 'code' | 'news' | 'document'>('search')
  const [results, setResults] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const tabs = [
    { id: 'search' as const, label: 'Web Search', icon: Search },
    { id: 'scrape' as const, label: 'Web Scrape', icon: Globe },
    { id: 'code' as const, label: 'Code Helper', icon: Code },
    { id: 'news' as const, label: 'News', icon: Newspaper },
    { id: 'document' as const, label: 'Documents', icon: Upload },
  ]

  const handleWebSearch = async () => {
    if (!query) return
    setIsLoading(true)
    try {
      const response = await fetch('/api/agents/web-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, num_results: 3 }),
      })
      const data = await response.json()
      setResults(data.results)
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleWebScrape = async () => {
    if (!url) return
    setIsLoading(true)
    try {
      const response = await fetch('/api/agents/web-scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      })
      const data = await response.json()
      setResults(data.content)
    } catch (error) {
      console.error('Scrape error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCodeHelper = async () => {
    if (!code) return
    setIsLoading(true)
    try {
      const response = await fetch('/api/agents/code-helper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, task: taskType }),
      })
      const data = await response.json()
      setResults(data.result)
    } catch (error) {
      console.error('Code helper error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleNews = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/agents/news')
      const data = await response.json()
      setResults(data.news)
    } catch (error) {
      console.error('News error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDocumentUpload = async () => {
    if (!selectedFile) return
    setIsLoading(true)
    const formData = new FormData()
    formData.append('file', selectedFile)
    try {
      const response = await fetch('/api/agents/analyze-document', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setResults(data.content)
    } catch (error) {
      console.error('Document upload error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!showAgents) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end justify-center p-4 z-50">
      <div className="bg-surface rounded-t-2xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-accent">AI Agents</h3>
          <button
            onClick={() => {
              setShowAgents(false)
              setResults(null)
            }}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1.5 mb-4 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id)
                  setResults(null)
                }}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'pill-btn-active'
                    : 'pill-btn-inactive'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
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
              <button
                onClick={handleWebSearch}
                disabled={isLoading}
                className="w-full btn-primary mt-4 flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
                {isLoading ? 'Searching...' : 'Search'}
              </button>
              {results && results.length > 0 && (
                <div className="mt-4 space-y-2">
                  {results.map((result: any, index: number) => (
                    <div key={index} className="bg-surface p-3 rounded-lg">
                      <h4 className="font-semibold text-accent">{result.title}</h4>
                      <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-sm text-gray-400 hover:text-white">
                        {result.url}
                      </a>
                      <p className="text-sm text-gray-300 mt-1">{result.snippet}</p>
                    </div>
                  ))}
                </div>
              )}
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
              <button
                onClick={handleWebScrape}
                disabled={isLoading}
                className="w-full btn-primary mt-4 flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Globe className="w-4 h-4" />
                )}
                {isLoading ? 'Scraping...' : 'Scrape'}
              </button>
              {results && (
                <div className="mt-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap">{results}</pre>
                </div>
              )}
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
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-2 text-white mb-4"
              >
                <option value="analyze">Analyze</option>
                <option value="debug">Debug</option>
                <option value="explain">Explain</option>
              </select>
              <button
                onClick={handleCodeHelper}
                disabled={isLoading}
                className="w-full btn-primary flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Code className="w-4 h-4" />
                )}
                {isLoading ? 'Processing...' : taskType.charAt(0).toUpperCase() + taskType.slice(1)}
              </button>
              {results && (
                <div className="mt-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap">{results}</pre>
                </div>
              )}
            </div>
          )}

          {activeTab === 'news' && (
            <div>
              <button
                onClick={handleNews}
                disabled={isLoading}
                className="w-full btn-primary flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Newspaper className="w-4 h-4" />
                )}
                {isLoading ? 'Loading...' : 'Load News'}
              </button>
              {results && Array.isArray(results) && results.length > 0 && (
                <div className="mt-4 space-y-2">
                  {results.map((newsItem: any, index: number) => (
                    <div key={index} className="bg-surface p-3 rounded-lg">
                      <h4 className="font-semibold text-accent">{newsItem.title}</h4>
                      <p className="text-xs text-gray-400 mt-1">{newsItem.source} • {newsItem.date}</p>
                      <p className="text-sm text-gray-300 mt-1">{newsItem.snippet}</p>
                      {newsItem.link && (
                        <a href={newsItem.link} target="_blank" rel="noopener noreferrer" className="text-sm text-accent hover:underline">
                          Read more
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'document' && (
            <div>
              <label className="block text-sm text-gray-300 mb-2">Upload Document</label>
              <input
                type="file"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                accept=".pdf,.epub,.txt,.docx,.md"
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-3 text-white"
              />
              <button
                onClick={handleDocumentUpload}
                disabled={!selectedFile || isLoading}
                className="w-full btn-primary mt-4 flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Upload className="w-4 h-4" />
                )}
                {isLoading ? 'Processing...' : 'Analyze'}
              </button>
              {results && (
                <div className="mt-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap">{results}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AgentsPanel
