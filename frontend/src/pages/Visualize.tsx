import { useEffect, useState } from 'react'
import { datasetAPI, visualizationAPI } from '../services/api'
import type { Dataset, VizSuggestion, ChartType } from '../types'
import Plot from 'react-plotly.js'
import { BarChart3, Sparkles } from 'lucide-react'

export default function Visualize() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [selectedDataset, setSelectedDataset] = useState<string>('')
  const [suggestions, setSuggestions] = useState<VizSuggestion[]>([])
  const [selectedSuggestion, setSelectedSuggestion] = useState<VizSuggestion | null>(null)
  const [chartData, setChartData] = useState<any>(null)
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

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

  const handleGetSuggestions = async () => {
    if (!selectedDataset) return

    setIsLoadingSuggestions(true)
    setSuggestions([])
    setSelectedSuggestion(null)
    setChartData(null)

    try {
      const data = await visualizationAPI.suggest(selectedDataset)
      setSuggestions(data)
    } catch (error: any) {
      console.error('Error getting suggestions:', error)
      alert(error.response?.data?.detail || 'Failed to get suggestions')
    } finally {
      setIsLoadingSuggestions(false)
    }
  }

  const handleGenerateChart = async (suggestion: VizSuggestion) => {
    if (!selectedDataset) return

    setSelectedSuggestion(suggestion)
    setIsGenerating(true)
    setChartData(null)

    try {
      const viz = await visualizationAPI.generate(
        selectedDataset,
        suggestion.chart_type,
        suggestion.config,
        suggestion.title
      )
      setChartData(viz.chart_data)
    } catch (error: any) {
      console.error('Error generating chart:', error)
      alert(error.response?.data?.detail || 'Failed to generate chart')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Visualize Data</h1>
        <p className="text-gray-600 mt-2">
          Get AI-powered chart suggestions or create custom visualizations
        </p>
      </div>

      <div className="card">
        <div className="space-y-4">
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

          <button
            onClick={handleGetSuggestions}
            disabled={isLoadingSuggestions || !selectedDataset}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Sparkles className="w-5 h-5" />
            <span>
              {isLoadingSuggestions ? 'Getting Suggestions...' : 'Get AI Suggestions'}
            </span>
          </button>
        </div>
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Suggested Visualizations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {suggestions.map((suggestion, idx) => (
              <div
                key={idx}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedSuggestion === suggestion
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-primary-300'
                }`}
                onClick={() => handleGenerateChart(suggestion)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5 text-primary-600" />
                    <h3 className="font-semibold text-gray-900">{suggestion.title}</h3>
                  </div>
                  <span className="text-sm text-gray-500">
                    {Math.round(suggestion.confidence * 100)}% match
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{suggestion.description}</p>
                <p className="text-xs text-gray-500">
                  <span className="font-medium">Chart Type:</span>{' '}
                  <span className="capitalize">{suggestion.chart_type}</span>
                </p>
                <p className="text-xs text-gray-500 mt-1">{suggestion.reasoning}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chart Display */}
      {isGenerating && (
        <div className="card">
          <div className="text-center py-12">
            <div className="text-gray-500">Generating chart...</div>
          </div>
        </div>
      )}

      {chartData && !isGenerating && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {selectedSuggestion?.title || 'Visualization'}
          </h2>
          <div className="flex justify-center">
            <Plot
              data={chartData.data}
              layout={{
                ...chartData.layout,
                autosize: true,
                width: undefined,
                height: 500,
              }}
              config={{ responsive: true }}
              style={{ width: '100%' }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
