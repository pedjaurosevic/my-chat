import React from 'react'
import type { Message } from '../../contexts/ChatContext'
import { User, Bot } from 'lucide-react'

interface MessageBubbleProps {
  message: Message
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-start space-x-3 max-w-xs lg:max-w-md xl:max-w-lg ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-accent' : 'bg-surface'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-background" />
          ) : (
            <Bot className="w-4 h-4 text-accent" />
          )}
        </div>

        {/* Message Content */}
        <div className={`rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-accent text-background'
            : 'bg-surface text-white'
        }`}>
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.content}
          </div>

          {/* Timestamp */}
          <div className={`text-xs mt-2 ${
            isUser ? 'text-background/70' : 'text-gray-400'
          }`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            {message.model && !isUser && (
              <span className="ml-2 opacity-75">• {message.model}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default MessageBubble