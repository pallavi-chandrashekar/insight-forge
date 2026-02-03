import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import contextService, { Context, ContextStats } from '../services/contextService';

const Contexts: React.FC = () => {
  const navigate = useNavigate();
  const [contexts, setContexts] = useState<Context[]>([]);
  const [stats, setStats] = useState<ContextStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [contextTypeFilter, setContextTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    loadContexts();
    loadStats();
  }, [searchTerm, contextTypeFilter, statusFilter, categoryFilter]);

  const loadContexts = async () => {
    try {
      setLoading(true);
      const data = await contextService.listContexts({
        search: searchTerm || undefined,
        context_type: contextTypeFilter || undefined,
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
      });
      setContexts(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load contexts');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await contextService.getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete context "${name}"?`)) {
      return;
    }

    try {
      await contextService.deleteContext(id);
      loadContexts();
      loadStats();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete context');
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      active: 'bg-green-100 text-green-800',
      draft: 'bg-yellow-100 text-yellow-800',
      deprecated: 'bg-gray-100 text-gray-800',
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getTypeBadge = (type: string) => {
    const badges: Record<string, string> = {
      single_dataset: 'bg-blue-100 text-blue-800',
      multi_dataset: 'bg-purple-100 text-purple-800',
    };
    return badges[type] || 'bg-gray-100 text-gray-800';
  };

  const getValidationBadge = (status: string) => {
    const badges: Record<string, string> = {
      passed: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
      pending: 'bg-gray-100 text-gray-800',
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold text-gray-900">Context Files</h1>
          <button
            onClick={() => navigate('/contexts/new')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            + New Context
          </button>
        </div>
        <p className="text-gray-600">
          Manage dataset metadata, relationships, and business rules
        </p>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Total Contexts</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total_contexts}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Single-Dataset</p>
            <p className="text-2xl font-bold text-blue-600">{stats.single_dataset_contexts}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Multi-Dataset</p>
            <p className="text-2xl font-bold text-purple-600">{stats.multi_dataset_contexts}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Active</p>
            <p className="text-2xl font-bold text-green-600">{stats.active_contexts}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Validation Failed</p>
            <p className="text-2xl font-bold text-red-600">{stats.failed_validation}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Search contexts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <select
            value={contextTypeFilter}
            onChange={(e) => setContextTypeFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Types</option>
            <option value="single_dataset">Single Dataset</option>
            <option value="multi_dataset">Multi Dataset</option>
          </select>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="draft">Draft</option>
            <option value="deprecated">Deprecated</option>
          </select>
          <input
            type="text"
            placeholder="Filter by category..."
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading contexts...</p>
        </div>
      )}

      {/* Contexts List */}
      {!loading && contexts.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 text-lg mb-4">No contexts found</p>
          <button
            onClick={() => navigate('/contexts/new')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Create Your First Context
          </button>
        </div>
      )}

      {!loading && contexts.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name & Version
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Validation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stats
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {contexts.map((context) => (
                <tr key={context.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <button
                        onClick={() => navigate(`/contexts/${context.id}`)}
                        className="text-blue-600 hover:text-blue-800 font-medium text-left"
                      >
                        {context.name}
                      </button>
                      <span className="text-sm text-gray-500">v{context.version}</span>
                      {context.category && (
                        <span className="text-xs text-gray-400 mt-1">{context.category}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getTypeBadge(context.context_type)}`}>
                      {context.context_type === 'single_dataset' ? 'Single' : 'Multi'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(context.status)}`}>
                      {context.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getValidationBadge(context.validation_status)}`}>
                      {context.validation_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div className="flex flex-col space-y-1">
                      <span>{context.datasets_count} dataset{context.datasets_count !== 1 ? 's' : ''}</span>
                      {context.relationships_count > 0 && (
                        <span>{context.relationships_count} relationship{context.relationships_count !== 1 ? 's' : ''}</span>
                      )}
                      {context.metrics_count > 0 && (
                        <span>{context.metrics_count} metric{context.metrics_count !== 1 ? 's' : ''}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium">
                    <button
                      onClick={() => navigate(`/contexts/${context.id}`)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(context.id, context.name)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Contexts;
