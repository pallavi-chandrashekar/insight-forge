import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { datasetAPI, queryAPI } from '../services/api'
import type { Dataset, QueryHistoryItem } from '../types'
import { Database, Search, Upload, FileText, Calendar, Sparkles } from 'lucide-react'
import SmartImportModal from '../components/SmartImportModal'
import UploadModal from '../components/UploadModal'
import QueryHistoryModal from '../components/QueryHistoryModal'
import DatasetsModal from '../components/DatasetsModal'

export default function Dashboard() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [recentQueries, setRecentQueries] = useState<QueryHistoryItem[]>([])
  const [totalQueries, setTotalQueries] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isSmartImportOpen, setIsSmartImportOpen] = useState(false)
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isQueryHistoryOpen, setIsQueryHistoryOpen] = useState(false)
  const [isDatasetsOpen, setIsDatasetsOpen] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [datasetsData, queriesData] = await Promise.all([
        datasetAPI.list(),
        queryAPI.history(),
      ])
      setDatasets(datasetsData)
      setTotalQueries(queriesData.length)
      setRecentQueries(queriesData.slice(0, 5))
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to InsightForge</p>
      </div>

      {/* Modals */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
      />
      <SmartImportModal
        isOpen={isSmartImportOpen}
        onClose={() => setIsSmartImportOpen(false)}
      />
      <QueryHistoryModal
        isOpen={isQueryHistoryOpen}
        onClose={() => setIsQueryHistoryOpen(false)}
      />
      <DatasetsModal
        isOpen={isDatasetsOpen}
        onClose={() => setIsDatasetsOpen(false)}
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <button
            onClick={() => setIsDatasetsOpen(true)}
            className="flex items-center justify-between hover:bg-gray-50 transition-colors -m-6 p-6 rounded-lg w-full text-left"
          >
            <div>
              <p className="text-gray-600 text-sm">Total Datasets</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{datasets.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
          </button>
        </div>

        <div className="card">
          <button
            onClick={() => setIsQueryHistoryOpen(true)}
            className="flex items-center justify-between hover:bg-gray-50 transition-colors -m-6 p-6 rounded-lg w-full text-left"
          >
            <div>
              <p className="text-gray-600 text-sm">Total Queries</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{totalQueries}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Search className="w-6 h-6 text-green-600" />
            </div>
          </button>
        </div>

        <div className="card">
          <button
            onClick={() => setIsUploadOpen(true)}
            className="flex items-center justify-between hover:bg-gray-50 transition-colors -m-6 p-6 rounded-lg w-full text-left"
          >
            <div>
              <p className="text-gray-600 text-sm">Quick Action</p>
              <p className="text-lg font-semibold text-gray-900 mt-1">Upload Dataset</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Upload className="w-6 h-6 text-blue-600" />
            </div>
          </button>
        </div>

        <div className="card">
          <button
            onClick={() => setIsSmartImportOpen(true)}
            className="flex items-center justify-between hover:bg-gray-50 transition-all -m-6 p-6 rounded-lg w-full text-left"
          >
            <div>
              <p className="text-gray-600 text-sm">Smart Import</p>
              <p className="text-lg font-semibold text-gray-900 mt-1">Any URL</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-blue-600" />
            </div>
          </button>
        </div>
      </div>

      {/* Recent Datasets */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Recent Datasets</h2>
          <button
            onClick={() => setIsUploadOpen(true)}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Upload New
          </button>
        </div>

        {datasets.length === 0 ? (
          <div className="text-center py-12">
            <Database className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No datasets yet</p>
            <button
              onClick={() => setIsUploadOpen(true)}
              className="btn btn-primary mt-4 inline-flex"
            >
              Upload Your First Dataset
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {datasets.slice(0, 5).map((dataset) => (
              <Link
                key={dataset.id}
                to={`/datasets/${dataset.id}`}
                className="block p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
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

      {/* Recent Queries */}
      {recentQueries.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Queries</h2>
          <div className="space-y-3">
            {recentQueries.map((query) => (
              <div
                key={query.id}
                className="p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{query.original_input}</p>
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                      <span className="capitalize">{query.query_type.replace('_', ' ')}</span>
                      <span>Dataset: {query.dataset_name}</span>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(query.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
