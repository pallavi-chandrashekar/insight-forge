import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { datasetAPI } from '../services/api'
import { Upload as UploadIcon, Link as LinkIcon, Globe } from 'lucide-react'

type UploadMode = 'file' | 'url' | 'scrape'

export default function Upload() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<UploadMode>('file')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // File upload state
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  // URL import state
  const [url, setUrl] = useState('')

  // Scrape state
  const [scrapeUrl, setScrapeUrl] = useState('')
  const [selector, setSelector] = useState('')

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setIsLoading(true)
    setError(null)

    try {
      const dataset = await datasetAPI.upload(file, name, description)
      navigate(`/datasets/${dataset.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleUrlImport = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const dataset = await datasetAPI.importFromUrl(name, url, description)
      navigate(`/datasets/${dataset.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'URL import failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const dataset = await datasetAPI.scrapeWebpage(
        name,
        scrapeUrl,
        selector || undefined,
        description
      )
      navigate(`/datasets/${dataset.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Web scraping failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Upload Data</h1>

      {/* Mode selector */}
      <div className="flex space-x-4 mb-8">
        <button
          onClick={() => setMode('file')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
            mode === 'file'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <UploadIcon className="w-5 h-5" />
          <span>Upload File</span>
        </button>
        <button
          onClick={() => setMode('url')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
            mode === 'url'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <LinkIcon className="w-5 h-5" />
          <span>Import from URL</span>
        </button>
        <button
          onClick={() => setMode('scrape')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
            mode === 'scrape'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <Globe className="w-5 h-5" />
          <span>Scrape Webpage</span>
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* File Upload Form */}
      {mode === 'file' && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Upload File</h2>
          <form onSubmit={handleFileUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                File
              </label>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                accept=".csv,.json,.xlsx,.xls,.parquet"
                className="input"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Supported formats: CSV, JSON, Excel, Parquet
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
                rows={3}
                placeholder="Brief description of this dataset..."
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !file}
              className="btn btn-primary"
            >
              {isLoading ? 'Uploading...' : 'Upload Dataset'}
            </button>
          </form>
        </div>
      )}

      {/* URL Import Form */}
      {mode === 'url' && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Import from URL</h2>
          <form onSubmit={handleUrlImport} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="input"
                placeholder="https://example.com/data.csv"
                required
              />
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
                rows={3}
                placeholder="Brief description of this dataset..."
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary"
            >
              {isLoading ? 'Importing...' : 'Import Dataset'}
            </button>
          </form>
        </div>
      )}

      {/* Scrape Form */}
      {mode === 'scrape' && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Scrape Webpage</h2>
          <form onSubmit={handleScrape} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Webpage URL
              </label>
              <input
                type="url"
                value={scrapeUrl}
                onChange={(e) => setScrapeUrl(e.target.value)}
                className="input"
                placeholder="https://example.com/page-with-table"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CSS Selector (optional)
              </label>
              <input
                type="text"
                value={selector}
                onChange={(e) => setSelector(e.target.value)}
                className="input"
                placeholder="#data-table or .table"
              />
              <p className="text-sm text-gray-500 mt-1">
                Leave empty to scrape the first table found
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
                rows={3}
                placeholder="Brief description of this dataset..."
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary"
            >
              {isLoading ? 'Scraping...' : 'Scrape and Import'}
            </button>
          </form>
        </div>
      )}
    </div>
  )
}
