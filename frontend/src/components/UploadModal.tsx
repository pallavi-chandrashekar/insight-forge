import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { datasetAPI, smartImportAPI } from '../services/api'
import contextService from '../services/contextService'
import { X, Upload, CheckCircle, AlertCircle, ExternalLink, FileText, Link } from 'lucide-react'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
}

type SuccessResult = {
  datasetId: string
  datasetName: string
  contextId?: string
  contextName?: string
}

type ContextSource = 'none' | 'file' | 'url'

export default function UploadModal({ isOpen, onClose }: UploadModalProps) {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [contextSource, setContextSource] = useState<ContextSource>('none')
  const [contextFile, setContextFile] = useState<File | null>(null)
  const [contextUrl, setContextUrl] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStep, setUploadStep] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<SuccessResult | null>(null)

  if (!isOpen) return null

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }
    if (!name.trim()) {
      setError('Please enter a dataset name')
      return
    }

    setIsUploading(true)
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

      setSuccess({
        datasetId: dataset.id,
        datasetName: name,
        ...contextResult
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file')
    } finally {
      setIsUploading(false)
      setUploadStep('')
    }
  }

  const handleClose = () => {
    setFile(null)
    setName('')
    setDescription('')
    setContextSource('none')
    setContextFile(null)
    setContextUrl('')
    setError(null)
    setSuccess(null)
    onClose()
  }

  const handleViewDataset = () => {
    if (success) {
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

  const handleUploadAnother = () => {
    setFile(null)
    setName('')
    setDescription('')
    setContextSource('none')
    setContextFile(null)
    setContextUrl('')
    setError(null)
    setSuccess(null)
  }

  // Success State
  if (success) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Upload Complete!
            </h2>
            <div className="text-gray-600 mb-6 space-y-1">
              <p>Dataset "{success.datasetName}" uploaded successfully.</p>
              {success.contextId && (
                <p className="text-sm text-green-600">Context "{success.contextName}" created.</p>
              )}
            </div>

            <div className="space-y-3">
              <button
                onClick={handleViewDataset}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2"
              >
                <span>View Dataset</span>
                <ExternalLink className="w-4 h-4" />
              </button>
              {success.contextId && (
                <button
                  onClick={handleViewContext}
                  className="w-full border border-blue-300 text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-50 flex items-center justify-center space-x-2"
                >
                  <span>View Context</span>
                  <FileText className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={handleUploadAnother}
                className="w-full border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50"
              >
                Upload Another
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
              <Upload className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Upload Dataset</h2>
              <p className="text-sm text-gray-500">Upload from your computer</p>
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
          {/* File Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Select File</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              accept=".csv,.json,.xlsx,.xls,.parquet"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              disabled={isUploading}
            />
            <p className="text-xs text-gray-500 mt-1">Supported: CSV, JSON, Excel, Parquet</p>
          </div>

          {/* Name Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Dataset Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My Dataset"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              disabled={isUploading}
            />
          </div>

          {/* Description Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description (optional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description..."
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              disabled={isUploading}
            />
          </div>

          {/* Context Source Selection */}
          <div className="pt-3 border-t border-gray-200">
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
                disabled={isUploading}
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
                disabled={isUploading}
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
                disabled={isUploading}
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  disabled={isUploading}
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  disabled={isUploading}
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

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={isUploading || !file || !name.trim()}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isUploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>{uploadStep || 'Uploading...'}</span>
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                <span>
                  Upload Dataset
                  {(contextSource === 'file' && contextFile) || (contextSource === 'url' && contextUrl.trim())
                    ? ' & Create Context'
                    : ''}
                </span>
              </>
            )}
          </button>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
