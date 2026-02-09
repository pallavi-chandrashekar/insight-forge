import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { queryAPI } from '../services/api'
import type { QueryHistoryItem } from '../types'
import { X, Search, Calendar, Database, ExternalLink } from 'lucide-react'

interface QueryHistoryModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function QueryHistoryModal({ isOpen, onClose }: QueryHistoryModalProps) {
  const navigate = useNavigate()
  const [queries, setQueries] = useState<QueryHistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadHistory()
    }
  }, [isOpen])

  const loadHistory = async () => {
    try {
      setIsLoading(true)
      const data = await queryAPI.history()
      setQueries(data)
    } catch (error) {
      console.error('Error loading query history:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  const filteredQueries = queries.filter(query =>
    query.original_input.toLowerCase().includes(searchQuery.toLowerCase()) ||
    query.dataset_name?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleViewDataset = (datasetId: string) => {
    onClose()
    navigate(`/datasets/${datasetId}`)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Search className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Query History</h2>
              <p className="text-sm text-gray-500">{queries.length} queries</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search queries..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-gray-500">Loading...</div>
            </div>
          ) : filteredQueries.length === 0 ? (
            <div className="text-center py-12">
              <Search className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">
                {searchQuery ? 'No queries match your search' : 'No queries yet'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredQueries.map((query) => (
                <div
                  key={query.id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                >
                  <p className="font-medium text-gray-900">{query.original_input}</p>
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-xs">
                        {query.query_type.replace('_', ' ')}
                      </span>
                      <span className="flex items-center">
                        <Database className="w-3 h-3 mr-1" />
                        {query.dataset_name}
                      </span>
                      <span className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {new Date(query.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <button
                      onClick={() => handleViewDataset(query.dataset_id)}
                      className="text-blue-600 hover:text-blue-700 text-sm flex items-center"
                    >
                      View Dataset
                      <ExternalLink className="w-3 h-3 ml-1" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full text-gray-500 hover:text-gray-700 text-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
