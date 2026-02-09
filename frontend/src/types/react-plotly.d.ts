declare module 'react-plotly.js' {
  import { Component } from 'react'
  import { PlotParams } from 'plotly.js'

  interface PlotlyProps {
    data: any[]
    layout?: object
    config?: object
    style?: object
    className?: string
    useResizeHandler?: boolean
    onInitialized?: (figure: any, graphDiv: any) => void
    onUpdate?: (figure: any, graphDiv: any) => void
    onPurge?: (figure: any, graphDiv: any) => void
    onError?: (err: any) => void
    onClick?: (data: any) => void
    onHover?: (data: any) => void
    onUnhover?: (data: any) => void
    onSelected?: (data: any) => void
    revision?: number
  }

  export default class Plot extends Component<PlotlyProps> {}
}
