import { useEffect, useState } from 'react'
import { datasetAPI, queryAPI } from '../services/api'
import type { Dataset, Query as QueryType } from '../types'
import { Search, Code, Database } from 'lucide-react'

export default function Query() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [selectedDataset, setSelectedDataset] = useState<string>('')
  const [queryMode, setQueryMode] = useState<'natural' | 'sql'>('natural')
  const [queryInput, setQueryInput] = useState('')
  const [result, setResult] = useState<QueryType | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadDatasets()
  }, [])

  const loadDatasets = async () => {
    try {
      const data = await datasetAPI.list()
      setDatasets(data)
      if (data.length > 0) {
        setSelectedDataset(data[0].id)
      }
    } catch (error) {
      console.error('Error loading datasets:', error)
    }
  }

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedDataset || !queryInput.trim()) return

    setIsLoading(true)
    setResult(null)

    try {
      const data =
        queryMode === 'natural'
          ? await queryAPI.naturalLanguage(selectedDataset, queryInput)
          : await queryAPI.execute(selectedDataset, 'sql', queryInput)
      setResult(data)
    } catch (error: any) {
      console.error('Query execution error:', error)
      alert(error.response?.data?.detail || 'Query execution failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Query Builder</h1>
        <p className="text-gray-600 mt-2">Ask questions in natural language or write SQL</p>
      </div>

      <div className="card">
        <form onSubmit={handleExecute} className="space-y-4">
          {/* Dataset Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Select Dataset
            </label>
            <select
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              className="input"
              required
            >
              {datasets.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.row_count?.toLocaleString()} rows)
                </option>
              ))}
            </select>
          </div>

          {/* Query Mode Selection */}
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => setQueryMode('natural')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                queryMode === 'natural'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <Search className="w-5 h-5" />
              <span>Natural Language</span>
            </button>
            <button
              type="button"
              onClick={() => setQueryMode('sql')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                queryMode === 'sql'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <Code className="w-5 h-5" />
              <span>SQL</span>
            </button>
          </div>

          {/* Query Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {queryMode === 'natural' ? 'Ask a question' : 'SQL Query'}
            </label>
            <textarea
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              className="input font-mono"
              rows={queryMode === 'natural' ? 3 : 8}
              placeholder={
                queryMode === 'natural'
                  ? 'e.g., What are the top 10 products by revenue?'
                  : 'SELECT * FROM df WHERE ...'
              }
              required
            />
            {queryMode === 'sql' && (
              <p className="text-sm text-gray-500 mt-1">
                Use "df" as the table name in your SQL query
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading || !selectedDataset}
            className="btn btn-primary"
          >
            {isLoading ? 'Executing...' : 'Execute Query'}
          </button>
        </form>
      </div>

      {/* Query Result */}
      {result && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Results</h2>
            {result.execution_time_ms && (
              <span className="text-sm text-gray-500">
                Executed in {result.execution_time_ms}ms
              </span>
            )}
          </div>

          {result.error_message ? (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              <p className="font-medium">Error:</p>
              <p className="mt-1">{result.error_message}</p>
            </div>
          ) : (
            <>
              {result.generated_query && (
                <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-700 mb-2">Generated SQL:</p>
                  <pre className="text-sm text-gray-800 font-mono overflow-x-auto">
                    {result.generated_query}
                  </pre>
                </div>
              )}

              {result.result_preview && result.result_preview.length > 0 ? (
                <div>
                  <p className="text-sm text-gray-600 mb-3">
                    Showing {result.result_preview.length} of {result.result_row_count} rows
                  </p>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {Object.keys(result.result_preview[0]).map((key) => (
                            <th
                              key={key}
                              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {result.result_preview.map((row, idx) => (
                          <tr key={idx}>
                            {Object.values(row).map((value, colIdx) => (
                              <td
                                key={colIdx}
                                className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                              >
                                {String(value ?? '')}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No results</p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
