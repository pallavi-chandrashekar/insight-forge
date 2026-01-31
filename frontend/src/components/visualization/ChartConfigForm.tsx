import { useState, useEffect } from 'react'
import { ChartType, VizConfig, Dataset } from '../../types'

interface ChartConfigFormProps {
  chartType: ChartType
  dataset: Dataset
  initialConfig?: VizConfig
  onConfigChange: (config: VizConfig) => void
}

export default function ChartConfigForm({
  chartType,
  dataset,
  initialConfig,
  onConfigChange,
}: ChartConfigFormProps) {
  const [config, setConfig] = useState<VizConfig>(
    initialConfig || {
      x_column: undefined,
      y_column: undefined,
      color_column: undefined,
      size_column: undefined,
      aggregation: undefined,
      title: undefined,
      x_label: undefined,
      y_label: undefined,
    }
  )

  useEffect(() => {
    if (initialConfig) {
      setConfig(initialConfig)
    }
  }, [initialConfig])

  useEffect(() => {
    onConfigChange(config)
  }, [config, onConfigChange])

  const columns = dataset.schema?.columns || []
  const numericColumns = columns.filter((col) =>
    ['int64', 'float64', 'int32', 'float32', 'number'].some((type) =>
      col.dtype.toLowerCase().includes(type)
    )
  )
  const categoricalColumns = columns.filter((col) =>
    ['object', 'string', 'category', 'bool'].some((type) => col.dtype.toLowerCase().includes(type))
  )

  const handleChange = (field: keyof VizConfig, value: string | undefined) => {
    setConfig((prev) => ({ ...prev, [field]: value || undefined }))
  }

  const getRequiredFields = () => {
    switch (chartType) {
      case 'bar':
      case 'pie':
        return { x: true, y: true }
      case 'line':
      case 'area':
      case 'scatter':
        return { x: true, y: true }
      case 'histogram':
        return { x: true, y: false }
      case 'box':
        return { x: false, y: true }
      case 'heatmap':
        return { x: false, y: false }
      default:
        return { x: false, y: false }
    }
  }

  const required = getRequiredFields()

  return (
    <div className="space-y-4">
      {/* Title */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Chart Title</label>
        <input
          type="text"
          value={config.title || ''}
          onChange={(e) => handleChange('title', e.target.value)}
          className="input"
          placeholder="Enter chart title"
        />
      </div>

      {/* X Column */}
      {chartType !== 'heatmap' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            X-Axis Column {required.x && <span className="text-red-500">*</span>}
          </label>
          <select
            value={config.x_column || ''}
            onChange={(e) => handleChange('x_column', e.target.value)}
            className="input"
            required={required.x}
          >
            <option value="">Select column...</option>
            {columns.map((col) => (
              <option key={col.name} value={col.name}>
                {col.name} ({col.dtype})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Y Column */}
      {chartType !== 'histogram' && chartType !== 'heatmap' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Y-Axis Column {required.y && <span className="text-red-500">*</span>}
          </label>
          <select
            value={config.y_column || ''}
            onChange={(e) => handleChange('y_column', e.target.value)}
            className="input"
            required={required.y}
          >
            <option value="">Select column...</option>
            {numericColumns.map((col) => (
              <option key={col.name} value={col.name}>
                {col.name} ({col.dtype})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Color Column */}
      {['bar', 'line', 'scatter', 'histogram', 'area', 'box'].includes(chartType) && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Color/Group By (Optional)
          </label>
          <select
            value={config.color_column || ''}
            onChange={(e) => handleChange('color_column', e.target.value)}
            className="input"
          >
            <option value="">None</option>
            {categoricalColumns.map((col) => (
              <option key={col.name} value={col.name}>
                {col.name} ({col.dtype})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Size Column (Scatter only) */}
      {chartType === 'scatter' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Size Column (Optional)
          </label>
          <select
            value={config.size_column || ''}
            onChange={(e) => handleChange('size_column', e.target.value)}
            className="input"
          >
            <option value="">None</option>
            {numericColumns.map((col) => (
              <option key={col.name} value={col.name}>
                {col.name} ({col.dtype})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Aggregation */}
      {['bar', 'pie', 'heatmap'].includes(chartType) && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Aggregation (Optional)
          </label>
          <select
            value={config.aggregation || ''}
            onChange={(e) => handleChange('aggregation', e.target.value)}
            className="input"
          >
            <option value="">None</option>
            <option value="sum">Sum</option>
            <option value="mean">Mean</option>
            <option value="count">Count</option>
            <option value="median">Median</option>
            <option value="min">Min</option>
            <option value="max">Max</option>
          </select>
        </div>
      )}

      {/* Axis Labels */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            X-Axis Label (Optional)
          </label>
          <input
            type="text"
            value={config.x_label || ''}
            onChange={(e) => handleChange('x_label', e.target.value)}
            className="input"
            placeholder="Auto"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Y-Axis Label (Optional)
          </label>
          <input
            type="text"
            value={config.y_label || ''}
            onChange={(e) => handleChange('y_label', e.target.value)}
            className="input"
            placeholder="Auto"
          />
        </div>
      </div>
    </div>
  )
}
