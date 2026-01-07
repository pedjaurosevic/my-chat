import React from 'react'
import { useChat } from '../../contexts/ChatContext'
import { X, Save } from 'lucide-react'

const SystemPrompt: React.FC = () => {
  const { systemPrompt, setSystemPrompt, showSystem, setShowSystem } = useChat()
  const [localPrompt, setLocalPrompt] = React.useState(systemPrompt)

  const handleSave = () => {
    setSystemPrompt(localPrompt)
    setShowSystem(false)
  }

  const handleCancel = () => {
    setLocalPrompt(systemPrompt)
    setShowSystem(false)
  }

  if (!showSystem) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-surface rounded-2xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-accent">System Instructions</h3>
          <button
            onClick={handleCancel}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <textarea
          value={localPrompt}
          onChange={(e) => setLocalPrompt(e.target.value)}
          placeholder="Enter system prompt..."
          className="w-full bg-background border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-accent resize-none"
          rows={10}
        />

        <div className="flex gap-3 mt-6">
          <button
            onClick={handleSave}
            className="flex-1 btn-primary flex items-center justify-center gap-2"
          >
            <Save className="w-4 h-4" />
            Save & Close
          </button>
          <button
            onClick={handleCancel}
            className="flex-1 btn-secondary"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

export default SystemPrompt
