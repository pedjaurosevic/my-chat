import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import type { ReactNode } from 'react'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  model?: string
}

interface ChatContextType {
  messages: Message[]
  isLoading: boolean
  sendMessage: (content: string, model?: string) => Promise<void>
  clearMessages: () => void
  currentModel: string
  setCurrentModel: (model: string) => void
  availableModels: string[]
  setAvailableModels: (models: string[]) => void
  systemPrompt: string
  setSystemPrompt: (prompt: string) => void
  documentContent: string
  setDocumentContent: (content: string) => void
  showSystem: boolean
  setShowSystem: (show: boolean) => void
  showHistory: boolean
  setShowHistory: (show: boolean) => void
  showDocs: boolean
  setShowDocs: (show: boolean) => void
  showAgents: boolean
  setShowAgents: (show: boolean) => void
  showDialogue: boolean
  setShowDialogue: (show: boolean) => void
  showExport: boolean
  setShowExport: (show: boolean) => void
  saveSession: (name?: string) => Promise<void>
  sessions: Session[]
  loadSession: (filename: string) => Promise<void>
  deleteSession: (filename: string) => Promise<void>
  exportChat: (format: 'txt' | 'epub' | 'pdf' | 'html') => void
}

export interface Session {
  filename: string
  name: string
  date: string
  messages: Message[]
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export const useChat = () => {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}

interface ChatProviderProps {
  children: ReactNode
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentModel, setCurrentModel] = useState('gpt-oss:20b-cloud')
  const [availableModels, setAvailableModels] = useState<string[]>([])
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful AI assistant.')
  const [documentContent, setDocumentContent] = useState('')
  const [showSystem, setShowSystem] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [showDocs, setShowDocs] = useState(false)
  const [showAgents, setShowAgents] = useState(false)
  const [showDialogue, setShowDialogue] = useState(false)
  const [showExport, setShowExport] = useState(false)
  const [sessions, setSessions] = useState<Session[]>([])

  // Load saved state from localStorage
  useEffect(() => {
    const savedSystemPrompt = localStorage.getItem('ollama-system-prompt')
    if (savedSystemPrompt) setSystemPrompt(savedSystemPrompt)
    const savedSessions = localStorage.getItem('ollama-sessions')
    if (savedSessions) setSessions(JSON.parse(savedSessions))
  }, [])

  // Auto-save system prompt
  useEffect(() => {
    localStorage.setItem('ollama-system-prompt', systemPrompt)
  }, [systemPrompt])

  const sendMessage = useCallback(async (content: string, model: string = currentModel) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Prepare messages with system prompt and document context
      const messagesToSend: any[] = []

      if (systemPrompt) {
        messagesToSend.push({ role: 'system', content: systemPrompt })
      }

      if (documentContent) {
        messagesToSend.push({
          role: 'system',
          content: `Context from document:\n${documentContent}\n\nUser Question:`
        })
      }

      messagesToSend.push({ role: 'user', content })

      // Real API call to FastAPI backend
      const response = await fetch('/api/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          model: model,
          source: 'Ollama (11434)',
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        model: model,
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        model: model,
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }, [currentModel, systemPrompt, documentContent])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  const saveSession = useCallback(async (name?: string) => {
    const timestamp = new Date().toISOString()
    const filename = name || `session_${Date.now()}`

    const session: Session = {
      filename,
      name: name || messages.find(m => m.role === 'user')?.content.substring(0, 30) || 'Untitled',
      date: timestamp,
      messages,
    }

    const newSessions = [session, ...sessions]
    setSessions(newSessions)
    localStorage.setItem('ollama-sessions', JSON.stringify(newSessions))
  }, [messages, sessions])

  const loadSession = useCallback(async (filename: string) => {
    const session = sessions.find(s => s.filename === filename)
    if (session) {
      setMessages(session.messages)
    }
  }, [sessions])

  const deleteSession = useCallback(async (filename: string) => {
    const newSessions = sessions.filter(s => s.filename !== filename)
    setSessions(newSessions)
    localStorage.setItem('ollama-sessions', JSON.stringify(newSessions))
  }, [sessions])

  const exportChat = useCallback((format: 'txt' | 'epub' | 'pdf' | 'html') => {
    let content = ''
    const timestamp = new Date().toISOString()

    if (format === 'txt') {
      content = `OLLAMA.CORE - Chat Export\nDate: ${timestamp}\nTotal messages: ${messages.length}\n\n`
      messages.forEach(msg => {
        content += `[${msg.role.toUpperCase()}${msg.model ? ` - ${msg.model}` : ''}]\n${msg.content}\n\n---\n\n`
      })
      downloadFile(content, `ollama_chat_${timestamp.replace(/[:.]/g, '-')}.txt`, 'text/plain')
    } else if (format === 'html') {
      content = `
        <!DOCTYPE html>
        <html>
        <head><title>OLLAMA.CORE Chat</title>
        <style>body { font-family: Georgia, serif; padding: 40px; max-width: 800px; margin: 0 auto; }
        .user { background: #f0f0f0; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .assistant { background: #e8f5e9; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .meta { font-size: 12px; color: #666; margin-bottom: 8px; }</style>
        </head>
        <body><h1>OLLAMA.CORE Chat</h1><p>${timestamp}</p>
        ${messages.map(msg => `
          <div class="${msg.role}">
            <div class="meta">${msg.role.toUpperCase()}${msg.model ? ` - ${msg.model}` : ''}</div>
            <div>${msg.content}</div>
          </div>
        `).join('')}
        </body></html>
      `
      downloadFile(content, `ollama_chat_${timestamp.replace(/[:.]/g, '-')}.html`, 'text/html')
    } else {
      // For PDF and EPUB, we'd need backend support
      alert('PDF and EPUB export requires backend support.')
    }
  }, [messages])

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const value: ChatContextType = {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    currentModel,
    setCurrentModel,
    availableModels,
    setAvailableModels,
    systemPrompt,
    setSystemPrompt,
    documentContent,
    setDocumentContent,
    showSystem,
    setShowSystem,
    showHistory,
    setShowHistory,
    showDocs,
    setShowDocs,
    showAgents,
    setShowAgents,
    showDialogue,
    setShowDialogue,
    showExport,
    setShowExport,
    saveSession,
    sessions,
    loadSession,
    deleteSession,
    exportChat,
  }

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  )
}