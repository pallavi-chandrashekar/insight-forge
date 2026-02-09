import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import contextService, { ContextDetail } from '../services/contextService';
import ReactMarkdown from 'react-markdown';
import ContextChat from '../components/ContextChat';
import { MessageCircle, FileText, Database, ArrowLeft, Download, Trash2 } from 'lucide-react';

type TabId = 'chat' | 'documentation' | 'datasets' | 'overview';

const ContextDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [context, setContext] = useState<ContextDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>('chat');

  useEffect(() => {
    if (id) {
      loadContext();
    }
  }, [id]);

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

  // Determine which tabs to show based on content
  const tabs = useMemo(() => {
    if (!context) return [];

    const hasDatasets = context.datasets && context.datasets.length > 0;
    const hasStructuredContent = hasDatasets ||
      (context.metrics && context.metrics.length > 0) ||
      (context.glossary && context.glossary.length > 0) ||
      (context.relationships && context.relationships.length > 0);

    // Always show Chat first - it's the main feature
    const availableTabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
      { id: 'chat', label: 'Ask Questions', icon: <MessageCircle className="w-4 h-4" /> },
    ];

    // Show Overview only if there's structured content
    if (hasStructuredContent) {
      availableTabs.push({ id: 'overview', label: 'Overview', icon: null });
    }

    // Show Datasets tab only if there are datasets
    if (hasDatasets) {
      availableTabs.push({
        id: 'datasets',
        label: `Datasets (${context.datasets.length})`,
        icon: <Database className="w-4 h-4" />
      });
    }

    // Always show Documentation
    availableTabs.push({ id: 'documentation', label: 'Documentation', icon: <FileText className="w-4 h-4" /> });

    return availableTabs;
  }, [context]);

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
    if (!window.confirm(`Are you sure you want to delete "${context?.name}"?`)) {
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
          <p className="mt-2 text-gray-600">Loading...</p>
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
      {/* Header - Simplified */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/contexts')}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Contexts
        </button>

        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{context.name}</h1>
            <p className="text-gray-600 mt-1">{context.description}</p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleDownload}
              className="flex items-center space-x-1 px-3 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
            <button
              onClick={handleDelete}
              className="flex items-center space-x-1 px-3 py-2 text-red-600 bg-red-50 rounded-lg hover:bg-red-100"
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete</span>
            </button>
          </div>
        </div>

        {/* Status badges - simplified */}
        <div className="flex gap-2 mt-3">
          <span className={`px-2 py-1 text-xs font-medium rounded ${
            context.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {context.status}
          </span>
        </div>
      </div>

      {/* Tabs - Simplified */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg shadow">
        {/* Chat Tab - Main Feature */}
        {activeTab === 'chat' && (
          <div className="h-[600px]">
            <ContextChat
              contextId={context.id}
              contextName={context.name}
            />
          </div>
        )}

        {/* Overview Tab - Only for structured contexts */}
        {activeTab === 'overview' && (
          <div className="p-6">
            <h2 className="text-xl font-bold mb-4">Context Overview</h2>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
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
                <p className="text-sm text-gray-600">Glossary</p>
                <p className="text-2xl font-bold text-gray-900">{context.glossary?.length || 0}</p>
              </div>
            </div>

            {/* Metrics List */}
            {context.metrics && context.metrics.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold mb-3">Metrics</h3>
                <div className="space-y-2">
                  {context.metrics.map((metric, idx) => (
                    <div key={idx} className="bg-gray-50 p-3 rounded-lg">
                      <div className="flex justify-between">
                        <span className="font-medium">{metric.name}</span>
                        <code className="text-xs bg-gray-200 px-2 py-1 rounded">{metric.expression}</code>
                      </div>
                      {metric.description && <p className="text-sm text-gray-600 mt-1">{metric.description}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Glossary */}
            {context.glossary && context.glossary.length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold mb-3">Business Glossary</h3>
                <div className="space-y-2">
                  {context.glossary.map((entry, idx) => (
                    <div key={idx} className="bg-gray-50 p-3 rounded-lg">
                      <span className="font-medium">{entry.term}:</span>
                      <span className="text-gray-600 ml-2">{entry.definition}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Business Rules */}
            {context.business_rules && context.business_rules.length > 0 && (
              <div>
                <h3 className="font-semibold mb-3">Business Rules</h3>
                <div className="space-y-2">
                  {context.business_rules.map((rule, idx) => (
                    <div key={idx} className="bg-gray-50 p-3 rounded-lg">
                      <div className="flex justify-between items-start">
                        <span className="font-medium">{rule.name}</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          rule.severity === 'error' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {rule.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{rule.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Datasets Tab */}
        {activeTab === 'datasets' && (
          <div className="p-6">
            <h2 className="text-xl font-bold mb-4">Datasets</h2>
            <div className="space-y-4">
              {context.datasets.map((ds, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-lg">{ds.name}</h3>
                      {ds.description && <p className="text-sm text-gray-600 mt-1">{ds.description}</p>}
                    </div>
                    <span className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">{ds.dataset_id}</span>
                  </div>

                  {/* Columns Table */}
                  {ds.columns && ds.columns.length > 0 && (
                    <div className="mt-4 overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Column</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Type</th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500">Description</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {ds.columns.slice(0, 10).map((col: any, colIdx: number) => (
                            <tr key={colIdx}>
                              <td className="px-3 py-2 font-mono text-xs">{col.name}</td>
                              <td className="px-3 py-2 font-mono text-xs text-gray-500">{col.data_type}</td>
                              <td className="px-3 py-2 text-gray-600">{col.description || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {ds.columns.length > 10 && (
                        <p className="text-sm text-gray-500 mt-2 px-3">
                          + {ds.columns.length - 10} more columns
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Documentation Tab */}
        {activeTab === 'documentation' && (
          <div className="p-6">
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
