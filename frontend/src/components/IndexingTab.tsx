import React, { useState } from 'react';
import { Database, Settings, Play, Clock, CheckCircle, XCircle, Zap, Sliders } from 'lucide-react';
import { Document, IndexRequest } from '../types';
import { projectsApi } from '../services/api';
import { useJob } from '../hooks/useJob';

interface IndexingTabProps {
  projectId: number;
  documents: Document[];
  onDocumentsChange: () => void;
}

const IndexingTab: React.FC<IndexingTabProps> = ({ projectId, documents, onDocumentsChange }) => {
  const [indexing, setIndexing] = useState(false);
  const [indexJobId, setIndexJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [indexRequest, setIndexRequest] = useState<IndexRequest>({
    mode: 'auto',
    embedding_model: 'jinaai/jina-embeddings-v3',
    chunk_size: 1000,
    chunk_overlap: 200
  });

  const indexJob = useJob(indexJobId);

  const handleStartIndexing = async () => {
    try {
      setIndexing(true);
      setError(null);
      
      const response = await projectsApi.index(projectId, indexRequest);
      setIndexJobId(response.data.job_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start indexing');
    } finally {
      setIndexing(false);
    }
  };

  const getJobStatus = (job: any) => {
    if (!job) return null;
    
    switch (job.status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'running':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  // Refresh documents when indexing completes
  React.useEffect(() => {
    if (indexJob.job?.status === 'completed') {
      onDocumentsChange();
      setIndexJobId(null);
    }
  }, [indexJob.job?.status, onDocumentsChange]);

  const vectorizedDocs = documents.filter(d => d.is_vectorized);
  const nonVectorizedDocs = documents.filter(d => !d.is_vectorized);
  const smallDocs = documents.filter(d => d.token_count && d.token_count < 7000);

  return (
    <div className="space-y-6">
      {/* Indexing Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mode Selection */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Indexing Configuration
          </h3>
          
          <div className="space-y-4">
            {/* Mode Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Indexing Mode
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="mode"
                    value="auto"
                    checked={indexRequest.mode === 'auto'}
                    onChange={(e) => setIndexRequest({...indexRequest, mode: e.target.value as any})}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500"
                  />
                  <div className="ml-3">
                    <div className="flex items-center">
                      <Zap className="h-4 w-4 text-yellow-500 mr-1" />
                      <span className="text-sm font-medium text-gray-900">Auto Mode</span>
                    </div>
                    <p className="text-xs text-gray-500">
                      Automatically detect embedding model token limits and chunk accordingly
                    </p>
                  </div>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="mode"
                    value="manual"
                    checked={indexRequest.mode === 'manual'}
                    onChange={(e) => setIndexRequest({...indexRequest, mode: e.target.value as any})}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500"
                  />
                  <div className="ml-3">
                    <div className="flex items-center">
                      <Sliders className="h-4 w-4 text-blue-500 mr-1" />
                      <span className="text-sm font-medium text-gray-900">Manual Mode</span>
                    </div>
                    <p className="text-xs text-gray-500">
                      Manually configure chunk size and overlap
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Embedding Model */}
            <div>
              <label htmlFor="embedding_model" className="block text-sm font-medium text-gray-700 mb-2">
                Embedding Model
              </label>
              <select
                id="embedding_model"
                value={indexRequest.embedding_model}
                onChange={(e) => setIndexRequest({...indexRequest, embedding_model: e.target.value as any})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="jinaai/jina-embeddings-v3">Jina Embeddings v3 (8K tokens)</option>
                <option value="qwen3-0.6B">Qwen3 0.6B (2K tokens)</option>
              </select>
            </div>

            {/* Manual Mode Settings */}
            {indexRequest.mode === 'manual' && (
              <div className="space-y-4">
                <div>
                  <label htmlFor="chunk_size" className="block text-sm font-medium text-gray-700 mb-2">
                    Chunk Size (characters)
                  </label>
                  <input
                    type="number"
                    id="chunk_size"
                    value={indexRequest.chunk_size}
                    onChange={(e) => setIndexRequest({...indexRequest, chunk_size: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    min="100"
                    max="10000"
                  />
                </div>
                
                <div>
                  <label htmlFor="chunk_overlap" className="block text-sm font-medium text-gray-700 mb-2">
                    Chunk Overlap (characters)
                  </label>
                  <input
                    type="number"
                    id="chunk_overlap"
                    value={indexRequest.chunk_overlap}
                    onChange={(e) => setIndexRequest({...indexRequest, chunk_overlap: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    min="0"
                    max="1000"
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Indexing Status */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Database className="h-5 w-5 mr-2" />
            Indexing Status
          </h3>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-900">{documents.length}</div>
                <div className="text-sm text-gray-500">Total Documents</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{vectorizedDocs.length}</div>
                <div className="text-sm text-gray-500">Vectorized</div>
              </div>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{smallDocs.length}</div>
              <div className="text-sm text-gray-500">Small Documents (&lt;7K tokens)</div>
              <div className="text-xs text-gray-400 mt-1">
                Will be stored as raw content without vectorization
              </div>
            </div>

            <button
              onClick={handleStartIndexing}
              disabled={indexing || documents.length === 0 || !!indexJobId}
              className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <Play className="h-5 w-5" />
              <span>
                {indexing ? 'Starting...' : indexJobId ? 'Indexing in Progress' : 'Start Indexing'}
              </span>
            </button>

            {/* Index Job Status */}
            {indexJob.job && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getJobStatus(indexJob.job)}
                    <span className="text-sm font-medium">
                      {indexJob.job.status === 'running' ? 'Indexing documents...' : 
                       indexJob.job.status === 'completed' ? 'Indexing completed' :
                       indexJob.job.status === 'failed' ? 'Indexing failed' : 'Indexing pending'}
                    </span>
                  </div>
                  {indexJob.job.status === 'running' && (
                    <span className="text-sm text-gray-500">
                      {Math.round(indexJob.job.progress * 100)}%
                    </span>
                  )}
                </div>
                {indexJob.job.status === 'running' && (
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${indexJob.job.progress * 100}%` }}
                    ></div>
                  </div>
                )}
                {indexJob.job.error_message && (
                  <p className="mt-2 text-sm text-red-600">{indexJob.job.error_message}</p>
                )}
                {indexJob.job.result && indexJob.job.status === 'completed' && (
                  <div className="mt-2 text-sm text-gray-600">
                    <p>Processed {indexJob.job.result.indexed_documents?.length || 0} documents</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Indexing Strategy Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">Indexing Strategy</h4>
        <div className="text-sm text-blue-800 space-y-1">
          <p>• Documents with &lt;7,000 tokens are stored as raw content for direct retrieval</p>
          <p>• Documents with ≥7,000 tokens are chunked and vectorized for semantic search</p>
          <p>• Auto mode automatically adjusts chunk size based on the selected embedding model's token limits</p>
          <p>• Manual mode allows you to fine-tune chunk size and overlap for optimal performance</p>
        </div>
      </div>

      {/* Documents Status */}
      {documents.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Document Status</h3>
          </div>
          
          <div className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                    <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                      <span>{doc.token_count?.toLocaleString() || 'Unknown'} tokens</span>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        doc.is_vectorized 
                          ? 'bg-green-100 text-green-800' 
                          : doc.token_count && doc.token_count < 7000
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {doc.is_vectorized 
                          ? 'Vectorized' 
                          : doc.token_count && doc.token_count < 7000
                          ? 'Raw (Small)'
                          : 'Not Indexed'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-500">
                    {doc.token_count && doc.token_count < 7000 
                      ? 'Will use raw content'
                      : doc.is_vectorized
                      ? 'Vector search enabled'
                      : 'Needs indexing'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default IndexingTab;