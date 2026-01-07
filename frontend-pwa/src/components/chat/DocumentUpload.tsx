import React from 'react'
import { useChat } from '../../contexts/ChatContext'
import { X, Upload, FileText, X as CloseIcon } from 'lucide-react'

const DocumentUpload: React.FC = () => {
  const {
    showDocs,
    setShowDocs,
    documentContent,
    setDocumentContent
  } = useChat()
  const fileInputRef = React.useRef<HTMLInputElement>(null)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const content = event.target?.result as string
      setDocumentContent(content)
    }
    reader.readAsText(file)
  }

  const handleClear = () => {
    setDocumentContent('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  if (!showDocs) return null

  const wordCount = documentContent ? documentContent.split(/\s+/).filter(w => w.length > 0).length : 0
  const charCount = documentContent.length

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-surface rounded-2xl w-full max-w-3xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-accent">Document Context</h3>
          <button
            onClick={() => setShowDocs(false)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Upload Button */}
        <div className="mb-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.json,.csv"
            onChange={handleFileUpload}
            className="hidden"
            id="document-upload"
          />
          <label
            htmlFor="document-upload"
            className="flex items-center justify-center gap-2 btn-primary cursor-pointer"
          >
            <Upload className="w-4 h-4" />
            Upload Document (TXT, MD)
          </label>
        </div>

        {/* Document Info */}
        {documentContent && (
          <div className="bg-background rounded-lg p-3 mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-accent" />
              <div className="text-sm">
                <span className="text-gray-300">{wordCount}</span> words •{' '}
                <span className="text-gray-300">{charCount}</span> characters
              </div>
            </div>
            <button
              onClick={handleClear}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              title="Clear document"
            >
              <CloseIcon className="w-4 h-4 text-red-400" />
            </button>
          </div>
        )}

        {/* Document Preview */}
        <div className="bg-background rounded-xl p-4">
          <textarea
            value={documentContent}
            onChange={(e) => setDocumentContent(e.target.value)}
            placeholder="Document content will appear here..."
            className="w-full bg-transparent border-0 text-white placeholder-gray-400 focus:outline-none resize-none"
            rows={15}
          />
        </div>

        {/* Info */}
        <p className="text-sm text-gray-400 mt-4">
          This document will be used as context for all future messages in this chat.
        </p>
      </div>
    </div>
  )
}

export default DocumentUpload
