import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { datasetAPI, smartImportAPI } from '../services/api'
import contextService from '../services/contextService'
import type { SmartImportResponse } from '../types'
import { Upload as UploadIcon, Sparkles, Loader2, CheckCircle, AlertCircle, FileText, Link } from 'lucide-react'

type Mode = 'file' | 'url'

export default function Upload() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<Mode>('file')
  const [isLoading, setIsLoading] = useState(false)
  const [uploadStep, setUploadStep] = useState('')
  const [error, setError] = useState<string | null>(null)

  // File upload state
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [contextSource, setContextSource] = useState<'none' | 'file' | 'url'>('none')
  const [contextFile, setContextFile] = useState<File | null>(null)
  const [contextUrl, setContextUrl] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState<{
    datasetId: string
    datasetName: string
    contextId?: string
    contextName?: string
  } | null>(null)

  // Smart Import state
  const [url, setUrl] = useState('')
  const [urlName, setUrlName] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<SmartImportResponse | null>(null)
  const [success, setSuccess] = useState<{ type: string; name: string; id: string } | null>(null)

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setIsLoading(true)
    setError(null)

    try {
      // Step 1: Upload dataset
      setUploadStep('Uploading dataset...')
      const dataset = await datasetAPI.upload(file, name, description)

      let contextResult = undefined

      // Step 2: Create context if provided
      if (contextSource === 'file' && contextFile) {
        setUploadStep('Creating context from file...')
        try {
          const context = await contextService.uploadContextFile(contextFile)
          contextResult = {
            contextId: context.id,
            contextName: context.name
          }
        } catch (contextErr: any) {
          console.error('Context upload failed:', contextErr)
        }
      } else if (contextSource === 'url' && contextUrl.trim()) {
        setUploadStep('Creating context from URL...')
        try {
          const response = await smartImportAPI.createContextFromUrl(contextUrl, name + ' Context')
          contextResult = {
            contextId: response.context_id,
            contextName: response.context_name
          }
        } catch (contextErr: any) {
          console.error('Context creation from URL failed:', contextErr)
        }
      }

      setUploadSuccess({
        datasetId: dataset.id,
        datasetName: name,
        ...contextResult
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setIsLoading(false)
      setUploadStep('')
    }
  }

  const handleAnalyzeUrl = async () => {
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    setIsAnalyzing(true)
    setError(null)
    setAnalysisResult(null)

    try {
      const result = await smartImportAPI.analyzeUrl(url, urlName || undefined)
      setAnalysisResult(result)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze URL')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleImportData = async () => {
    if (!url.trim() || !urlName.trim()) {
      setError('Please enter both URL and name')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const dataset = await datasetAPI.importFromUrl(urlName, url)
      setSuccess({ type: 'dataset', name: urlName, id: dataset.id })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateContext = async () => {
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await smartImportAPI.createContextFromUrl(url, urlName || undefined)
      setSuccess({ type: 'context', name: response.context_name || urlName || 'Context', id: response.context_id })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create context')
    } finally {
      setIsLoading(false)
    }
  }

  const resetUrlForm = () => {
    setUrl('')
    setUrlName('')
    setAnalysisResult(null)
    setSuccess(null)
    setError(null)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Import Data</h1>

      {/* Two options as tabs */}
      <div className="flex space-x-4 mb-6">
        <button
          onClick={() => { setMode('file'); setError(null); }}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            mode === 'file'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <UploadIcon className="w-5 h-5" />
          <span>Upload File</span>
        </button>
        <button
          onClick={() => { setMode('url'); setError(null); }}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            mode === 'url'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          <Sparkles className="w-5 h-5" />
          <span>Smart Import</span>
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-start space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* File Upload Form */}
      {mode === 'file' && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-2">Upload from Computer</h2>
          <p className="text-gray-600 mb-6">
            Upload CSV, JSON, Excel, or Parquet files directly from your computer.
            Your data will be analyzed and ready for visualization and querying.
          </p>

          {/* Success State */}
          {uploadSuccess ? (
            <div className="text-center py-8">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Upload Complete!</h3>
              <div className="text-gray-600 mb-6 space-y-1">
                <p>Dataset "{uploadSuccess.datasetName}" uploaded successfully.</p>
                {uploadSuccess.contextId && (
                  <p className="text-sm text-green-600">Context "{uploadSuccess.contextName}" created.</p>
                )}
              </div>
              <div className="space-x-3">
                <button
                  onClick={() => navigate(`/datasets/${uploadSuccess.datasetId}`)}
                  className="btn btn-primary"
                >
                  View Dataset
                </button>
                {uploadSuccess.contextId && (
                  <button
                    onClick={() => navigate(`/contexts/${uploadSuccess.contextId}`)}
                    className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
                  >
                    View Context
                  </button>
                )}
                <button
                  onClick={() => {
                    setFile(null)
                    setName('')
                    setDescription('')
                    setContextSource('none')
                    setContextFile(null)
                    setContextUrl('')
                    setUploadSuccess(null)
                  }}
                  className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
                >
                  Upload Another
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleFileUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dataset File
                </label>
                <input
                  type="file"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  accept=".csv,.json,.xlsx,.xls,.parquet"
                  className="input"
                  required
                  disabled={isLoading}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Supported: CSV, JSON, Excel, Parquet
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dataset Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input"
                  placeholder="My Dataset"
                  required
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="input"
                  rows={2}
                  placeholder="Brief description..."
                  disabled={isLoading}
                />
              </div>

              {/* Context Source Selection */}
              <div className="pt-4 border-t border-gray-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Add Context (optional)
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Add documentation about your dataset - helps AI understand your data better.
                </p>

                {/* Context source tabs */}
                <div className="flex space-x-2 mb-3">
                  <button
                    type="button"
                    onClick={() => setContextSource('none')}
                    className={`px-3 py-1.5 text-xs rounded-lg ${
                      contextSource === 'none'
                        ? 'bg-gray-200 text-gray-800'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-150'
                    }`}
                    disabled={isLoading}
                  >
                    None
                  </button>
                  <button
                    type="button"
                    onClick={() => setContextSource('url')}
                    className={`px-3 py-1.5 text-xs rounded-lg flex items-center space-x-1 ${
                      contextSource === 'url'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-150'
                    }`}
                    disabled={isLoading}
                  >
                    <Link className="w-3 h-3" />
                    <span>From URL</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setContextSource('file')}
                    className={`px-3 py-1.5 text-xs rounded-lg flex items-center space-x-1 ${
                      contextSource === 'file'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-150'
                    }`}
                    disabled={isLoading}
                  >
                    <FileText className="w-3 h-3" />
                    <span>From File</span>
                  </button>
                </div>

                {/* URL input */}
                {contextSource === 'url' && (
                  <div>
                    <input
                      type="url"
                      value={contextUrl}
                      onChange={(e) => setContextUrl(e.target.value)}
                      placeholder="https://kaggle.com/datasets/... or documentation URL"
                      className="input"
                      disabled={isLoading}
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      Paste Kaggle dataset page, GitHub README, or any documentation URL
                    </p>
                  </div>
                )}

                {/* File input */}
                {contextSource === 'file' && (
                  <div>
                    <input
                      type="file"
                      onChange={(e) => setContextFile(e.target.files?.[0] || null)}
                      accept=".md,.yaml,.yml,.txt"
                      className="input"
                      disabled={isLoading}
                    />
                    {contextFile && (
                      <p className="text-xs text-green-600 mt-1 flex items-center">
                        <FileText className="w-3 h-3 mr-1" />
                        {contextFile.name}
                      </p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">Supported: Markdown, YAML, Text</p>
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading || !file}
                className="btn btn-primary w-full"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>{uploadStep || 'Uploading...'}</span>
                  </span>
                ) : (
                  <span>
                    Upload Dataset
                    {(contextSource === 'file' && contextFile) || (contextSource === 'url' && contextUrl.trim())
                      ? ' & Create Context'
                      : ''}
                  </span>
                )}
              </button>
            </form>
          )}
        </div>
      )}

      {/* Smart Import Form */}
      {mode === 'url' && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-2">Import from URL</h2>
          <p className="text-gray-600 mb-6">
            Paste any URL and we'll auto-detect if it's data (CSV, JSON, Excel) or documentation.
            Data files become datasets; documentation becomes searchable context you can chat with.
          </p>

          {/* Success State */}
          {success ? (
            <div className="text-center py-8">
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                {success.type === 'dataset' ? 'Dataset Imported!' : 'Context Created!'}
              </h3>
              <p className="text-gray-600 mb-6">"{success.name}" is ready.</p>
              <div className="space-x-3">
                <button
                  onClick={() => navigate(success.type === 'dataset' ? `/datasets/${success.id}` : `/contexts/${success.id}`)}
                  className="btn btn-primary"
                >
                  View {success.type === 'dataset' ? 'Dataset' : 'Context'}
                </button>
                <button
                  onClick={resetUrlForm}
                  className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
                >
                  Import Another
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => { setUrl(e.target.value); setAnalysisResult(null); }}
                  className="input"
                  placeholder="https://example.com/data.csv or documentation URL"
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name (optional)
                </label>
                <input
                  type="text"
                  value={urlName}
                  onChange={(e) => setUrlName(e.target.value)}
                  className="input"
                  placeholder="Auto-generated if empty"
                  disabled={isLoading}
                />
              </div>

              {/* Analyze Button - show when no result yet */}
              {!analysisResult && (
                <button
                  onClick={handleAnalyzeUrl}
                  disabled={isAnalyzing || !url.trim()}
                  className="btn bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 w-full"
                >
                  {isAnalyzing ? (
                    <span className="flex items-center justify-center space-x-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Analyzing...</span>
                    </span>
                  ) : (
                    <span className="flex items-center justify-center space-x-2">
                      <Sparkles className="w-4 h-4" />
                      <span>Analyze URL</span>
                    </span>
                  )}
                </button>
              )}

              {/* Analysis Result */}
              {analysisResult && (
                <div className="space-y-4">
                  <div className={`p-4 rounded-lg border ${
                    analysisResult.message.type === 'success' ? 'bg-green-50 border-green-200' :
                    analysisResult.message.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                    analysisResult.message.type === 'error' ? 'bg-red-50 border-red-200' :
                    'bg-blue-50 border-blue-200'
                  }`}>
                    <p className="font-medium text-gray-900">{analysisResult.message.title}</p>
                    <p className="text-sm text-gray-600 mt-1">{analysisResult.message.message}</p>
                  </div>

                  {/* Dataset Page Instructions */}
                  {analysisResult.url_type === 'dataset_page' && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm">
                      <p className="font-medium text-amber-800 mb-2">How to import the data:</p>
                      <ol className="text-amber-700 space-y-1 list-decimal list-inside">
                        <li>Go to the dataset page and click "Download"</li>
                        <li>Copy the direct download link (ends in .csv, .json, etc.)</li>
                        <li>Paste that link here instead</li>
                      </ol>
                      <p className="text-amber-600 mt-2 text-xs">Or create a context from the page description below.</p>
                    </div>
                  )}

                  <div className="flex space-x-3">
                    {analysisResult.can_import_data && analysisResult.url_type !== 'dataset_page' && (
                      <button
                        onClick={handleImportData}
                        disabled={isLoading || !urlName.trim()}
                        className="flex-1 btn bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-300"
                      >
                        {isLoading ? 'Importing...' : 'Import as Data'}
                      </button>
                    )}
                    {analysisResult.can_create_context && (
                      <button
                        onClick={handleCreateContext}
                        disabled={isLoading}
                        className="flex-1 btn bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300"
                      >
                        {isLoading ? 'Creating...' : analysisResult.url_type === 'dataset_page' ? 'Create Context from Description' : 'Create Context'}
                      </button>
                    )}
                  </div>

                  <button
                    onClick={resetUrlForm}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    Try a different URL
                  </button>
                </div>
              )}

              {/* Help text */}
              {!analysisResult && !isAnalyzing && (
                <div className="text-sm text-gray-500 pt-4 border-t space-y-1">
                  <p className="font-medium">Supported URL types:</p>
                  <p>• <strong>Data:</strong> CSV, JSON, Excel file URLs</p>
                  <p>• <strong>Documentation:</strong> GitHub, official docs, articles</p>
                  <p>• <strong>Dataset pages:</strong> Kaggle, Data.world</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
