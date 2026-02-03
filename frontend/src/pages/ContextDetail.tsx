import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import contextService, { ContextDetail } from '../services/contextService';
import ReactMarkdown from 'react-markdown';
import mermaid from 'mermaid';

const ContextDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [context, setContext] = useState<ContextDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'datasets' | 'relationships' | 'metrics' | 'glossary' | 'rules' | 'markdown'>('overview');

  useEffect(() => {
    if (id) {
      loadContext();
    }
  }, [id]);

  useEffect(() => {
    // Initialize Mermaid
    mermaid.initialize({ startOnLoad: true, theme: 'default' });

    // Render ER diagram if it exists
    if (context?.data_model?.er_diagram) {
      try {
        mermaid.contentLoaded();
      } catch (err) {
        console.error('Mermaid rendering error:', err);
      }
    }
  }, [context, activeTab]);

  const loadContext = async () => {
    try {
      setLoading(true);
      const data = await contextService.getContext(id!);
      setContext(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load context');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const blob = await contextService.downloadContext(id!);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${context?.name}_v${context?.version}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to download context');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete context "${context?.name}"?`)) {
      return;
    }

    try {
      await contextService.deleteContext(id!);
      navigate('/contexts');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete context');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading context...</p>
        </div>
      </div>
    );
  }

  if (error || !context) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error || 'Context not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <button
              onClick={() => navigate('/contexts')}
              className="text-blue-600 hover:text-blue-800 mb-2"
            >
              ← Back to Contexts
            </button>
            <h1 className="text-3xl font-bold text-gray-900">{context.name}</h1>
            <p className="text-gray-600 mt-1">Version {context.version}</p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleDownload}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Download
            </button>
            <button
              onClick={handleDelete}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
            >
              Delete
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
            context.context_type === 'single_dataset'
              ? 'bg-blue-100 text-blue-800'
              : 'bg-purple-100 text-purple-800'
          }`}>
            {context.context_type === 'single_dataset' ? 'Single Dataset' : 'Multi Dataset'}
          </span>
          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
            context.status === 'active'
              ? 'bg-green-100 text-green-800'
              : context.status === 'draft'
              ? 'bg-yellow-100 text-yellow-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {context.status}
          </span>
          <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
            context.validation_status === 'passed'
              ? 'bg-green-100 text-green-800'
              : context.validation_status === 'warning'
              ? 'bg-yellow-100 text-yellow-800'
              : context.validation_status === 'failed'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            Validation: {context.validation_status}
          </span>
          {context.category && (
            <span className="px-3 py-1 text-sm bg-gray-100 text-gray-800 rounded-full">
              {context.category}
            </span>
          )}
        </div>

        <p className="text-gray-700 mb-4">{context.description}</p>

        {/* Tags */}
        {context.tags && context.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {context.tags.map((tag, idx) => (
              <span key={idx} className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded">
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Validation Errors/Warnings */}
        {context.validation_errors && context.validation_errors.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <h3 className="text-red-800 font-semibold mb-2">Validation Errors:</h3>
            <ul className="list-disc list-inside space-y-1">
              {context.validation_errors.map((err, idx) => (
                <li key={idx} className="text-red-700 text-sm">
                  {err.message} {err.field && `(${err.field})`}
                </li>
              ))}
            </ul>
          </div>
        )}

        {context.validation_warnings && context.validation_warnings.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <h3 className="text-yellow-800 font-semibold mb-2">Validation Warnings:</h3>
            <ul className="list-disc list-inside space-y-1">
              {context.validation_warnings.map((warn, idx) => (
                <li key={idx} className="text-yellow-700 text-sm">
                  {warn.message} {warn.field && `(${warn.field})`}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'datasets', label: `Datasets (${context.datasets.length})` },
            { id: 'relationships', label: `Relationships (${context.relationships?.length || 0})` },
            { id: 'metrics', label: `Metrics (${context.metrics?.length || 0})` },
            { id: 'glossary', label: `Glossary (${context.glossary?.length || 0})` },
            { id: 'rules', label: `Business Rules (${context.business_rules?.length || 0})` },
            { id: 'markdown', label: 'Documentation' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow p-6">
        {activeTab === 'overview' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Context Overview</h2>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Datasets</p>
                <p className="text-2xl font-bold text-gray-900">{context.datasets.length}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Relationships</p>
                <p className="text-2xl font-bold text-gray-900">{context.relationships?.length || 0}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Metrics</p>
                <p className="text-2xl font-bold text-gray-900">{context.metrics?.length || 0}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Glossary Terms</p>
                <p className="text-2xl font-bold text-gray-900">{context.glossary?.length || 0}</p>
              </div>
            </div>

            {/* ER Diagram */}
            {context.data_model?.er_diagram && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Entity Relationship Diagram</h3>
                <div className="bg-gray-50 p-6 rounded-lg overflow-x-auto">
                  <div className="mermaid">
                    {context.data_model.er_diagram}
                  </div>
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="space-y-2">
              {context.owner && (
                <div className="flex">
                  <span className="text-gray-600 w-32">Owner:</span>
                  <span className="text-gray-900">{context.owner}</span>
                </div>
              )}
              {context.created_by && (
                <div className="flex">
                  <span className="text-gray-600 w-32">Created By:</span>
                  <span className="text-gray-900">{context.created_by}</span>
                </div>
              )}
              {context.created_at && (
                <div className="flex">
                  <span className="text-gray-600 w-32">Created:</span>
                  <span className="text-gray-900">{new Date(context.created_at).toLocaleString()}</span>
                </div>
              )}
              {context.updated_at && (
                <div className="flex">
                  <span className="text-gray-600 w-32">Updated:</span>
                  <span className="text-gray-900">{new Date(context.updated_at).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'datasets' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Datasets</h2>
            <div className="space-y-4">
              {context.datasets.map((ds, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-lg">{ds.name}</h3>
                      <p className="text-sm text-gray-600">ID: {ds.id}</p>
                      {ds.alias && <p className="text-sm text-gray-600">Alias: {ds.alias}</p>}
                    </div>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded">{ds.dataset_id}</span>
                  </div>
                  {ds.description && <p className="text-gray-700 mb-3">{ds.description}</p>}

                  {/* Catalog Info */}
                  {ds.catalog && (
                    <div className="bg-gray-50 p-3 rounded mt-3 space-y-2 text-sm">
                      {ds.catalog.business_name && (
                        <div><strong>Business Name:</strong> {ds.catalog.business_name}</div>
                      )}
                      {ds.catalog.purpose && (
                        <div><strong>Purpose:</strong> {ds.catalog.purpose}</div>
                      )}
                      {ds.catalog.usage_notes && (
                        <div><strong>Usage Notes:</strong> {ds.catalog.usage_notes}</div>
                      )}
                      {ds.catalog.compliance && ds.catalog.compliance.length > 0 && (
                        <div>
                          <strong>Compliance:</strong>{' '}
                          {ds.catalog.compliance.map((c: string, i: number) => (
                            <span key={i} className="inline-block bg-red-100 text-red-800 px-2 py-0.5 rounded text-xs ml-1">
                              {c}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Data Dictionary */}
                  {ds.columns && ds.columns.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-semibold mb-2">Data Dictionary ({ds.columns.length} columns)</h4>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200 text-sm">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Column</th>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Business Name</th>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {ds.columns.map((col: any, colIdx: number) => (
                              <tr key={colIdx}>
                                <td className="px-3 py-2 font-mono text-xs">
                                  {col.name}
                                  {col.primary_key && <span className="ml-1 text-blue-600">PK</span>}
                                </td>
                                <td className="px-3 py-2">{col.business_name || '-'}</td>
                                <td className="px-3 py-2 font-mono text-xs">{col.data_type}</td>
                                <td className="px-3 py-2 text-gray-600">{col.description || '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'relationships' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Relationships</h2>
            {!context.relationships || context.relationships.length === 0 ? (
              <p className="text-gray-500">No relationships defined</p>
            ) : (
              <div className="space-y-4">
                {context.relationships.map((rel, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-lg mb-2">{rel.name}</h3>
                    <p className="text-sm text-gray-600 mb-3">{rel.description}</p>
                    <div className="bg-gray-50 p-3 rounded space-y-2 text-sm">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono bg-blue-100 px-2 py-1 rounded">{rel.left_dataset}</span>
                        <span className="text-gray-600">{rel.join_type.toUpperCase()} JOIN</span>
                        <span className="font-mono bg-blue-100 px-2 py-1 rounded">{rel.right_dataset}</span>
                      </div>
                      <div className="font-semibold mt-2">Conditions:</div>
                      {rel.conditions && rel.conditions.map((cond: any, condIdx: number) => (
                        <div key={condIdx} className="ml-4 font-mono text-xs">
                          {cond.left_column} {cond.operator} {cond.right_column}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'metrics' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Metrics</h2>
            {!context.metrics || context.metrics.length === 0 ? (
              <p className="text-gray-500">No metrics defined</p>
            ) : (
              <div className="space-y-4">
                {context.metrics.map((metric, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-semibold text-lg">{metric.name}</h3>
                        <p className="text-sm text-gray-600">ID: {metric.id}</p>
                      </div>
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded">{metric.data_type}</span>
                    </div>
                    {metric.description && <p className="text-gray-700 mb-3">{metric.description}</p>}
                    <div className="bg-gray-50 p-3 rounded font-mono text-sm">
                      {metric.expression}
                    </div>
                    {metric.format && (
                      <div className="mt-2 text-sm text-gray-600">Format: {metric.format}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'glossary' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Business Glossary</h2>
            {!context.glossary || context.glossary.length === 0 ? (
              <p className="text-gray-500">No glossary terms defined</p>
            ) : (
              <div className="space-y-4">
                {context.glossary.map((entry, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-lg mb-2">{entry.term}</h3>
                    <p className="text-gray-700 mb-3">{entry.definition}</p>
                    {entry.synonyms && entry.synonyms.length > 0 && (
                      <div className="text-sm mb-2">
                        <strong>Synonyms:</strong> {entry.synonyms.join(', ')}
                      </div>
                    )}
                    {entry.related_columns && entry.related_columns.length > 0 && (
                      <div className="text-sm mb-2">
                        <strong>Related Columns:</strong> {entry.related_columns.join(', ')}
                      </div>
                    )}
                    {entry.examples && (
                      <div className="text-sm bg-gray-50 p-2 rounded mt-2">
                        <strong>Examples:</strong> {entry.examples}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'rules' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Business Rules</h2>
            {!context.business_rules || context.business_rules.length === 0 ? (
              <p className="text-gray-500">No business rules defined</p>
            ) : (
              <div className="space-y-4">
                {context.business_rules.map((rule, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-lg">{rule.name}</h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${
                        rule.severity === 'error' ? 'bg-red-100 text-red-800' :
                        rule.severity === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {rule.severity}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-3">{rule.description}</p>
                    <div className="bg-gray-50 p-3 rounded space-y-2 text-sm">
                      <div><strong>Type:</strong> {rule.rule_type}</div>
                      <div><strong>Condition:</strong> <code className="font-mono text-xs">{rule.condition}</code></div>
                      {rule.error_message && (
                        <div><strong>Error Message:</strong> {rule.error_message}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'markdown' && (
          <div>
            <h2 className="text-xl font-bold mb-4">Documentation</h2>
            <div className="prose max-w-none">
              <ReactMarkdown>{context.markdown_content}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContextDetailPage;
