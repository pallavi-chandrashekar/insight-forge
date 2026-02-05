import { useEffect, useState } from 'react'
import { datasetAPI, visualizationAPI } from '../services/api'
import type { Dataset, VizSuggestion, ChartType } from '../types'
import Plot from 'react-plotly.js'
import {
  BarChart3, Sparkles, Wand2, LineChart, ScatterChart,
  PieChart, BarChart, TrendingUp, Grid, Box, Activity,
  Download, Save, Trash2, Eye, MessageSquare
} from 'lucide-react'

export default function Visualize() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [selectedDataset, setSelectedDataset] = useState<string>('')
  const [suggestions, setSuggestions] = useState<VizSuggestion[]>([])
  const [selectedSuggestion, setSelectedSuggestion] = useState<VizSuggestion | null>(null)
  const [chartData, setChartData] = useState<any>(null)
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [mode, setMode] = useState<'ai' | 'manual' | 'nl'>('manual')

  // Manual chart creation state
  const [chartType, setChartType] = useState<ChartType>('bar')
  const [chartConfig, setChartConfig] = useState<any>({
    x_column: '',
    y_column: '',
    aggregation: 'sum',
    title: ''
  })
  const [datasetColumns, setDatasetColumns] = useState<string[]>([])
  const [savedChartId, setSavedChartId] = useState<string | null>(null)

  // Natural language visualization state
  const [nlDescription, setNlDescription] = useState('')
  const [nlParsedIntent, setNlParsedIntent] = useState<any>(null)

  // Chart type metadata
  const chartTypes = [
    { type: 'bar', icon: BarChart3, label: 'Bar Chart', description: 'Compare values across categories' },
    { type: 'line', icon: LineChart, label: 'Line Chart', description: 'Show trends over time' },
    { type: 'scatter', icon: ScatterChart, label: 'Scatter Plot', description: 'Explore relationships' },
    { type: 'pie', icon: PieChart, label: 'Pie Chart', description: 'Show proportions' },
    { type: 'histogram', icon: BarChart, label: 'Histogram', description: 'Show distributions' },
    { type: 'heatmap', icon: Grid, label: 'Heatmap', description: 'Show patterns in 2D' },
    { type: 'box', icon: Box, label: 'Box Plot', description: 'Show statistical spread' },
    { type: 'area', icon: Activity, label: 'Area Chart', description: 'Show cumulative trends' },
    { type: 'table', icon: Grid, label: 'Table', description: 'Display raw data' },
  ]

  useEffect(() => {
    loadDatasets()
  }, [])

  const loadDatasets = async () => {
    try {
      const data = await datasetAPI.list()
      setDatasets(data)
      if (data.length > 0) {
        setSelectedDataset(data[0].id)
        loadDatasetColumns(data[0].id)
      }
    } catch (error) {
      console.error('Error loading datasets:', error)
    }
  }

  const loadDatasetColumns = async (datasetId: string) => {
    try {
      const preview = await datasetAPI.preview(datasetId)
      setDatasetColumns(preview.columns || [])
    } catch (error) {
      console.error('Error loading dataset columns:', error)
    }
  }

  const handleDatasetChange = (datasetId: string) => {
    setSelectedDataset(datasetId)
    loadDatasetColumns(datasetId)
    setChartData(null)
    setSuggestions([])
    setNlDescription('')
    setNlParsedIntent(null)
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

  const handleManualGenerate = async () => {
    if (!selectedDataset) return

    setIsGenerating(true)
    setChartData(null)
    setSavedChartId(null)

    try {
      const viz = await visualizationAPI.generate(
        selectedDataset,
        chartType,
        chartConfig,
        chartConfig.title || `${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart`
      )
      setChartData(viz.chart_data)
      setSavedChartId(viz.id)
    } catch (error: any) {
      console.error('Error generating chart:', error)
      alert(error.response?.data?.detail || 'Failed to generate chart')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownloadChart = () => {
    if (!chartData) return

    // Trigger Plotly's download
    const plotDiv = document.querySelector('.js-plotly-plot') as any
    if (plotDiv && plotDiv.downloadImage) {
      plotDiv.downloadImage({
        format: 'png',
        width: 1200,
        height: 800,
        filename: chartConfig.title || 'chart'
      })
    }
  }

  const handleDeleteChart = async () => {
    if (!savedChartId) return

    if (!confirm('Are you sure you want to delete this visualization?')) return

    try {
      await visualizationAPI.delete(savedChartId)
      setChartData(null)
      setSavedChartId(null)
      alert('Visualization deleted successfully')
    } catch (error: any) {
      console.error('Error deleting chart:', error)
      alert('Failed to delete visualization')
    }
  }

  const handleNLGenerate = async () => {
    if (!selectedDataset || !nlDescription.trim()) return

    setIsGenerating(true)
    setChartData(null)
    setSavedChartId(null)
    setNlParsedIntent(null)

    try {
      const response = await visualizationAPI.fromNaturalLanguage(
        selectedDataset,
        nlDescription
      )

      setChartData(response.visualization.chart_data)
      setSavedChartId(response.visualization.id)
      setNlParsedIntent(response.parsed_intent)

    } catch (error: any) {
      console.error('Error generating from NL:', error)

      const errorDetail = error.response?.data?.detail

      if (typeof errorDetail === 'object' && errorDetail.suggestions) {
        alert(`${errorDetail.error}\n\nSuggestions:\n${errorDetail.suggestions.join('\n')}`)
      } else {
        alert(errorDetail || 'Failed to generate visualization')
      }
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

      {/* Mode Toggle */}
      <div className="card">
        <div className="flex space-x-2 mb-6 border-b border-gray-200">
          <button
            onClick={() => setMode('manual')}
            className={`pb-2 px-4 font-medium transition-colors ${
              mode === 'manual'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Wand2 className="w-4 h-4" />
              <span>Manual Creation</span>
            </div>
          </button>
          <button
            onClick={() => setMode('ai')}
            className={`pb-2 px-4 font-medium transition-colors ${
              mode === 'ai'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4" />
              <span>AI Suggestions</span>
            </div>
          </button>
          <button
            onClick={() => setMode('nl')}
            className={`pb-2 px-4 font-medium transition-colors ${
              mode === 'nl'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4" />
              <span>Natural Language</span>
            </div>
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Select Dataset
            </label>
            <select
              value={selectedDataset}
              onChange={(e) => handleDatasetChange(e.target.value)}
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

          {mode === 'ai' && (
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
          )}

          {mode === 'manual' && (
            <div className="space-y-6">
              {/* Chart Type Selection */}
              <div>
                <label className="block text-lg font-semibold text-gray-900 mb-3">
                  Select Chart Type
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {chartTypes.map((ct) => (
                    <button
                      key={ct.type}
                      onClick={() => setChartType(ct.type as ChartType)}
                      className={`p-4 rounded-lg border-2 transition-all text-left ${
                        chartType === ct.type
                          ? 'border-primary-500 bg-primary-50 shadow-md'
                          : 'border-gray-200 hover:border-primary-300 hover:shadow-sm'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <ct.icon className={`w-6 h-6 mt-0.5 ${
                          chartType === ct.type ? 'text-primary-600' : 'text-gray-400'
                        }`} />
                        <div className="flex-1">
                          <div className={`font-semibold ${
                            chartType === ct.type ? 'text-primary-900' : 'text-gray-900'
                          }`}>
                            {ct.label}
                          </div>
                          <div className="text-xs text-gray-500 mt-0.5">
                            {ct.description}
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Chart Configuration */}
              <div className="bg-gray-50 rounded-lg p-5">
                <h3 className="font-semibold text-gray-900 mb-4">Configure Chart</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      X-Axis Column *
                    </label>
                    <select
                      value={chartConfig.x_column}
                      onChange={(e) => setChartConfig({ ...chartConfig, x_column: e.target.value })}
                      className="input bg-white"
                      required
                    >
                      <option value="">Select column...</option>
                      {datasetColumns.map((col) => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>

                  {chartType !== 'histogram' && chartType !== 'table' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Y-Axis Column {chartType !== 'pie' && '*'}
                      </label>
                      <select
                        value={chartConfig.y_column}
                        onChange={(e) => setChartConfig({ ...chartConfig, y_column: e.target.value })}
                        className="input bg-white"
                        required={chartType !== 'pie'}
                      >
                        <option value="">Select column...</option>
                        {datasetColumns.map((col) => (
                          <option key={col} value={col}>{col}</option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  {['bar', 'line', 'pie', 'area'].includes(chartType) && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Aggregation Function
                      </label>
                      <select
                        value={chartConfig.aggregation}
                        onChange={(e) => setChartConfig({ ...chartConfig, aggregation: e.target.value })}
                        className="input bg-white"
                      >
                        <option value="sum">Sum (total)</option>
                        <option value="mean">Mean (average)</option>
                        <option value="count">Count</option>
                        <option value="min">Minimum</option>
                        <option value="max">Maximum</option>
                      </select>
                    </div>
                  )}

                  {chartType === 'scatter' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Color By (Optional)
                      </label>
                      <select
                        value={chartConfig.color_column || ''}
                        onChange={(e) => setChartConfig({ ...chartConfig, color_column: e.target.value })}
                        className="input bg-white"
                      >
                        <option value="">None</option>
                        {datasetColumns.map((col) => (
                          <option key={col} value={col}>{col}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Chart Title
                    </label>
                    <input
                      type="text"
                      value={chartConfig.title}
                      onChange={(e) => setChartConfig({ ...chartConfig, title: e.target.value })}
                      placeholder={`My ${chartType} chart`}
                      className="input bg-white"
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-gray-600">
                  {!chartConfig.x_column && '← Select columns to get started'}
                  {chartConfig.x_column && !chartConfig.y_column && chartType !== 'histogram' && chartType !== 'table' && '← Select Y-axis column'}
                </div>
                <button
                  onClick={handleManualGenerate}
                  disabled={isGenerating || !selectedDataset || !chartConfig.x_column || (chartType !== 'histogram' && chartType !== 'table' && !chartConfig.y_column)}
                  className="btn btn-primary flex items-center space-x-2 px-6 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-shadow disabled:shadow-none"
                >
                  <BarChart3 className="w-6 h-6" />
                  <span>
                    {isGenerating ? 'Generating Chart...' : 'Generate Visualization'}
                  </span>
                </button>
              </div>
            </div>
          )}

          {mode === 'nl' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe what you want to visualize
                </label>
                <textarea
                  value={nlDescription}
                  onChange={(e) => setNlDescription(e.target.value)}
                  placeholder="E.g., show average screen time by age group, create pie chart of device types, compare social media hours across age groups"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 min-h-[100px] focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  rows={3}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Be specific about columns and chart type for best results
                </p>
              </div>

              {nlParsedIntent && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <h4 className="font-semibold text-blue-900 mb-1">Understanding:</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Chart: {nlParsedIntent.chart_type}</li>
                    <li>• X-axis: {nlParsedIntent.config.x_column}</li>
                    {nlParsedIntent.config.y_column && (
                      <li>• Y-axis: {Array.isArray(nlParsedIntent.config.y_column) ? nlParsedIntent.config.y_column.join(', ') : nlParsedIntent.config.y_column}</li>
                    )}
                    {nlParsedIntent.config.aggregation && (
                      <li>• Calculation: {nlParsedIntent.config.aggregation}</li>
                    )}
                  </ul>
                  <p className="text-xs text-gray-600 mt-2 italic">
                    {nlParsedIntent.reasoning}
                  </p>
                </div>
              )}

              <button
                onClick={handleNLGenerate}
                disabled={isGenerating || !selectedDataset || !nlDescription.trim()}
                className="btn btn-primary flex items-center space-x-2 px-6 py-3 text-lg font-semibold shadow-lg hover:shadow-xl transition-shadow disabled:shadow-none"
              >
                <Sparkles className="w-6 h-6" />
                <span>
                  {isGenerating ? 'Generating...' : 'Generate Visualization'}
                </span>
              </button>
            </div>
          )}
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
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {mode === 'ai'
                  ? selectedSuggestion?.title
                  : mode === 'nl'
                    ? (nlParsedIntent?.title || `${nlParsedIntent?.chart_type?.charAt(0).toUpperCase() + nlParsedIntent?.chart_type?.slice(1)} Chart`)
                    : (chartConfig.title || `${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart`)
                }
              </h2>
              {mode === 'ai' && selectedSuggestion && (
                <p className="text-sm text-gray-600 mt-1">{selectedSuggestion.description}</p>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={handleDownloadChart}
                className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                title="Download as PNG"
              >
                <Download className="w-5 h-5" />
              </button>

              {(mode === 'manual' || mode === 'nl') && savedChartId && (
                <>
                  <button
                    className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Saved"
                  >
                    <Save className="w-5 h-5 fill-current" />
                  </button>
                  <button
                    onClick={handleDeleteChart}
                    className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </>
              )}
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-center">
              <Plot
                data={chartData.data}
                layout={{
                  ...chartData.layout,
                  autosize: true,
                  width: undefined,
                  height: 500,
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                }}
                config={{
                  responsive: true,
                  displayModeBar: true,
                  modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                  displaylogo: false,
                }}
                style={{ width: '100%' }}
              />
            </div>
          </div>

          {mode === 'manual' && (
            <div className="mt-4 flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-center space-x-2 text-sm text-blue-700">
                <Eye className="w-4 h-4" />
                <span>Tip: Hover over data points, zoom by clicking and dragging, double-click to reset</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
