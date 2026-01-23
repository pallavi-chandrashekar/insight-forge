import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { datasetAPI } from '../services/api'
import type { Dataset, DatasetPreview } from '../types'
import { ArrowLeft, Trash2, FileText } from 'lucide-react'

export default function DatasetPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [dataset, setDataset] = useState<Dataset | null>(null)
  const [preview, setPreview] = useState<DatasetPreview | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    if (id) loadDataset(id)
  }, [id])

  const loadDataset = async (datasetId: string) => {
    try {
      const [datasetData, previewData] = await Promise.all([
        datasetAPI.get(datasetId),
        datasetAPI.preview(datasetId, 20),
      ])
      setDataset(datasetData)
      setPreview(previewData)
    } catch (error) {
      console.error('Error loading dataset:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!id || !confirm('Are you sure you want to delete this dataset?')) return

    setIsDeleting(true)
    try {
      await datasetAPI.delete(id)
      navigate('/dashboard')
    } catch (error) {
      console.error('Error deleting dataset:', error)
      alert('Failed to delete dataset')
      setIsDeleting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dataset...</div>
      </div>
    )
  }

  if (!dataset || !preview) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Dataset not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="btn btn-secondary"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center space-x-3">
              <FileText className="w-6 h-6 text-gray-400" />
              <h1 className="text-3xl font-bold text-gray-900">{dataset.name}</h1>
            </div>
            {dataset.description && (
              <p className="text-gray-600 mt-2">{dataset.description}</p>
            )}
            <div className="flex items-center space-x-6 mt-4 text-sm text-gray-500">
              <span>{dataset.row_count?.toLocaleString()} rows</span>
              <span>{dataset.column_count} columns</span>
              <span className="capitalize">{dataset.source_type}</span>
              <span>{new Date(dataset.created_at).toLocaleString()}</span>
            </div>
          </div>
        </div>

        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="btn btn-danger flex items-center space-x-2"
        >
          <Trash2 className="w-5 h-5" />
          <span>{isDeleting ? 'Deleting...' : 'Delete'}</span>
        </button>
      </div>

      {/* Schema */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Schema</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Column
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nullable
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sample Values
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dataset.schema?.columns.map((column, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {column.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {column.dtype}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {column.nullable ? 'Yes' : 'No'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {column.sample_values.slice(0, 3).map(String).join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Preview */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Data Preview ({preview.preview_rows} of {preview.total_rows.toLocaleString()} rows)
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {preview.columns.map((column) => (
                  <th
                    key={column}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {preview.data.map((row, idx) => (
                <tr key={idx}>
                  {preview.columns.map((column) => (
                    <td
                      key={column}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                    >
                      {String(row[column] ?? '')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
