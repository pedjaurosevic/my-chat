import React, { useRef, useEffect } from 'react'
import { useChat } from '../../contexts/ChatContext'
import { MessageSquare } from 'lucide-react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import { FullToolbar } from './PillButtons'
import SystemPrompt from './SystemPrompt'
import HistoryPanel from './HistoryPanel'
import DocumentUpload from './DocumentUpload'
import AgentsPanel from './AgentsPanel'
import ExportPanel from './ExportPanel'

const ChatScreen: React.FC = () => {
  const { messages, isLoading, sendMessage, currentModel, setCurrentModel } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content: string) => {
    await sendMessage(content)
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <h1 className="text-xl font-bold text-accent">OLLAMA.CORE</h1>
        <select
          value={currentModel}
          onChange={(e) => setCurrentModel(e.target.value)}
          className="bg-surface text-white px-3 py-1 rounded-lg border border-gray-600 text-sm"
        >
          <option value="gpt-oss:120b-cloud">GPT-OSS 120B Cloud</option>
          <option value="gpt-oss:20b-cloud">GPT-OSS 20B Cloud</option>
          <option value="deepseek-v3.2:cloud">DeepSeek V3.2 Cloud</option>
          <option value="kimi-k2:1t-cloud">Kimi K2 1T Cloud</option>
          <option value="qwen3:14b">Qwen3 14B</option>
          <option value="qwen2.5:32b">Qwen2.5 32B</option>
          <option value="gemma3:27b-cloud">Gemma3 27B Cloud</option>
          <option value="deepseek-r1:14b">DeepSeek R1 14B</option>
          <option value="llama3.2:3b">Llama 3.2:3B (Local)</option>
          <option value="tinyllama:latest">TinyLlama (Local)</option>
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-12">
            <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Start a conversation with your AI assistant</p>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-surface rounded-2xl px-4 py-3 max-w-xs">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Pill Buttons */}
      <FullToolbar />

      {/* Modals */}
      <SystemPrompt />
      <HistoryPanel />
      <DocumentUpload />
      <AgentsPanel />
      <ExportPanel />

      {/* Chat Input */}
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />


    </div>
  )
}

export default ChatScreen