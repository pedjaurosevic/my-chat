import React from 'react'
import { useChat } from '../../contexts/ChatContext'
import { X, Trash2, FolderOpen, Save } from 'lucide-react'

const HistoryPanel: React.FC = () => {
  const {
    showHistory,
    setShowHistory,
    sessions,
    loadSession,
    deleteSession,
    saveSession,
    messages
  } = useChat()
  const [sessionName, setSessionName] = React.useState('')

  const handleSave = () => {
    saveSession(sessionName || undefined)
    setSessionName('')
  }

  if (!showHistory) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-surface rounded-2xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-accent">Session History</h3>
          <button
            onClick={() => setShowHistory(false)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Save Current Session */}
        <div className="bg-background rounded-xl p-4 mb-6">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Save Current Session</h4>
          <div className="flex gap-2">
            <input
              type="text"
              value={sessionName}
              onChange={(e) => setSessionName(e.target.value)}
              placeholder="Session name (optional)"
              className="flex-1 bg-surface border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-accent"
            />
            <button
              onClick={handleSave}
              disabled={messages.length === 0}
              className="btn-primary flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
          </div>
        </div>

        {/* Saved Sessions */}
        <div>
          <h4 className="text-sm font-semibold text-gray-300 mb-3">Saved Sessions</h4>
          {sessions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No saved sessions yet</p>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.filename}
                  className="bg-background rounded-lg p-4 flex items-center justify-between"
                >
                  <div className="flex-1">
                    <h5 className="font-medium text-white">{session.name}</h5>
                    <p className="text-sm text-gray-400">
                      {session.messages.length} messages • {new Date(session.date).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => loadSession(session.filename)}
                      className="p-2 hover:bg-surface rounded-lg transition-colors"
                      title="Load"
                    >
                      <FolderOpen className="w-4 h-4 text-accent" />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm(`Delete session "${session.name}"?`)) {
                          deleteSession(session.filename)
                        }
                      }}
                      className="p-2 hover:bg-surface rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default HistoryPanel
