import { useState, useRef, useEffect } from 'react'
import { contextChatAPI } from '../services/api'
import type { ContextChatMessage } from '../types'
import { Send, Loader2, Sparkles, MessageCircle } from 'lucide-react'

interface ContextChatProps {
  contextId: string
  contextName: string
}

interface MessageWithSources extends ContextChatMessage {
  sources?: string[]
}

export default function ContextChat({ contextId, contextName }: ContextChatProps) {
  const [messages, setMessages] = useState<MessageWithSources[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [followUpSuggestions, setFollowUpSuggestions] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (question?: string) => {
    const questionText = question || input.trim()
    if (!questionText || isLoading) return

    // Add user message
    const userMessage: ContextChatMessage = {
      role: 'user',
      content: questionText
    }

    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput('')
    setIsLoading(true)
    setFollowUpSuggestions([])

    try {
      const response = await contextChatAPI.askQuestion({
        context_id: contextId,
        question: questionText,
        conversation_history: messages
      })

      // Add assistant message with sources
      const assistantMessage: MessageWithSources = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources || []
      }

      setMessages([...newMessages, assistantMessage])

      // Set follow-up suggestions
      if (response.follow_up_suggestions) {
        setFollowUpSuggestions(response.follow_up_suggestions)
      }
    } catch (error: any) {
      // Add error message
      const errorMessage: ContextChatMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}`
      }
      setMessages([...newMessages, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <MessageCircle className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Ask About Documentation</h3>
            <p className="text-sm text-gray-500">{contextName}</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h4 className="font-medium text-gray-900 mb-2">Ask me anything about this documentation!</h4>
            <p className="text-sm text-gray-500 mb-4">I can help you understand the content, explain concepts, and find information.</p>
            <div className="space-y-2">
              <p className="text-xs text-gray-400 font-medium">Try asking:</p>
              <button
                onClick={() => handleSubmit("What are the main topics covered in this documentation?")}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                "What are the main topics covered?"
              </button>
              <button
                onClick={() => handleSubmit("Summarize the key concepts")}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                "Summarize the key concepts"
              </button>
              <button
                onClick={() => handleSubmit("What best practices are mentioned?")}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                "What best practices are mentioned?"
              </button>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            </div>

            {/* Show sources for assistant messages */}
            {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
              <div className="mt-2 max-w-3xl">
                <p className="text-xs font-medium text-gray-500 mb-1">📚 Sources:</p>
                <div className="flex flex-wrap gap-2">
                  {message.sources.map((source, sourceIndex) => (
                    <span
                      key={sourceIndex}
                      className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded border border-blue-200"
                    >
                      {source}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <Loader2 className="w-5 h-5 text-gray-500 animate-spin" />
            </div>
          </div>
        )}

        {/* Follow-up suggestions */}
        {followUpSuggestions.length > 0 && !isLoading && (
          <div className="space-y-2 pt-4">
            <p className="text-xs font-medium text-gray-500">Suggested follow-up questions:</p>
            {followUpSuggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSubmit(suggestion)}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors border border-blue-200"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="flex space-x-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about this documentation..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={() => handleSubmit()}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">Press Enter to send, Shift+Enter for new line</p>
      </div>
    </div>
  )
}
