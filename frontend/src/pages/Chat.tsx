import { useState, useEffect } from 'react'
import contextService, { Context } from '../services/contextService'
import ContextChat from '../components/ContextChat'
import { MessageCircle, ChevronDown, FileText, AlertCircle } from 'lucide-react'

export default function Chat() {
  const [contexts, setContexts] = useState<Context[]>([])
  const [selectedContext, setSelectedContext] = useState<Context | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [chatKey, setChatKey] = useState(0) // Used to reset chat when context changes

  useEffect(() => {
    loadContexts()
  }, [])

  const loadContexts = async () => {
    try {
      setIsLoading(true)
      const data = await contextService.listContexts({ status: 'active' })
      setContexts(data)

      // Auto-select first context if available
      if (data.length > 0 && !selectedContext) {
        setSelectedContext(data[0])
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load contexts')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectContext = (context: Context) => {
    setSelectedContext(context)
    setChatKey(prev => prev + 1) // Reset chat when context changes
    setIsDropdownOpen(false)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col">
      {/* Header with Context Selector */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Chat</h1>
            <p className="text-gray-600">Ask questions about your documentation</p>
          </div>

          {/* Context Dropdown */}
          {contexts.length > 0 && (
            <div className="relative">
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center space-x-3 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 min-w-[250px]"
              >
                <FileText className="w-5 h-5 text-gray-400" />
                <span className="flex-1 text-left truncate">
                  {selectedContext ? selectedContext.name : 'Select a document'}
                </span>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-80 overflow-y-auto">
                  {contexts.map((context) => (
                    <button
                      key={context.id}
                      onClick={() => handleSelectContext(context)}
                      className={`w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                        selectedContext?.id === context.id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="font-medium text-gray-900 truncate">{context.name}</div>
                      <div className="text-sm text-gray-500 truncate">{context.description}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        {context.datasets_count} datasets • {context.context_type}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 min-h-0">
        {contexts.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Documents Available</h3>
              <p className="text-gray-500 mb-4">
                Upload a document or create a context to start chatting.
              </p>
              <a href="/upload" className="btn btn-primary">
                Upload Data
              </a>
            </div>
          </div>
        ) : selectedContext ? (
          <ContextChat
            key={chatKey}
            contextId={selectedContext.id}
            contextName={selectedContext.name}
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Document</h3>
              <p className="text-gray-500">
                Choose a document from the dropdown above to start chatting.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
