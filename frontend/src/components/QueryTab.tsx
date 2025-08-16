import React, { useState } from 'react';
import { Search, MessageCircle, Star, Clock, FileText, Database } from 'lucide-react';
import { Document, QueryRequest, QueryResponse } from '../types';
import { projectsApi } from '../services/api';

interface QueryTabProps {
  projectId: number;
  documents: Document[];
}

const QueryTab: React.FC<QueryTabProps> = ({ projectId, documents }) => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [queryHistory, setQueryHistory] = useState<Array<{query: string, timestamp: Date, results: number}>>([]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setSearching(true);
      setError(null);
      
      const queryRequest: QueryRequest = {
        query: query.trim(),
        top_k: topK,
        include_metadata: includeMetadata
      };
      
      const response = await projectsApi.query(projectId, queryRequest);
      setResults(response.data);
      
      // Add to query history
      setQueryHistory(prev => [
        { query: query.trim(), timestamp: new Date(), results: response.data.results.length },
        ...prev.slice(0, 9) // Keep last 10 queries
      ]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setSearching(false);
    }
  };

  const handleExampleQuery = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  const vectorizedDocs = documents.filter(d => d.is_vectorized);
  const nonVectorizedDocs = documents.filter(d => !d.is_vectorized);

  const exampleQueries = [
    "What is the main topic discussed?",
    "Summarize the key findings",
    "What are the important conclusions?",
    "Explain the methodology used",
    "List the main recommendations"
  ];

  return (
    <div className="space-y-6">
      {/* Search Interface */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Search className="h-5 w-5 mr-2" />
          Query Test Interface
        </h3>
        
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="relative">
              <input
                type="text"
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Enter your search query..."
                required
              />
              <button
                type="submit"
                disabled={searching || !query.trim() || documents.length === 0}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary-600 text-white p-2 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Search className="h-4 w-4" />
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="top_k" className="block text-sm font-medium text-gray-700 mb-2">
                Number of Results
              </label>
              <select
                id="top_k"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value={3}>3 results</option>
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
              </select>
            </div>
            
            <div className="flex items-center">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeMetadata}
                  onChange={(e) => setIncludeMetadata(e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Include metadata</span>
              </label>
            </div>
          </div>
        </form>

        {/* Example Queries */}
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Example queries:</p>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleQuery(example)}
                className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded-full hover:bg-gray-200 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Search Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-gray-400 mr-3" />
            <div>
              <div className="text-lg font-semibold text-gray-900">{documents.length}</div>
              <div className="text-sm text-gray-500">Total Documents</div>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center">
            <Database className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <div className="text-lg font-semibold text-gray-900">{vectorizedDocs.length}</div>
              <div className="text-sm text-gray-500">Vector Search Ready</div>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <div className="text-lg font-semibold text-gray-900">{nonVectorizedDocs.length}</div>
              <div className="text-sm text-gray-500">Raw Content Only</div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Search Results */}
      {results && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">
                Search Results for "{results.query}"
              </h3>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span className={`px-2 py-1 rounded-full text-xs ${
                  results.is_vectorized 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {results.is_vectorized ? 'Vector Search' : 'Raw Content'}
                </span>
                <span>{results.total_results} results</span>
              </div>
            </div>
          </div>
          
          {results.results.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p>No results found for your query</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {results.results.map((result, index) => (
                <div key={index} className="p-6">
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="font-medium text-gray-900">Result {index + 1}</h4>
                    {result.score !== undefined && (
                      <div className="flex items-center text-sm text-gray-500">
                        <Star className="h-4 w-4 mr-1" />
                        <span>{(result.score * 100).toFixed(1)}% match</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4 mb-3">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                      {result.content}
                    </pre>
                  </div>
                  
                  {result.metadata && includeMetadata && (
                    <div className="text-xs text-gray-500">
                      <details className="cursor-pointer">
                        <summary className="font-medium hover:text-gray-700">Metadata</summary>
                        <pre className="mt-2 bg-gray-100 rounded p-2 overflow-x-auto">
                          {JSON.stringify(result.metadata, null, 2)}
                        </pre>
                      </details>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Query History */}
      {queryHistory.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              Recent Queries
            </h3>
          </div>
          
          <div className="divide-y divide-gray-200">
            {queryHistory.map((item, index) => (
              <div key={index} className="p-4 hover:bg-gray-50">
                <div className="flex justify-between items-center">
                  <button
                    onClick={() => setQuery(item.query)}
                    className="text-left flex-1 text-sm text-gray-900 hover:text-primary-600 transition-colors"
                  >
                    {item.query}
                  </button>
                  <div className="flex items-center space-x-3 text-xs text-gray-500">
                    <span>{item.results} results</span>
                    <span>{item.timestamp.toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">Search Tips</h4>
        <div className="text-sm text-blue-800 space-y-1">
          <p>• <strong>Vector Search:</strong> For documents ≥7,000 tokens, semantic similarity search is used</p>
          <p>• <strong>Raw Content:</strong> For documents &lt;7,000 tokens, direct content matching is used</p>
          <p>• Use natural language queries for better semantic matching</p>
          <p>• Try different phrasings if you don't get the expected results</p>
          <p>• Adjust the number of results to see more or fewer matches</p>
        </div>
      </div>

      {/* No Documents Warning */}
      {documents.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <MessageCircle className="h-5 w-5 text-yellow-600 mr-2" />
            <p className="text-yellow-800">
              No documents available for querying. Upload and parse documents first.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryTab;