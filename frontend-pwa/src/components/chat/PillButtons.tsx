import React from 'react'
import type { LucideIcon } from 'lucide-react'
import { RotateCcw, Settings, MessageSquare, Search, Users, FileText, Download, Cpu } from 'lucide-react'
import { useChat } from '../../contexts/ChatContext'

interface PillButton {
  id: string
  label: string
  icon: LucideIcon | null
  action: () => void
}

interface PillButtonsProps {
  buttons: PillButton[]
}

const PillButtons: React.FC<PillButtonsProps> = ({ buttons }) => {
  return (
    <div className="flex flex-wrap justify-center gap-2 p-4 border-t border-gray-800">
      {buttons.map((button) => {
        const Icon = button.icon
        return (
          <button
            key={button.id}
            onClick={button.action}
            className="pill-btn pill-btn-inactive"
          >
            {Icon && <Icon className="w-4 h-4" />}
            <span>{button.label}</span>
          </button>
        )
      })}
    </div>
  )
}

export const FullToolbar: React.FC = () => {
  const {
    clearMessages,
    setShowSystem,
    setShowHistory,
    setShowAgents,
    setShowDialogue,
    setShowDocs,
    setShowExport,
    currentModel,
  } = useChat()

  const pillButtons: PillButton[] = [
    { id: 'clear', label: 'Clear', icon: RotateCcw, action: clearMessages },
    { id: 'system', label: 'System', icon: Settings, action: () => setShowSystem(true) },
    { id: 'history', label: 'History', icon: MessageSquare, action: () => setShowHistory(true) },
    { id: 'agents', label: 'Agents', icon: Search, action: () => setShowAgents(true) },
    { id: 'dialogue', label: 'Dialogue', icon: Users, action: () => setShowDialogue(true) },
    { id: 'docs', label: 'Docs', icon: FileText, action: () => setShowDocs(true) },
    { id: 'model', label: currentModel.substring(0, 20), icon: Cpu, action: () => {} },
    { id: 'export', label: 'Export', icon: Download, action: () => setShowExport(true) },
  ]

  return <PillButtons buttons={pillButtons} />
}

export default PillButtons