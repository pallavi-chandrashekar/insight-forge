import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { smartImportAPI, authAPI } from '../services/api'
import type { SmartImportResponse, KaggleCredentials } from '../types'
import { X, Sparkles, FileText, Database, AlertCircle, CheckCircle, Info, AlertTriangle, Loader2, ExternalLink, Key, Save } from 'lucide-react'

interface SmartImportModalProps {
  isOpen: boolean
  onClose: () => void
}

type SuccessResult = {
  type: 'dataset' | 'context' | 'both'
  datasetId?: string
  datasetName?: string
  contextId?: string
  contextName?: string
  credentialsSaved?: boolean
}

export default function SmartImportModal({ isOpen, onClose }: SmartImportModalProps) {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')
  const [datasetName, setDatasetName] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SmartImportResponse | null>(null)
  const [success, setSuccess] = useState<SuccessResult | null>(null)

  // Kaggle credentials
  const [kaggleUsername, setKaggleUsername] = useState('')
  const [kaggleKey, setKaggleKey] = useState('')
  const [storedCredentials, setStoredCredentials] = useState<KaggleCredentials | null>(null)
  const [useStoredCredentials, setUseStoredCredentials] = useState(true)
  const [saveCredentials, setSaveCredentials] = useState(false)
  const [isLoadingCredentials, setIsLoadingCredentials] = useState(false)

  // Check for stored Kaggle credentials when modal opens
  useEffect(() => {
    if (isOpen) {
      checkStoredCredentials()
    }
  }, [isOpen])

  const checkStoredCredentials = async () => {
    setIsLoadingCredentials(true)
    try {
      const creds = await authAPI.getKaggleCredentials()
      setStoredCredentials(creds)
      if (creds.has_credentials && creds.kaggle_username) {
        setUseStoredCredentials(true)
      }
    } catch {
      // Ignore errors - just means no stored credentials
      setStoredCredentials(null)
    } finally {
      setIsLoadingCredentials(false)
    }
  }

  if (!isOpen) return null

  const isKaggleUrl = url.toLowerCase().includes('kaggle.com')
  const hasStoredKaggleCreds = storedCredentials?.has_credentials ?? false

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    setIsAnalyzing(true)
    setError(null)
    setResult(null)

    try {
      const response = await smartImportAPI.analyzeUrl(url, datasetName || undefined)
      setResult(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze URL')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleImportData = async () => {
    if (!url.trim() || !datasetName.trim()) {
      setError('Please enter both URL and dataset name')
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const { datasetAPI } = await import('../services/api')
      const dataset = await datasetAPI.importFromUrl(datasetName, url)
      setSuccess({
        type: 'dataset',
        datasetId: dataset.id,
        datasetName: datasetName
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import data')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleKaggleImport = async () => {
    if (!url.trim() || !datasetName.trim()) {
      setError('Please enter both URL and dataset name')
      return
    }

    // Determine which credentials to use
    const usingStored = useStoredCredentials && hasStoredKaggleCreds
    const username = usingStored ? undefined : kaggleUsername
    const key = usingStored ? undefined : kaggleKey

    // Validate credentials if not using stored
    if (!usingStored && (!kaggleUsername.trim() || !kaggleKey.trim())) {
      setError('Please enter your Kaggle credentials')
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const response = await smartImportAPI.importFromKaggle(
        url,
        datasetName,
        {
          kaggle_username: username,
          kaggle_key: key,
          create_context: true,
          save_credentials: !usingStored && saveCredentials,
        }
      )

      setSuccess({
        type: response.context_id ? 'both' : 'dataset',
        datasetId: response.dataset_id,
        datasetName: response.dataset_name,
        contextId: response.context_id,
        contextName: response.context_name,
        credentialsSaved: response.credentials_saved,
      })

      // Refresh stored credentials if we saved new ones
      if (response.credentials_saved) {
        checkStoredCredentials()
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to import from Kaggle')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleCreateContext = async () => {
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    setIsProcessing(true)
    setError(null)

    try {
      const response = await smartImportAPI.createContextFromUrl(url, datasetName || undefined)
      setSuccess({
        type: 'context',
        contextId: response.context_id,
        contextName: response.context_name || datasetName || 'New Context'
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create context')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleClose = () => {
    setUrl('')
    setDatasetName('')
    setResult(null)
    setError(null)
    setSuccess(null)
    setKaggleUsername('')
    setKaggleKey('')
    setSaveCredentials(false)
    onClose()
  }

  const handleViewDataset = () => {
    if (success?.datasetId) {
      handleClose()
      navigate(`/datasets/${success.datasetId}`)
    }
  }

  const handleViewContext = () => {
    if (success?.contextId) {
      handleClose()
      navigate(`/contexts/${success.contextId}`)
    }
  }

  const handleImportAnother = () => {
    setUrl('')
    setDatasetName('')
    setResult(null)
    setError(null)
    setSuccess(null)
    setKaggleUsername('')
    setKaggleKey('')
    setSaveCredentials(false)
  }

  // Success State
  if (success) {
    const getSuccessTitle = () => {
      if (success.type === 'both') return 'Import Complete!'
      if (success.type === 'dataset') return 'Dataset Imported!'
      return 'Context Created!'
    }

    const getSuccessMessage = () => {
      if (success.type === 'both') {
        return `Dataset "${success.datasetName}" and context "${success.contextName}" have been created successfully.`
      }
      if (success.type === 'dataset') {
        return `"${success.datasetName}" has been successfully imported.`
      }
      return `"${success.contextName}" has been successfully created.`
    }

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              {getSuccessTitle()}
            </h2>
            <p className="text-gray-600 mb-4">
              {getSuccessMessage()}
            </p>

            {success.credentialsSaved && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 mb-4 text-sm text-blue-700">
                <Save className="w-4 h-4 inline mr-1" />
                Kaggle credentials saved for future imports
              </div>
            )}

            <div className="space-y-3">
              {/* Show both buttons when both dataset and context created */}
              {success.type === 'both' && (
                <>
                  <button
                    onClick={handleViewDataset}
                    className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center justify-center space-x-2"
                  >
                    <Database className="w-4 h-4" />
                    <span>View Dataset</span>
                  </button>
                  <button
                    onClick={handleViewContext}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2"
                  >
                    <FileText className="w-4 h-4" />
                    <span>View Context</span>
                  </button>
                </>
              )}

              {/* Single button for dataset only */}
              {success.type === 'dataset' && (
                <button
                  onClick={handleViewDataset}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2"
                >
                  <span>View Dataset</span>
                  <ExternalLink className="w-4 h-4" />
                </button>
              )}

              {/* Single button for context only */}
              {success.type === 'context' && (
                <button
                  onClick={handleViewContext}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2"
                >
                  <span>View Context</span>
                  <ExternalLink className="w-4 h-4" />
                </button>
              )}

              <button
                onClick={handleImportAnother}
                className="w-full border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
              >
                Import Another
              </button>
              <button
                onClick={handleClose}
                className="w-full text-gray-500 hover:text-gray-700"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Sparkles className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Smart Import</h2>
              <p className="text-sm text-gray-500">Paste any URL</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-4">
          {/* URL Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              disabled={isAnalyzing || isProcessing}
            />
          </div>

          {/* Name Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name {isKaggleUrl && result?.url_type === 'dataset_page' ? '(required for Kaggle)' : '(optional)'}
            </label>
            <input
              type="text"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder={isKaggleUrl ? "Enter dataset name" : "Auto-generated if empty"}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              disabled={isAnalyzing || isProcessing}
            />
          </div>

          {/* Analyze Button */}
          {!result && (
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !url.trim()}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Analyze URL</span>
                </>
              )}
            </button>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="space-y-3">
              {/* Message */}
              <div className={`border rounded-lg p-3 ${
                result.message.type === 'success' ? 'bg-green-50 border-green-200' :
                result.message.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                result.message.type === 'error' ? 'bg-red-50 border-red-200' :
                'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex items-start space-x-2">
                  {result.message.type === 'success' && <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />}
                  {result.message.type === 'warning' && <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />}
                  {result.message.type === 'error' && <AlertCircle className="w-4 h-4 text-red-500 mt-0.5" />}
                  {result.message.type === 'info' && <Info className="w-4 h-4 text-blue-500 mt-0.5" />}
                  <div>
                    <p className="text-sm font-medium text-gray-900">{result.message.title}</p>
                    <p className="text-sm text-gray-600 mt-1">{result.message.message}</p>
                  </div>
                </div>
              </div>

              {/* Kaggle Import with API */}
              {result.url_type === 'dataset_page' && isKaggleUrl && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <Key className="w-4 h-4 text-blue-600" />
                    <p className="font-medium text-blue-800">Import directly from Kaggle</p>
                  </div>

                  {/* Stored Credentials Option */}
                  {isLoadingCredentials ? (
                    <div className="flex items-center space-x-2 text-sm text-gray-500 mb-3">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Checking saved credentials...</span>
                    </div>
                  ) : hasStoredKaggleCreds ? (
                    <div className="mb-3">
                      <div className="flex items-center space-x-2 mb-2">
                        <input
                          type="checkbox"
                          id="useStoredCreds"
                          checked={useStoredCredentials}
                          onChange={(e) => setUseStoredCredentials(e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="useStoredCreds" className="text-sm text-gray-700">
                          Use saved credentials ({storedCredentials?.kaggle_username})
                        </label>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-blue-700 mb-3">
                      Enter your Kaggle API credentials to download the dataset automatically.
                    </p>
                  )}

                  {/* Credential Inputs - only show if not using stored */}
                  {(!hasStoredKaggleCreds || !useStoredCredentials) && (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Kaggle Username</label>
                        <input
                          type="text"
                          value={kaggleUsername}
                          onChange={(e) => setKaggleUsername(e.target.value)}
                          placeholder="your_username"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                          disabled={isProcessing}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Kaggle API Key</label>
                        <input
                          type="password"
                          value={kaggleKey}
                          onChange={(e) => setKaggleKey(e.target.value)}
                          placeholder="Your API key"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                          disabled={isProcessing}
                        />
                      </div>

                      {/* Save Credentials Checkbox */}
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="saveCredentials"
                          checked={saveCredentials}
                          onChange={(e) => setSaveCredentials(e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="saveCredentials" className="text-sm text-gray-700">
                          Save credentials for future imports
                        </label>
                      </div>

                      <p className="text-xs text-gray-500">
                        Get your API key from <a href="https://www.kaggle.com/settings" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Kaggle Settings → API</a>
                      </p>
                    </div>
                  )}

                  <button
                    onClick={handleKaggleImport}
                    disabled={
                      isProcessing ||
                      !datasetName.trim() ||
                      (!hasStoredKaggleCreds && (!kaggleUsername.trim() || !kaggleKey.trim())) ||
                      (hasStoredKaggleCreds && !useStoredCredentials && (!kaggleUsername.trim() || !kaggleKey.trim()))
                    }
                    className="w-full mt-3 bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 flex items-center justify-center space-x-2 text-sm"
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Importing from Kaggle...</span>
                      </>
                    ) : (
                      <>
                        <Database className="w-4 h-4" />
                        <span>Import Dataset + Context</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Dataset Page Instructions (non-Kaggle) */}
              {result.url_type === 'dataset_page' && !isKaggleUrl && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm">
                  <p className="font-medium text-amber-800 mb-2">How to import the data:</p>
                  <ol className="text-amber-700 space-y-1 list-decimal list-inside">
                    <li>Go to the dataset page and click "Download"</li>
                    <li>Copy the direct download link (ends in .csv, .json, etc.)</li>
                    <li>Paste that link here instead</li>
                  </ol>
                  <p className="text-amber-600 mt-2 text-xs">Or create a context from the page description below.</p>
                </div>
              )}

              {/* Action Buttons - Hide for Kaggle since we have dedicated form */}
              {!(result.url_type === 'dataset_page' && isKaggleUrl) && (
                <div className="flex space-x-2">
                  {result.can_import_data && result.url_type !== 'dataset_page' && (
                    <button
                      onClick={handleImportData}
                      disabled={isProcessing || !datasetName.trim()}
                      className="flex-1 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-300 flex items-center justify-center space-x-1 text-sm"
                    >
                      {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Database className="w-4 h-4" />}
                      <span>Import Data</span>
                    </button>
                  )}

                  {result.can_create_context && (
                    <button
                      onClick={handleCreateContext}
                      disabled={isProcessing}
                      className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 flex items-center justify-center space-x-1 text-sm"
                    >
                      {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                      <span>{result.url_type === 'dataset_page' ? 'Create Context from Description' : 'Create Context'}</span>
                    </button>
                  )}
                </div>
              )}

              <button
                onClick={() => setResult(null)}
                disabled={isProcessing}
                className="w-full text-sm text-gray-500 hover:text-gray-700"
              >
                Try another URL
              </button>
            </div>
          )}

          {/* Help - only show initially */}
          {!result && !isAnalyzing && (
            <div className="text-xs text-gray-500 space-y-1 pt-2 border-t">
              <p><strong>Supported:</strong></p>
              <p>• Data files: CSV, JSON, Excel URLs</p>
              <p>• Documentation: GitHub, official docs, articles</p>
              <p>• Kaggle: Direct import with API credentials</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
