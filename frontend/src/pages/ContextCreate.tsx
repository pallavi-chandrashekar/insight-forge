import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import contextService from '../services/contextService';

const ContextCreate: React.FC = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'upload' | 'paste'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [content, setContent] = useState('');
  const [validate, setValidate] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setValidationErrors(null);

      const context = await contextService.uploadContextFile(file, validate);
      navigate(`/contexts/${context.id}`);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'object' && detail.validation) {
        setValidationErrors(detail.validation);
        setError(detail.message || 'Validation failed');
      } else {
        setError(detail || 'Failed to upload context');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!content.trim()) {
      setError('Please enter context content');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setValidationErrors(null);

      const context = await contextService.createContext(content, validate);
      navigate(`/contexts/${context.id}`);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'object' && detail.validation) {
        setValidationErrors(detail.validation);
        setError(detail.message || 'Validation failed');
      } else {
        setError(detail || 'Failed to create context');
      }
    } finally {
      setLoading(false);
    }
  };

  const exampleContext = `---
name: my_sales_context
version: 1.0.0
description: Sales data context for revenue analysis
context_type: single_dataset
status: active
tags: ["sales", "revenue"]
category: "Revenue Analytics"

datasets:
  - id: sales_ds
    name: "Sales Data"
    dataset_id: "your-dataset-uuid-here"
    description: "Monthly sales data"

    columns:
      - name: "month"
        business_name: "Sales Month"
        description: "Month of sale"
        data_type: "date"
        nullable: false

      - name: "revenue"
        business_name: "Total Revenue"
        description: "Revenue amount"
        data_type: "decimal"
        nullable: false

metrics:
  - id: total_revenue
    name: "Total Revenue"
    description: "Sum of all revenue"
    expression: "SUM(revenue)"
    data_type: "float"
    format: "$,.2f"

glossary:
  - term: "Revenue"
    definition: "Total monetary value of sales"
    synonyms: ["Sales", "Gross Sales"]
    related_columns: ["revenue"]
---

# Sales Context

## Overview
This context provides metadata for the sales dataset.

## Usage
Use this context for revenue analysis and reporting.
`;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/contexts')}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Contexts
        </button>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Create New Context</h1>
        <p className="text-gray-600">
          Upload a context file or paste YAML content
        </p>
      </div>

      {/* Mode Selector */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setMode('upload')}
            className={`px-4 py-2 rounded-lg font-medium ${
              mode === 'upload'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Upload File
          </button>
          <button
            onClick={() => setMode('paste')}
            className={`px-4 py-2 rounded-lg font-medium ${
              mode === 'paste'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Paste Content
          </button>
        </div>

        {/* Upload Mode */}
        {mode === 'upload' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Context File (.md, .yaml, .yml)
            </label>
            <input
              type="file"
              accept=".md,.yaml,.yml"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {file && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </p>
            )}
          </div>
        )}

        {/* Paste Mode */}
        {mode === 'paste' && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Context Content (YAML + Markdown)
              </label>
              <button
                onClick={() => setContent(exampleContext)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Load Example
              </button>
            </div>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste your context file content here..."
              className="w-full h-96 px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="mt-2 text-sm text-gray-500">
              {content.length} characters
            </p>
          </div>
        )}

        {/* Validation Checkbox */}
        <div className="mt-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={validate}
              onChange={(e) => setValidate(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              Validate context file (recommended)
            </span>
          </label>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}

        {/* Validation Errors */}
        {validationErrors && (
          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-semibold text-yellow-800 mb-2">Validation Issues:</h3>

            {validationErrors.errors && validationErrors.errors.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-semibold text-red-700 mb-1">
                  Errors ({validationErrors.errors.length}):
                </p>
                <ul className="list-disc list-inside space-y-1">
                  {validationErrors.errors.map((err: any, idx: number) => (
                    <li key={idx} className="text-sm text-red-700">
                      {err.message} {err.field && `(${err.field})`}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {validationErrors.warnings && validationErrors.warnings.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-yellow-700 mb-1">
                  Warnings ({validationErrors.warnings.length}):
                </p>
                <ul className="list-disc list-inside space-y-1">
                  {validationErrors.warnings.map((warn: any, idx: number) => (
                    <li key={idx} className="text-sm text-yellow-700">
                      {warn.message} {warn.field && `(${warn.field})`}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Submit Button */}
        <div className="mt-6 flex space-x-4">
          <button
            onClick={mode === 'upload' ? handleUpload : handleCreate}
            disabled={loading || (mode === 'upload' && !file) || (mode === 'paste' && !content.trim())}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center"
          >
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            )}
            {loading ? 'Creating...' : 'Create Context'}
          </button>
          <button
            onClick={() => navigate('/contexts')}
            className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">Context File Format</h3>
        <p className="text-sm text-blue-800 mb-3">
          Context files use YAML frontmatter (between ---) followed by Markdown documentation.
        </p>
        <div className="text-sm text-blue-900">
          <p className="font-semibold mb-1">Required fields:</p>
          <ul className="list-disc list-inside ml-2 space-y-1">
            <li>name - Context identifier</li>
            <li>version - Semantic version (e.g., "1.0.0")</li>
            <li>description - Brief description</li>
            <li>datasets - Array of dataset definitions</li>
          </ul>
        </div>
        <div className="mt-3 text-sm">
          <a
            href="https://github.com/your-repo/context-examples"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-700 hover:text-blue-900 underline"
          >
            View example context files →
          </a>
        </div>
      </div>
    </div>
  );
};

export default ContextCreate;
