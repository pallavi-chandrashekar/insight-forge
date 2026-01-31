import { ChartType } from '../../types'
import {
  BarChart3,
  LineChart,
  ScatterChart,
  PieChart,
  BarChart2,
  Grid3X3,
  BoxSelect,
  AreaChart,
  Table,
} from 'lucide-react'

interface ChartTypeSelectorProps {
  selected: ChartType | null
  onSelect: (type: ChartType) => void
}

const chartTypes: Array<{
  type: ChartType
  icon: typeof BarChart3
  label: string
  description: string
}> = [
  {
    type: 'bar',
    icon: BarChart3,
    label: 'Bar Chart',
    description: 'Compare values across categories',
  },
  {
    type: 'line',
    icon: LineChart,
    label: 'Line Chart',
    description: 'Show trends over time',
  },
  {
    type: 'scatter',
    icon: ScatterChart,
    label: 'Scatter Plot',
    description: 'Display relationships between variables',
  },
  {
    type: 'pie',
    icon: PieChart,
    label: 'Pie Chart',
    description: 'Show proportions',
  },
  {
    type: 'histogram',
    icon: BarChart2,
    label: 'Histogram',
    description: 'Show distribution of data',
  },
  {
    type: 'heatmap',
    icon: Grid3X3,
    label: 'Heatmap',
    description: 'Visualize matrix data',
  },
  {
    type: 'box',
    icon: BoxSelect,
    label: 'Box Plot',
    description: 'Show statistical distribution',
  },
  {
    type: 'area',
    icon: AreaChart,
    label: 'Area Chart',
    description: 'Emphasize magnitude of change',
  },
  {
    type: 'table',
    icon: Table,
    label: 'Table',
    description: 'Display structured data',
  },
]

export default function ChartTypeSelector({ selected, onSelect }: ChartTypeSelectorProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {chartTypes.map(({ type, icon: Icon, label, description }) => (
        <button
          key={type}
          onClick={() => onSelect(type)}
          className={`p-4 border-2 rounded-lg text-left transition-all hover:shadow-md ${
            selected === type
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-primary-300'
          }`}
        >
          <Icon className={`w-8 h-8 mb-2 ${selected === type ? 'text-primary-600' : 'text-gray-600'}`} />
          <h3 className="font-semibold text-gray-900 mb-1">{label}</h3>
          <p className="text-xs text-gray-500">{description}</p>
        </button>
      ))}
    </div>
  )
}
