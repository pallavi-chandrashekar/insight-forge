import { useState, useEffect } from 'react'
import { authAPI } from '../services/api'
import type { LLMSettings, LLMProvider, KaggleCredentials, LLMStatus } from '../types'

export default function Settings() {
  const [llmSettings, setLLMSettings] = useState<LLMSettings | null>(null)
  const [llmStatus, setLLMStatus] = useState<LLMStatus | null>(null)
  const [providers, setProviders] = useState<LLMProvider[]>([])
  const [kaggleCredentials, setKaggleCredentials] = useState<KaggleCredentials | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Form state
  const [selectedProvider, setSelectedProvider] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [kaggleUsername, setKaggleUsername] = useState('')
  const [kaggleKey, setKaggleKey] = useState('')

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const [llm, providerList, kaggle, status] = await Promise.all([
        authAPI.getLLMSettings(),
        authAPI.getLLMProviders(),
        authAPI.getKaggleCredentials(),
        authAPI.getLLMStatus(),
      ])
      setLLMSettings(llm)
      setProviders(providerList)
      setKaggleCredentials(kaggle)
      setLLMStatus(status)
      if (llm.provider) {
        setSelectedProvider(llm.provider)
      }
      if (kaggle.kaggle_username) {
        setKaggleUsername(kaggle.kaggle_username)
      }
    } catch (err) {
      setError('Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveLLM = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedProvider || !apiKey) {
      setError('Please select a provider and enter your API key')
      return
    }

    try {
      setSaving(true)
      setError(null)
      await authAPI.saveLLMSettings(selectedProvider, apiKey)
      setSuccess('LLM settings saved successfully!')
      setApiKey('')
      await loadSettings()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save LLM settings')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteLLM = async () => {
    if (!confirm('Are you sure you want to remove your LLM settings?')) return

    try {
      setSaving(true)
      await authAPI.deleteLLMSettings()
      setSuccess('LLM settings removed')
      setSelectedProvider('')
      await loadSettings()
    } catch (err) {
      setError('Failed to remove LLM settings')
    } finally {
      setSaving(false)
    }
  }

  const handleSaveKaggle = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!kaggleUsername || !kaggleKey) {
      setError('Please enter both Kaggle username and API key')
      return
    }

    try {
      setSaving(true)
      setError(null)
      await authAPI.saveKaggleCredentials(kaggleUsername, kaggleKey)
      setSuccess('Kaggle credentials saved successfully!')
      setKaggleKey('')
      await loadSettings()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save Kaggle credentials')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteKaggle = async () => {
    if (!confirm('Are you sure you want to remove your Kaggle credentials?')) return

    try {
      setSaving(true)
      await authAPI.deleteKaggleCredentials()
      setSuccess('Kaggle credentials removed')
      setKaggleUsername('')
      await loadSettings()
    } catch (err) {
      setError('Failed to remove Kaggle credentials')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
          <button onClick={() => setError(null)} className="ml-2 text-red-500 hover:text-red-700">
            &times;
          </button>
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          {success}
          <button onClick={() => setSuccess(null)} className="ml-2 text-green-500 hover:text-green-700">
            &times;
          </button>
        </div>
      )}

      {/* LLM Settings */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">AI Provider Settings</h2>
        <p className="text-gray-600 mb-4">
          Configure your AI provider to enable natural language queries, visualization suggestions, and chat features.
          Your API key is encrypted and stored securely.
        </p>

        {/* Show current status */}
        {llmStatus?.using_free_tier && !llmSettings?.is_configured && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <span className="text-blue-700 font-medium">Using free tier </span>
                <span className="text-blue-600">(limited requests). Add your own API key for better performance.</span>
              </div>
            </div>
          </div>
        )}

        {!llmStatus?.is_available && (
          <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-yellow-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <span className="text-yellow-700 font-medium">AI features disabled. </span>
                <span className="text-yellow-600">Add your API key below to enable natural language queries and AI suggestions.</span>
              </div>
            </div>
          </div>
        )}

        {llmSettings?.is_configured && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-green-700 font-medium">Currently configured: </span>
                <span className="text-green-800 font-semibold capitalize">{llmSettings.provider}</span>
              </div>
              <button
                onClick={handleDeleteLLM}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                Remove
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSaveLLM} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select AI Provider
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {providers.map((provider) => (
                <div
                  key={provider.id}
                  onClick={() => setSelectedProvider(provider.id)}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedProvider === provider.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <h3 className="font-medium">{provider.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{provider.description}</p>
                  <a
                    href={provider.signup_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:text-blue-800 mt-2 inline-block"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Get API Key &rarr;
                  </a>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
              API Key
            </label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={llmSettings?.is_configured ? '••••••••••••••••' : 'Enter your API key'}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Your API key is encrypted before storage and never shared.
            </p>
          </div>

          <button
            type="submit"
            disabled={saving || !selectedProvider || !apiKey}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : llmSettings?.is_configured ? 'Update Settings' : 'Save Settings'}
          </button>
        </form>
      </div>

      {/* Kaggle Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Kaggle Integration</h2>
        <p className="text-gray-600 mb-4">
          Configure your Kaggle credentials to import datasets directly from Kaggle.
          Get your API credentials from your{' '}
          <a
            href="https://www.kaggle.com/settings/account"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800"
          >
            Kaggle Account Settings
          </a>.
        </p>

        {kaggleCredentials?.has_credentials && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-green-700 font-medium">Kaggle connected: </span>
                <span className="text-green-800 font-semibold">{kaggleCredentials.kaggle_username}</span>
              </div>
              <button
                onClick={handleDeleteKaggle}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                Remove
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSaveKaggle} className="space-y-4">
          <div>
            <label htmlFor="kaggleUsername" className="block text-sm font-medium text-gray-700 mb-1">
              Kaggle Username
            </label>
            <input
              type="text"
              id="kaggleUsername"
              value={kaggleUsername}
              onChange={(e) => setKaggleUsername(e.target.value)}
              placeholder="your_kaggle_username"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="kaggleKey" className="block text-sm font-medium text-gray-700 mb-1">
              Kaggle API Key
            </label>
            <input
              type="password"
              id="kaggleKey"
              value={kaggleKey}
              onChange={(e) => setKaggleKey(e.target.value)}
              placeholder={kaggleCredentials?.has_credentials ? '••••••••••••••••' : 'Enter your Kaggle API key'}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            disabled={saving || !kaggleUsername || !kaggleKey}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : kaggleCredentials?.has_credentials ? 'Update Credentials' : 'Save Credentials'}
          </button>
        </form>
      </div>
    </div>
  )
}
