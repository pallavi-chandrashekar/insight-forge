import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { datasetAPI } from '../services/api'
import type { Dataset, DatasetPreview, DatasetDeleteInfo } from '../types'
import { ArrowLeft, Trash2, FileText, AlertTriangle, X, Download, ChevronDown, Table2, Copy, ExternalLink } from 'lucide-react'

export default function DatasetPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [dataset, setDataset] = useState<Dataset | null>(null)
  const [preview, setPreview] = useState<DatasetPreview | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isDeleting, setIsDeleting] = useState(false)

  // Delete confirmation modal state
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleteInfo, setDeleteInfo] = useState<DatasetDeleteInfo | null>(null)
  const [isLoadingDeleteInfo, setIsLoadingDeleteInfo] = useState(false)

  // Schema download
  const [showDownloadMenu, setShowDownloadMenu] = useState(false)
  const [showDataModelModal, setShowDataModelModal] = useState(false)
  const [showVisualModelModal, setShowVisualModelModal] = useState(false)
  const [generatedSQL, setGeneratedSQL] = useState('')
  const [mermaidCode, setMermaidCode] = useState('')

  useEffect(() => {
    if (id) loadDataset(id)
  }, [id])

  const loadDataset = async (datasetId: string) => {
    try {
      const [datasetData, previewData] = await Promise.all([
        datasetAPI.get(datasetId),
        datasetAPI.preview(datasetId, 20),
      ])
      setDataset(datasetData)
      setPreview(previewData)
    } catch (error) {
      console.error('Error loading dataset:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteClick = async () => {
    if (!id) return

    setIsLoadingDeleteInfo(true)
    try {
      const info = await datasetAPI.getDeleteInfo(id)
      setDeleteInfo(info)
      setShowDeleteModal(true)
    } catch (error) {
      console.error('Error getting delete info:', error)
      // Fall back to simple delete if we can't get info
      if (confirm('Are you sure you want to delete this dataset?')) {
        await performDelete({ deleteContext: true, deleteLinkedDatasets: false })
      }
    } finally {
      setIsLoadingDeleteInfo(false)
    }
  }

  const performDelete = async (options: {
    deleteContext: boolean
    deleteLinkedDatasets: boolean
  }) => {
    if (!id) return

    setIsDeleting(true)
    setShowDeleteModal(false)
    try {
      const result = await datasetAPI.delete(id, options)
      console.log('Delete result:', result)
      navigate('/dashboard')
    } catch (error) {
      console.error('Error deleting dataset:', error)
      alert('Failed to delete dataset')
      setIsDeleting(false)
    }
  }

  const mapDtypeToSQL = (dtype: string): string => {
    const lower = dtype.toLowerCase()
    if (lower.includes('int64') || lower.includes('int32')) return 'BIGINT'
    if (lower.includes('int')) return 'INTEGER'
    if (lower.includes('float') || lower.includes('double')) return 'DOUBLE PRECISION'
    if (lower.includes('bool')) return 'BOOLEAN'
    if (lower.includes('datetime') || lower.includes('timestamp')) return 'TIMESTAMP'
    if (lower.includes('date')) return 'DATE'
    if (lower.includes('time')) return 'TIME'
    return 'VARCHAR(255)'
  }

  const generateDataModel = () => {
    if (!dataset?.schema?.columns) return

    const tableName = dataset.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '')

    const columns = dataset.schema.columns.map((col) => {
      const sqlType = mapDtypeToSQL(col.dtype)
      const nullable = col.nullable ? '' : ' NOT NULL'
      const comment = col.sample_values?.length
        ? ` -- e.g., ${col.sample_values.slice(0, 2).map(String).join(', ')}`
        : ''
      return `  ${col.name.toLowerCase().replace(/[^a-z0-9_]/g, '_')} ${sqlType}${nullable}${comment}`
    })

    const sql = `-- Generated from: ${dataset.name}
-- Rows: ${dataset.row_count?.toLocaleString() || 'unknown'}
-- Columns: ${dataset.column_count || columns.length}

CREATE TABLE ${tableName} (
${columns.join(',\n')}
);

-- Sample queries:
-- SELECT * FROM ${tableName} LIMIT 10;
-- SELECT COUNT(*) FROM ${tableName};
`

    setGeneratedSQL(sql)
    setShowDataModelModal(true)
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      alert('Copied to clipboard!')
    } catch {
      // Fallback
      const textarea = document.createElement('textarea')
      textarea.value = text
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      alert('Copied to clipboard!')
    }
  }

  const downloadSQL = () => {
    const blob = new Blob([generatedSQL], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${dataset?.name.replace(/[^a-z0-9]/gi, '_')}_ddl.sql`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const generateVisualModel = () => {
    if (!dataset?.schema?.columns) return

    const tableName = dataset.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '')

    // Generate Mermaid ER diagram syntax
    const columns = dataset.schema.columns.map((col) => {
      const sqlType = mapDtypeToSQL(col.dtype).replace(' ', '_')
      const pk = col.name.toLowerCase().includes('id') && dataset.schema!.columns.indexOf(col) === 0 ? 'PK' : ''
      return `    ${sqlType} ${col.name.replace(/[^a-z0-9_]/gi, '_')} ${pk}`.trimEnd()
    })

    const mermaid = `erDiagram
    ${tableName.toUpperCase()} {
${columns.join('\n')}
    }`

    setMermaidCode(mermaid)
    setShowVisualModelModal(true)
  }

  const openInMermaidLive = () => {
    // Encode the mermaid code for URL
    const encoded = btoa(JSON.stringify({ code: mermaidCode, mermaid: { theme: 'default' } }))
    const url = `https://mermaid.live/edit#base64:${encoded}`
    window.open(url, '_blank')
  }

  const openInDBDiagram = () => {
    // DBDiagram uses a different syntax, so we'll generate DBML
    if (!dataset?.schema?.columns) return

    const tableName = dataset.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_|_$/g, '')

    const columns = dataset.schema.columns.map((col, idx) => {
      const sqlType = mapDtypeToSQL(col.dtype).toLowerCase().replace(' ', '_')
      const pk = idx === 0 && col.name.toLowerCase().includes('id') ? ' [pk]' : ''
      const note = col.sample_values?.length ? ` [note: 'e.g., ${col.sample_values.slice(0, 2).map(String).join(', ')}']` : ''
      return `  ${col.name.replace(/[^a-z0-9_]/gi, '_')} ${sqlType}${pk}${note}`
    })

    const dbml = `Table ${tableName} {\n${columns.join('\n')}\n}`

    // Copy to clipboard and open dbdiagram
    navigator.clipboard.writeText(dbml).then(() => {
      window.open('https://dbdiagram.io/d', '_blank')
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dataset...</div>
      </div>
    )
  }

  if (!dataset || !preview) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Dataset not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <button
            onClick={() => navigate(-1)}
            className="btn btn-secondary"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center space-x-3">
              <FileText className="w-6 h-6 text-gray-400" />
              <h1 className="text-3xl font-bold text-gray-900">{dataset.name}</h1>
            </div>
            {dataset.description && (
              <p className="text-gray-600 mt-2">{dataset.description}</p>
            )}
            <div className="flex items-center space-x-6 mt-4 text-sm text-gray-500">
              <span>{dataset.row_count?.toLocaleString()} rows</span>
              <span>{dataset.column_count} columns</span>
              <span className="capitalize">{dataset.source_type}</span>
              <span>{new Date(dataset.created_at).toLocaleString()}</span>
            </div>
          </div>
        </div>

        <button
          onClick={handleDeleteClick}
          disabled={isDeleting || isLoadingDeleteInfo}
          className="btn btn-danger flex items-center space-x-2"
        >
          <Trash2 className="w-5 h-5" />
          <span>
            {isDeleting
              ? 'Deleting...'
              : isLoadingDeleteInfo
              ? 'Loading...'
              : 'Delete'}
          </span>
        </button>
      </div>

      {/* Schema */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Schema</h2>
          <div className="relative">
            <button
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
              className="btn btn-secondary flex items-center space-x-2 text-sm"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
              <ChevronDown className="w-4 h-4" />
            </button>
            {showDownloadMenu && (
              <div className="absolute right-0 mt-1 w-52 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">Export Schema</div>
                <a
                  href={`/api/datasets/${id}/schema/download?format=json`}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  onClick={() => setShowDownloadMenu(false)}
                >
                  Download as JSON
                </a>
                <a
                  href={`/api/datasets/${id}/schema/download?format=csv`}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  onClick={() => setShowDownloadMenu(false)}
                >
                  Download as CSV
                </a>
                <hr className="my-1" />
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">Data Model</div>
                <button
                  onClick={() => {
                    setShowDownloadMenu(false)
                    generateVisualModel()
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                >
                  <Table2 className="w-4 h-4" />
                  <span>Visual Diagram</span>
                </button>
                <button
                  onClick={() => {
                    setShowDownloadMenu(false)
                    generateDataModel()
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>SQL DDL</span>
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Column
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nullable
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sample Values
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dataset.schema?.columns.map((column, idx) => (
                <tr key={idx}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {column.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {column.dtype}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {column.nullable ? 'Yes' : 'No'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {column.sample_values.slice(0, 3).map(String).join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Preview */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Data Preview ({preview.preview_rows} of {preview.total_rows.toLocaleString()} rows)
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {preview.columns.map((column) => (
                  <th
                    key={column}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {preview.data.map((row, idx) => (
                <tr key={idx}>
                  {preview.columns.map((column) => (
                    <td
                      key={column}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                    >
                      {String(row[column] ?? '')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && deleteInfo && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                Delete Dataset
              </h3>
              <button
                onClick={() => setShowDeleteModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <p className="text-gray-600">
                Are you sure you want to delete{' '}
                <span className="font-semibold">{deleteInfo.dataset_name}</span>?
              </p>

              {deleteInfo.has_context && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-800">
                    This dataset is linked to context:{' '}
                    <span className="font-semibold">{deleteInfo.context_name}</span>
                  </p>
                </div>
              )}

              {deleteInfo.other_datasets.length > 0 && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-amber-800">
                        Other datasets share the same context:
                      </p>
                      <ul className="mt-1 text-sm text-amber-700 list-disc list-inside">
                        {deleteInfo.other_datasets.map((ds) => (
                          <li key={ds.id}>{ds.name}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t bg-gray-50 space-y-2">
              {deleteInfo.other_datasets.length > 0 ? (
                <>
                  <button
                    onClick={() =>
                      performDelete({ deleteContext: false, deleteLinkedDatasets: false })
                    }
                    className="w-full btn btn-secondary text-left"
                  >
                    Delete this dataset only (keep context)
                  </button>
                  <button
                    onClick={() =>
                      performDelete({ deleteContext: true, deleteLinkedDatasets: false })
                    }
                    className="w-full btn bg-amber-500 hover:bg-amber-600 text-white text-left"
                  >
                    Delete dataset + context (other datasets will lose context)
                  </button>
                  <button
                    onClick={() =>
                      performDelete({ deleteContext: true, deleteLinkedDatasets: true })
                    }
                    className="w-full btn btn-danger text-left"
                  >
                    Delete ALL linked datasets + context
                  </button>
                </>
              ) : (
                <>
                  {deleteInfo.has_context ? (
                    <>
                      <button
                        onClick={() =>
                          performDelete({ deleteContext: false, deleteLinkedDatasets: false })
                        }
                        className="w-full btn btn-secondary text-left"
                      >
                        Delete dataset only (keep context)
                      </button>
                      <button
                        onClick={() =>
                          performDelete({ deleteContext: true, deleteLinkedDatasets: false })
                        }
                        className="w-full btn btn-danger text-left"
                      >
                        Delete dataset + context
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() =>
                        performDelete({ deleteContext: false, deleteLinkedDatasets: false })
                      }
                      className="w-full btn btn-danger"
                    >
                      Delete Dataset
                    </button>
                  )}
                </>
              )}

              <button
                onClick={() => setShowDeleteModal(false)}
                className="w-full btn btn-secondary mt-2"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Visual Data Model Modal */}
      {showVisualModelModal && dataset?.schema && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                Visual Data Model
              </h3>
              <button
                onClick={() => setShowVisualModelModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-6">
              <div className="flex flex-col lg:flex-row gap-6">
                {/* Visual ER Diagram */}
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-500 mb-3">Entity Diagram</h4>
                  <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-6 flex justify-center">
                    <div className="inline-block">
                      {/* Table Header */}
                      <div className="bg-blue-600 text-white px-4 py-2 rounded-t-lg font-semibold text-center">
                        {dataset.name}
                      </div>
                      {/* Table Body */}
                      <div className="bg-white border-2 border-blue-600 border-t-0 rounded-b-lg shadow-lg min-w-[280px]">
                        {dataset.schema.columns.map((col, idx) => {
                          const isPK = idx === 0 && col.name.toLowerCase().includes('id')
                          return (
                            <div
                              key={idx}
                              className={`flex items-center px-3 py-2 ${
                                idx !== dataset.schema!.columns.length - 1 ? 'border-b border-gray-200' : ''
                              } ${isPK ? 'bg-yellow-50' : ''}`}
                            >
                              <div className="flex items-center space-x-2 flex-1">
                                {isPK && (
                                  <span className="text-xs bg-yellow-400 text-yellow-900 px-1.5 py-0.5 rounded font-medium">
                                    PK
                                  </span>
                                )}
                                <span className="font-medium text-gray-900">{col.name}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <span className="text-sm text-blue-600 font-mono">
                                  {mapDtypeToSQL(col.dtype)}
                                </span>
                                {!col.nullable && (
                                  <span className="text-xs text-red-500">NOT NULL</span>
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </div>
                      {/* Table Footer - Stats */}
                      <div className="mt-2 text-center text-xs text-gray-500">
                        {dataset.row_count?.toLocaleString()} rows • {dataset.column_count} columns
                      </div>
                    </div>
                  </div>
                </div>

                {/* Mermaid Code */}
                <div className="lg:w-80">
                  <h4 className="text-sm font-medium text-gray-500 mb-3">Mermaid ER Code</h4>
                  <pre className="bg-gray-900 text-green-400 p-3 rounded-lg text-xs font-mono overflow-x-auto whitespace-pre h-64 overflow-y-auto">
                    {mermaidCode}
                  </pre>
                  <button
                    onClick={() => copyToClipboard(mermaidCode)}
                    className="mt-2 w-full btn btn-secondary text-sm flex items-center justify-center space-x-2"
                  >
                    <Copy className="w-4 h-4" />
                    <span>Copy Mermaid Code</span>
                  </button>
                </div>
              </div>
            </div>

            <div className="p-4 border-t bg-gray-50">
              <div className="text-sm text-gray-600 mb-3">Open in external tools:</div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={openInMermaidLive}
                  className="btn btn-secondary text-sm flex items-center space-x-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Mermaid Live Editor</span>
                </button>
                <button
                  onClick={openInDBDiagram}
                  className="btn btn-secondary text-sm flex items-center space-x-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>dbdiagram.io</span>
                </button>
                <button
                  onClick={() => {
                    setShowVisualModelModal(false)
                    generateDataModel()
                  }}
                  className="btn btn-secondary text-sm flex items-center space-x-2"
                >
                  <FileText className="w-4 h-4" />
                  <span>View SQL DDL</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SQL Data Model Modal */}
      {showDataModelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                SQL Data Model (DDL)
              </h3>
              <button
                onClick={() => setShowDataModelModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4">
              <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm font-mono overflow-x-auto whitespace-pre">
                {generatedSQL}
              </pre>
            </div>

            <div className="p-4 border-t bg-gray-50 flex space-x-2">
              <button
                onClick={() => copyToClipboard(generatedSQL)}
                className="flex-1 btn btn-secondary flex items-center justify-center space-x-2"
              >
                <FileText className="w-4 h-4" />
                <span>Copy to Clipboard</span>
              </button>
              <button
                onClick={downloadSQL}
                className="flex-1 btn btn-primary flex items-center justify-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Download .sql</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
