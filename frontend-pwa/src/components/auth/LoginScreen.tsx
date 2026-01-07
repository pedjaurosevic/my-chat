import React, { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'

const LoginScreen: React.FC = () => {
  const [pin, setPin] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (pin.length !== 4) {
      setError('PIN must be 4 digits')
      return
    }

    const success = await login(pin)
    if (!success) {
      setError('Invalid PIN')
      setPin('')
    }
  }

  const handleKeyPress = (key: string) => {
    if (key === 'clear') {
      setPin('')
    } else if (key === 'backspace') {
      setPin(prev => prev.slice(0, -1))
    } else if (pin.length < 4 && /^\d$/.test(key)) {
      setPin(prev => prev + key)
    }
  }

  const keypadButtons = [
    '1', '2', '3',
    '4', '5', '6',
    '7', '8', '9',
    'clear', '0', 'backspace'
  ]

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-surface p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-accent mb-2">OLLAMA.CORE</h1>
          <p className="text-gray-400">Private AI Chat</p>
        </div>

        {/* PIN Display */}
        <div className="bg-surface/50 backdrop-blur-md rounded-2xl p-6 mb-6 border border-white/10">
          <div className="text-center mb-4">
            <label className="text-accent font-medium">Enter PIN</label>
          </div>

          <div className="flex justify-center gap-4 mb-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className={`w-12 h-12 rounded-xl border-2 flex items-center justify-center text-2xl font-bold transition-all ${
                  i < pin.length
                    ? 'bg-accent text-background border-accent'
                    : 'border-gray-600 bg-surface'
                }`}
              >
                {i < pin.length ? '●' : ''}
              </div>
            ))}
          </div>

          {error && (
            <div className="text-red-400 text-center text-sm mb-4">
              {error}
            </div>
          )}
        </div>

        {/* Keypad */}
        <div className="bg-surface/50 backdrop-blur-md rounded-2xl p-6 border border-white/10">
          <div className="grid grid-cols-3 gap-3">
            {keypadButtons.map((key) => (
              <button
                key={key}
                onClick={() => handleKeyPress(key)}
                className={`aspect-square rounded-xl font-bold text-lg transition-all active:scale-95 ${
                  key === 'clear'
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : key === 'backspace'
                    ? 'bg-orange-600 hover:bg-orange-700 text-white'
                    : 'bg-surface hover:bg-gray-700 text-white border border-gray-600'
                }`}
              >
                {key === 'clear' ? '⌫' : key === 'backspace' ? '←' : key}
              </button>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={pin.length !== 4}
            className="w-full mt-6 py-3 rounded-xl font-bold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed bg-accent hover:bg-accent/80 text-background active:scale-95"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  )
}

export default LoginScreen