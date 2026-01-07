import React from 'react'
import { useChat } from '../../contexts/ChatContext'
import { X, FileText, BookOpen, Download, Printer } from 'lucide-react'

const ExportPanel: React.FC = () => {
  const { showExport, setShowExport, exportChat, messages } = useChat()

  if (!showExport) return null

  const exportOptions = [
    { id: 'txt', label: 'TXT', icon: FileText, description: 'Plain text format' },
    { id: 'html', label: 'HTML', icon: Printer, description: 'Print-friendly format' },
    { id: 'epub', label: 'EPUB', icon: BookOpen, description: 'E-reader format (coming soon)' },
    { id: 'pdf', label: 'PDF', icon: Download, description: 'PDF document (coming soon)' },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-surface rounded-2xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-bold text-accent">Export Chat</h3>
          <button
            onClick={() => setShowExport(false)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-3">
          {exportOptions.map((option) => {
            const Icon = option.icon
            return (
              <button
                key={option.id}
                onClick={() => {
                  if (option.id === 'epub' || option.id === 'pdf') {
                    alert('This format is coming soon!')
                  } else {
                    exportChat(option.id as 'txt' | 'html' | 'epub' | 'pdf')
                  }
                }}
                disabled={messages.length === 0}
                className="w-full p-4 bg-background hover:bg-gray-800 rounded-xl text-left transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-5 h-5 text-accent" />
                  <div className="flex-1">
                    <h4 className="font-medium text-white">{option.label}</h4>
                    <p className="text-sm text-gray-400">{option.description}</p>
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        {messages.length === 0 && (
          <p className="text-sm text-gray-400 text-center mt-4">
            No messages to export
          </p>
        )}

        <button
          onClick={() => setShowExport(false)}
          className="w-full btn-secondary mt-4"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}

export default ExportPanel
