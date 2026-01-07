import React, { useState } from 'react'
import { useChat } from '../../contexts/ChatContext'
import { X, Play, Save, MessageSquare, Users, ChevronDown } from 'lucide-react'

interface DialogueMessage {
  role: string
  name: string
  content: string
  model: string
  persona?: string
}

const DialoguePanel: React.FC = () => {
  const { showDialogue, setShowDialogue, availableModels } = useChat()
  const [mode, setMode] = useState<'two' | 'multi'>('two')
  const [model1, setModel1] = useState('qwen2.5:32b')
  const [model2, setModel2] = useState('deepseek-r1:14b')
  const [persona1, setPersona1] = useState('INTJ - Arhitekta')
  const [persona2, setPersona2] = useState('ENTP - Debatnik')
  const [multiParticipants, setMultiParticipants] = useState<Array<{ id: number; model: string; persona: string }>>([
    { id: 1, model: 'qwen2.5:32b', persona: 'INTJ - Arhitekta' },
    { id: 2, model: 'deepseek-r1:14b', persona: 'ENTP - Debatnik' },
    { id: 3, model: 'qwen3:14b', persona: 'INFJ - Zastupnik' },
    { id: 4, model: 'llama3.2:3b', persona: 'ENFJ - Protagonista' },
    { id: 5, model: 'user', persona: 'User' },
  ])
  const [dialogueId, setDialogueId] = useState<string | null>(null)
  const [exportMenuOpen, setExportMenuOpen] = useState(false)
  const [initialPrompt, setInitialPrompt] = useState('')
  const [messages, setMessages] = useState<DialogueMessage[]>([])
  const [currentRound, setCurrentRound] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [userInput, setUserInput] = useState('')

  const MBTI_PERSONAS = [
    'INTJ - Arhitekta',
    'INTP - Logičar',
    'ENTJ - Komandant',
    'ENTP - Debatnik',
    'INFJ - Zastupnik',
    'INFP - Posrednik',
    'ENFJ - Protagonista',
    'ENFP - Aktivista',
    'ISTJ - Logističar',
    'ISFJ - Branilac',
    'ESTJ - Izvršilac',
    'ESFJ - Konzul',
    'ISTP - Virtuoso',
    'ISFP - Avanturista',
    'ESTP - Preduzetnik',
    'ESFP - Zabavljač',
  ]

  const handleStartDialogue = async () => {
    setUserInput('')
    setCurrentRound(0)

    setIsLoading(true)
    try {
      let response

      if (mode === 'two') {
        response = await fetch('/api/dialogue/dialogue/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            participant1: { model: model1, persona: persona1 },
            participant2: { model: model2, persona: persona2 },
            initial_prompt: initialPrompt,
            max_rounds: 5,
            dialogue_type: 'debate',
          }),
        })
      } else {
        response = await fetch('/api/dialogue/dialogue/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            participant1: { model: multiParticipants[0].model, persona: multiParticipants[0].persona },
            participant2: { model: multiParticipants[1].model, persona: multiParticipants[1].persona },
            initial_prompt: initialPrompt,
            max_rounds: 10,
            dialogue_type: 'discussion',
          }),
        })
      }

      const data = await response.json()
      setDialogueId(data.dialogue_id)

      setMessages([
        {
          role: 'user',
          name: 'Moderator',
          content: initialPrompt,
          model: 'moderator',
        },
        ...(data.messages || []),
      ])
      setCurrentRound(1)
    } catch (error) {
      console.error('Dialogue error:', error)
    } finally {
      setIsLoading(false)
    }
  }

      setMessages([
        {
          role: 'user',
          name: 'Moderator',
          content: initialPrompt,
          model: 'moderator',
        },
        ...data.messages,
       ])

      setCurrentRound(1)
    } catch (error) {
      console.error('Dialogue error:', error)
    } finally {
      setIsLoading(false)
    }
  }
  }
            }),
        )

        setMessages([
          {
            role: 'user',
            name: 'Moderator',
            content: initialPrompt,
            model: 'moderator',
          },
          ...responses,
        ])
      }
      setCurrentRound(1)
    } catch (error) {
      console.error('Dialogue error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleNextRound = async () => {
      // Alternate between model1 and model2
      const currentModel = currentRound % 2 === 0 ? model2 : model1
      const currentPersona = currentRound % 2 === 0 ? persona2 : persona1

      setIsLoading(true)
      try {
        const response = await fetch('/api/chat/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: 'Continue the debate...',
            model: currentModel,
            source: 'Ollama (11434)',
          }),
        })

        const data = await response.json()
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            name: `${currentModel} (${currentPersona})`,
            content: data.response,
            model: currentModel,
            persona: currentPersona,
          },
        ])
        setCurrentRound((prev) => prev + 1)
      } catch (error) {
        console.error('Dialogue error:', error)
      } finally {
        setIsLoading(false)
      }
    } else {
      // Multi-participant debate
      const nextIndex = currentRound % 5
      const participant = multiParticipants[nextIndex]

      if (participant.model === 'user') {
        // User turn - wait for user input
        if (!userInput) return
        setMessages((prev) => [
          ...prev,
          {
            role: 'user',
            name: 'User',
            content: userInput,
            model: 'user',
          },
        ])
        setUserInput('')
        setCurrentRound((prev) => prev + 1)
      } else {
        // AI turn
        setIsLoading(true)
        try {
          const response = await fetch('/api/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message: 'Continue the debate...',
              model: participant.model,
              source: 'Ollama (11434)',
            }),
          })

          const data = await response.json()
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              name: `${participant.model} (${participant.persona})`,
              content: data.response,
              model: participant.model,
              persona: participant.persona,
            },
          ])
          setCurrentRound((prev) => prev + 1)
        } catch (error) {
          console.error('Dialogue error:', error)
        } finally {
          setIsLoading(false)
        }
      }
    }
  }

  const handleSaveDialogue = (format: 'txt' | 'pdf' | 'epub') => {
    if (format === 'txt') {
      const content = messages
        .map((msg) => `[${msg.role.toUpperCase()} - ${msg.name}]\n${msg.content}\n\n`)
        .join('\n' + '-'.repeat(50) + '\n\n')

      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `dialogue_${Date.now()}.txt`
      a.click()
      URL.revokeObjectURL(url)
    } else if (format === 'pdf') {
      try {
        const response = await fetch(`/api/dialogue/dialogue_${dialogueId}/export?format=pdf`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
        const data = await response.json()
        const blob = new Blob([data.content], { type: 'application/pdf' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = data.filename
        a.click()
        URL.revokeObjectURL(url)
      } catch (error) {
        console.error('PDF export error:', error)
        alert('PDF export failed. Please try TXT format.')
      }
    } else if (format === 'epub') {
      try {
        const response = await fetch(`/api/dialogue/dialogue_${dialogueId}/export?format=epub`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
        const data = await response.json()
        const blob = new Blob([data.content], { type: 'application/epub+zip' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = data.filename
        a.click()
        URL.revokeObjectURL(url)
      } catch (error) {
        console.error('EPUB export error:', error)
        alert('EPUB export failed. Please try TXT format.')
      }
    }
  }

  const isUserTurn = mode === 'multi' && currentRound % 5 === 4 && !isLoading

  if (!showDialogue) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-surface rounded-t-2xl w-full max-w-5xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-accent flex items-center gap-2">
            <Users className="w-5 h-5" />
            AI Debate
          </h3>
          <button
            onClick={() => {
              setShowDialogue(false)
              setMessages([])
              setCurrentRound(0)
            }}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mode Selector */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => {
              setMode('two')
              setMessages([])
              setCurrentRound(0)
            }}
            className={`px-4 py-2 rounded-lg font-medium ${
              mode === 'two' ? 'pill-btn-active' : 'pill-btn-inactive'
            }`}
          >
            2 Model Debate
          </button>
          <button
            onClick={() => {
              setMode('multi')
              setMessages([])
              setCurrentRound(0)
            }}
            className={`px-4 py-2 rounded-lg font-medium ${
              mode === 'multi' ? 'pill-btn-active' : 'pill-btn-inactive'
            }`}
          >
            5 Participant Debate
          </button>
        </div>

        {/* Configuration */}
        <div className="bg-background rounded-xl p-4 mb-4">
          <label className="block text-sm text-gray-300 mb-2">Initial Prompt / Topic</label>
          <textarea
            value={initialPrompt}
            onChange={(e) => setInitialPrompt(e.target.value)}
            placeholder="Enter a topic for the debate..."
            className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-accent resize-none"
            rows={3}
            disabled={messages.length > 0}
          />

          {mode === 'two' && (
            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2">Model 1</label>
                <select
                  value={model1}
                  onChange={(e) => setModel1(e.target.value)}
                  className="w-full bg-surface border border-gray-600 rounded-lg px-3 py-2 text-white mb-2"
                  disabled={messages.length > 0}
                >
                  {availableModels.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
                <label className="block text-sm text-gray-300 mb-2">MBTI Persona</label>
                <select
                  value={persona1}
                  onChange={(e) => setPersona1(e.target.value)}
                  className="w-full bg-surface border border-gray-600 rounded-lg px-3 py-2 text-white"
                  disabled={messages.length > 0}
                >
                  {MBTI_PERSONAS.map((persona) => (
                    <option key={persona} value={persona}>
                      {persona}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-300 mb-2">Model 2</label>
                <select
                  value={model2}
                  onChange={(e) => setModel2(e.target.value)}
                  className="w-full bg-surface border border-gray-600 rounded-lg px-3 py-2 text-white mb-2"
                  disabled={messages.length > 0}
                >
                  {availableModels.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
                <label className="block text-sm text-gray-300 mb-2">MBTI Persona</label>
                <select
                  value={persona2}
                  onChange={(e) => setPersona2(e.target.value)}
                  className="w-full bg-surface border border-gray-600 rounded-lg px-3 py-2 text-white"
                  disabled={messages.length > 0}
                >
                  {MBTI_PERSONAS.map((persona) => (
                    <option key={persona} value={persona}>
                      {persona}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {mode === 'multi' && (
            <div className="grid grid-cols-2 gap-2 mt-4">
              {multiParticipants.slice(0, 5).map((participant, index) => (
                <div key={participant.id} className="bg-surface p-2 rounded-lg">
                  <label className="block text-xs text-gray-400 mb-1">Participant {index + 1}</label>
                  <select
                    value={participant.model}
                    onChange={(e) => {
                      const newParticipants = [...multiParticipants]
                      newParticipants[index].model = e.target.value
                      setMultiParticipants(newParticipants)
                    }}
                    className="w-full bg-background border border-gray-600 rounded px-2 py-1 text-white text-xs mb-1"
                    disabled={messages.length > 0 || participant.id === 5}
                  >
                    {participant.id === 5 ? (
                      <option value="user">User (You)</option>
                    ) : (
                      availableModels.map((model) => (
                        <option key={model} value={model}>
                          {model}
                        </option>
                      ))
                    )}
                  </select>
                  <select
                    value={participant.persona}
                    onChange={(e) => {
                      const newParticipants = [...multiParticipants]
                      newParticipants[index].persona = e.target.value
                      setMultiParticipants(newParticipants)
                    }}
                    className="w-full bg-background border border-gray-600 rounded px-2 py-1 text-white text-xs"
                    disabled={messages.length > 0 || participant.id === 5}
                  >
                    {participant.id === 5 ? (
                      <option value="User">User</option>
                    ) : (
                      MBTI_PERSONAS.map((persona) => (
                        <option key={persona} value={persona}>
                          {persona}
                        </option>
                      ))
                    )}
                  </select>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2 mt-4">
            {messages.length === 0 && (
              <button
                onClick={handleStartDialogue}
                disabled={isLoading || !initialPrompt}
                className="flex-1 btn-primary flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                {isLoading ? 'Starting...' : 'Start Debate'}
              </button>
            )}
            {messages.length > 0 && (
              <>
                <button
                  onClick={handleNextRound}
                  disabled={isLoading || (isUserTurn && !userInput)}
                  className="flex-1 btn-primary flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                  {isLoading ? 'Thinking...' : isUserTurn ? 'Submit Response' : 'Next Round'}
                </button>
                <div className="relative">
                  <button
                    onClick={() => setExportMenuOpen(!exportMenuOpen)}
                    className="btn-secondary flex items-center justify-center gap-2"
                  >
                    <Save className="w-4 h-4" />
                    Export
                    <ChevronDown className="w-4 h-4" />
                  </button>
                  {exportMenuOpen && (
                    <div className="absolute right-0 top-full mt-2 bg-surface border border-gray-600 rounded-lg shadow-lg z-10 p-2 min-w-[150px]">
                      <button
                        onClick={() => handleSaveDialogue('txt')}
                        className="w-full text-left px-3 py-2 hover:bg-gray-700 rounded text-white text-sm"
                      >
                        📄 Save as TXT
                      </button>
                      <button
                        onClick={() => handleSaveDialogue('pdf')}
                        className="w-full text-left px-3 py-2 hover:bg-gray-700 rounded text-white text-sm"
                      >
                        📕 Save as PDF
                      </button>
                      <button
                        onClick={() => handleSaveDialogue('epub')}
                        className="w-full text-left px-3 py-2 hover:bg-gray-700 rounded text-white text-sm"
                      >
                        📚 Save as EPUB
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {isUserTurn && (
            <div className="mt-4">
              <label className="block text-sm text-gray-300 mb-2">Your Response</label>
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Type your response to the debate..."
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-accent resize-none"
                rows={3}
              />
            </div>
          )}
        </div>

        {/* Messages Display */}
        {messages.length > 0 && (
          <div className="bg-background rounded-xl p-4 max-h-96 overflow-y-auto">
            <h4 className="text-sm font-semibold text-gray-400 mb-4 flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Debate History (Round {currentRound})
            </h4>
            <div className="space-y-3">
              {messages.map((msg, index) => {
                const bgColor = mode === 'two'
                  ? (msg.model === model1 ? 'bg-yellow-900/30' : 'bg-purple-900/30')
                  : (msg.model === 'user' ? 'bg-white' : `bg-${['blue', 'green', 'red', 'orange'][index % 4]}-900/30`)

                return (
                  <div
                    key={index}
                    className={`${bgColor} p-3 rounded-lg border-l-4 ${
                      msg.role === 'user' ? 'border-gray-400' : `border-${['yellow', 'purple'][index % 2]}-500`
                    }`}
                  >
                    <div className="text-xs text-gray-400 mb-1">
                      {msg.name}
                      {msg.persona && ` • ${msg.persona}`}
                    </div>
                    <p className="text-sm text-white whitespace-pre-wrap">{msg.content}</p>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DialoguePanel
