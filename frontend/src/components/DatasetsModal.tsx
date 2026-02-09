import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { datasetAPI } from '../services/api'
import type { Dataset } from '../types'
import { X, Database, FileText, Calendar, Search } from 'lucide-react'

interface DatasetsModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function DatasetsModal({ isOpen, onClose }: DatasetsModalProps) {
  const navigate = useNavigate()
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadDatasets()
    }
  }, [isOpen])

  const loadDatasets = async () => {
    try {
      setIsLoading(true)
      const data = await datasetAPI.list()
      setDatasets(data)
    } catch (error) {
      console.error('Error loading datasets:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  const filteredDatasets = datasets.filter(dataset =>
    dataset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    dataset.description?.toLowerCase().includes(searchQuery.toLowerCase())
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
            <div className="p-2 bg-blue-100 rounded-lg">
              <Database className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Datasets</h2>
              <p className="text-sm text-gray-500">{datasets.length} datasets</p>
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
              placeholder="Search datasets..."
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
          ) : filteredDatasets.length === 0 ? (
            <div className="text-center py-12">
              <Database className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">
                {searchQuery ? 'No datasets match your search' : 'No datasets yet'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredDatasets.map((dataset) => (
                <button
                  key={dataset.id}
                  onClick={() => handleViewDataset(dataset.id)}
                  className="w-full p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <FileText className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <h3 className="font-medium text-gray-900">{dataset.name}</h3>
                        {dataset.description && (
                          <p className="text-sm text-gray-600 mt-1 line-clamp-1">{dataset.description}</p>
                        )}
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                          <span>{dataset.row_count?.toLocaleString()} rows</span>
                          <span>{dataset.column_count} columns</span>
                          <span className="capitalize">{dataset.source_type}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center text-sm text-gray-500">
                      <Calendar className="w-4 h-4 mr-1" />
                      {new Date(dataset.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </button>
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
