'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://syfl-ai-backend.onrender.com'

export default function Home() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLogin, setIsLogin] = useState(true)
  const [token, setToken] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [chatMessages, setChatMessages] = useState<Array<{role: string, content: string}>>([])
  const [userInput, setUserInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      if (isLogin) {
        const formData = new FormData()
        formData.append('username', email)
        formData.append('password', password)
        
        const res = await axios.post(`${API_URL}/auth/login`, formData)
        setToken(res.data.access_token)
        setMessage('Connexion réussie !')
      } else {
        // Validation du mot de passe côté frontend
        if (password.length < 8) {
          setMessage('Le mot de passe doit contenir au moins 8 caractères')
          setLoading(false)
          return
        }
        if (!/[A-Z]/.test(password)) {
          setMessage('Le mot de passe doit contenir au moins une majuscule')
          setLoading(false)
          return
        }
        if (!/[a-z]/.test(password)) {
          setMessage('Le mot de passe doit contenir au moins une minuscule')
          setLoading(false)
          return
        }
        if (!/[0-9]/.test(password)) {
          setMessage('Le mot de passe doit contenir au moins un chiffre')
          setLoading(false)
          return
        }

        // Extraire username de l'email (partie avant @)
        const usernameFromEmail = email.split('@')[0].replace(/[^a-zA-Z0-9_]/g, '_')
        await axios.post(`${API_URL}/auth/register`, {
          email,
          username: usernameFromEmail,
          password,
          full_name: usernameFromEmail
        })
        setMessage('Inscription réussie ! Connectez-vous maintenant.')
        setIsLogin(true)
      }
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Erreur lors de l\'authentification')
    } finally {
      setLoading(false)
    }
  }

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!userInput.trim() || !token) return

    setLoading(true)
    const newMessage = { role: 'user', content: userInput }
    setChatMessages([...chatMessages, newMessage])
    setUserInput('')

    try {
      const res = await axios.post(
        `${API_URL}/chat`,
        { message: userInput },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      setChatMessages(prev => [...prev, { role: 'assistant', content: res.data.response }])
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Erreur lors du chat')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    setToken(null)
    setChatMessages([])
    setMessage('')
  }

  if (!token) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-6 bg-gradient-to-br from-green-50 to-blue-50">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-3xl font-bold text-center mb-2 text-gray-800">
            SYFL AI
          </h1>
          <p className="text-center text-gray-600 mb-6">
            Assistant Juridique pour le Droit du Travail Togolais
          </p>

          <form onSubmit={handleAuth} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
              {!isLogin && (
                <p className="mt-1 text-xs text-gray-500">
                  Min. 8 caractères avec majuscule, minuscule et chiffre
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Chargement...' : isLogin ? 'Se connecter' : 'S\'inscrire'}
            </button>
          </form>

          <button
            onClick={() => setIsLogin(!isLogin)}
            className="w-full mt-4 text-sm text-green-600 hover:text-green-700"
          >
            {isLogin ? 'Pas de compte ? S\'inscrire' : 'Déjà un compte ? Se connecter'}
          </button>

          {message && (
            <div className={`mt-4 p-3 rounded-lg text-sm ${
              message.includes('réussie') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {message}
            </div>
          )}
        </div>
      </main>
    )
  }

  return (
    <main className="flex min-h-screen flex-col bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-green-600">SYFL AI</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm text-red-600 hover:text-red-700 font-medium"
          >
            Déconnexion
          </button>
        </div>
      </header>

      <div className="flex-1 max-w-4xl w-full mx-auto p-4">
        <div className="bg-white rounded-2xl shadow-lg h-[calc(100vh-12rem)] flex flex-col">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {chatMessages.length === 0 ? (
              <div className="text-center text-gray-500 mt-20">
                <p className="text-xl mb-2">👋 Bonjour !</p>
                <p>Posez-moi une question sur le droit du travail togolais</p>
              </div>
            ) : (
              chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl px-4 py-3">
                  <p className="text-gray-600">En train de réfléchir...</p>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleChat} className="border-t p-4 flex gap-2">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Posez votre question..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !userInput.trim()}
              className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-full transition disabled:opacity-50"
            >
              Envoyer
            </button>
          </form>
        </div>
      </div>

      {message && (
        <div className="fixed bottom-4 right-4 bg-red-100 text-red-800 px-4 py-2 rounded-lg shadow-lg">
          {message}
        </div>
      )}
    </main>
  )
}
