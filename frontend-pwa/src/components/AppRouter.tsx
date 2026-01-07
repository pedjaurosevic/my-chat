import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import LoginScreen from './auth/LoginScreen'
import ChatScreen from './chat/ChatScreen'

const AppRouter: React.FC = () => {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <LoginScreen />
  }

  return <ChatScreen />
}

export default AppRouter