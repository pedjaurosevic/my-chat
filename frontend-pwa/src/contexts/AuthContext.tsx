import React, { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'

interface AuthContextType {
  isAuthenticated: boolean
  login: (pin: string) => Promise<boolean>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if already authenticated on app start (24 hour session)
    const authTimestamp = localStorage.getItem('ollama-auth-timestamp')
    if (authTimestamp) {
      const loginTime = parseInt(authTimestamp)
      const now = Date.now()
      const twentyFourHours = 24 * 60 * 60 * 1000

      if (now - loginTime < twentyFourHours) {
        setIsAuthenticated(true)
      } else {
        localStorage.removeItem('ollama-auth-timestamp')
      }
    }
  }, [])

  const login = async (pin: string): Promise<boolean> => {
    // Simple PIN check - in production, this would call your API
    if (pin === '2020') {
      setIsAuthenticated(true)
      localStorage.setItem('ollama-auth-timestamp', Date.now().toString())
      return true
    }
    return false
  }

  const logout = () => {
    setIsAuthenticated(false)
    localStorage.removeItem('ollama-auth-timestamp')
  }

  const value = {
    isAuthenticated,
    login,
    logout,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}