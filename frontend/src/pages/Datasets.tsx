import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { datasetAPI } from '../services/api'
import type { Dataset } from '../types'
import { Database, FileText, Calendar, Search } from 'lucide-react'
import UploadModal from '../components/UploadModal'

export default function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [isUploadOpen, setIsUploadOpen] = useState(false)

  useEffect(() => {
    loadDatasets()
  }, [])

  const loadDatasets = async () => {
    try {
      const data = await datasetAPI.list()
      setDatasets(data)
    } catch (error) {
      console.error('Error loading datasets:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredDatasets = datasets.filter(dataset =>
    dataset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    dataset.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => {
          setIsUploadOpen(false)
          loadDatasets() // Refresh list after upload
        }}
      />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Datasets</h1>
          <p className="text-gray-600 mt-1">{datasets.length} datasets</p>
        </div>
        <button
          onClick={() => setIsUploadOpen(true)}
          className="btn btn-primary"
        >
          Upload Dataset
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search datasets..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Datasets List */}
      {filteredDatasets.length === 0 ? (
        <div className="card text-center py-12">
          <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">
            {searchQuery ? 'No datasets match your search' : 'No datasets yet'}
          </p>
          {!searchQuery && (
            <button
              onClick={() => setIsUploadOpen(true)}
              className="btn btn-primary mt-4"
            >
              Upload Your First Dataset
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredDatasets.map((dataset) => (
            <Link
              key={dataset.id}
              to={`/datasets/${dataset.id}`}
              className="block card hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <FileText className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <h3 className="font-medium text-gray-900">{dataset.name}</h3>
                    {dataset.description && (
                      <p className="text-sm text-gray-600 mt-1">{dataset.description}</p>
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
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
