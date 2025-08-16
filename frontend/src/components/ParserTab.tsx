import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Globe, FileText, Eye, Clock, CheckCircle, XCircle } from 'lucide-react';
import { Document } from '../types';
import { projectsApi } from '../services/api';
import { useJob } from '../hooks/useJob';

interface ParserTabProps {
  projectId: number;
  documents: Document[];
  onDocumentsChange: () => void;
}

const ParserTab: React.FC<ParserTabProps> = ({ projectId, documents, onDocumentsChange }) => {
  const [uploading, setUploading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [uploadJobId, setUploadJobId] = useState<string | null>(null);
  const [scrapeJobId, setScrapeJobId] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uploadJob = useJob(uploadJobId);
  const scrapeJob = useJob(scrapeJobId);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    try {
      setUploading(true);
      setError(null);
      
      const response = await projectsApi.upload(projectId, acceptedFiles);
      setUploadJobId(response.data.job_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  const handleScrapeUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scrapeUrl.trim()) return;

    try {
      setScraping(true);
      setError(null);
      
      const response = await projectsApi.scrape(projectId, { url: scrapeUrl });
      setScrapeJobId(response.data.job_id);
      setScrapeUrl('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to scrape URL');
    } finally {
      setScraping(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    },
    multiple: true,
    disabled: uploading
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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

  // Refresh documents when jobs complete
  React.useEffect(() => {
    if (uploadJob.job?.status === 'completed') {
      onDocumentsChange();
      setUploadJobId(null);
    }
  }, [uploadJob.job?.status, onDocumentsChange]);

  React.useEffect(() => {
    if (scrapeJob.job?.status === 'completed') {
      onDocumentsChange();
      setScrapeJobId(null);
    }
  }, [scrapeJob.job?.status, onDocumentsChange]);

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* File Upload */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Upload className="h-5 w-5 mr-2" />
            Upload Documents
          </h3>
          
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary-400 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            {isDragActive ? (
              <p className="text-primary-600 font-medium">Drop files here...</p>
            ) : (
              <div>
                <p className="text-gray-600 font-medium mb-2">
                  Drag & drop files here, or click to select
                </p>
                <p className="text-sm text-gray-500">
                  Supports: PDF, DOCX, PPTX, TXT, MD, PNG, JPG
                </p>
              </div>
            )}
          </div>

          {/* Upload Job Status */}
          {uploadJob.job && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getJobStatus(uploadJob.job)}
                  <span className="text-sm font-medium">
                    {uploadJob.job.status === 'running' ? 'Processing files...' : 
                     uploadJob.job.status === 'completed' ? 'Upload completed' :
                     uploadJob.job.status === 'failed' ? 'Upload failed' : 'Upload pending'}
                  </span>
                </div>
                {uploadJob.job.status === 'running' && (
                  <span className="text-sm text-gray-500">
                    {Math.round(uploadJob.job.progress * 100)}%
                  </span>
                )}
              </div>
              {uploadJob.job.status === 'running' && (
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadJob.job.progress * 100}%` }}
                  ></div>
                </div>
              )}
              {uploadJob.job.error_message && (
                <p className="mt-2 text-sm text-red-600">{uploadJob.job.error_message}</p>
              )}
            </div>
          )}
        </div>

        {/* URL Scraping */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Globe className="h-5 w-5 mr-2" />
            Scrape URL
          </h3>
          
          <form onSubmit={handleScrapeUrl} className="space-y-4">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                Website URL
              </label>
              <input
                type="url"
                id="url"
                value={scrapeUrl}
                onChange={(e) => setScrapeUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="https://example.com/article"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={scraping || !scrapeUrl.trim()}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {scraping ? 'Scraping...' : 'Scrape Content'}
            </button>
          </form>

          {/* Scrape Job Status */}
          {scrapeJob.job && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2">
                {getJobStatus(scrapeJob.job)}
                <span className="text-sm font-medium">
                  {scrapeJob.job.status === 'running' ? 'Scraping content...' : 
                   scrapeJob.job.status === 'completed' ? 'Scraping completed' :
                   scrapeJob.job.status === 'failed' ? 'Scraping failed' : 'Scraping pending'}
                </span>
              </div>
              {scrapeJob.job.error_message && (
                <p className="mt-2 text-sm text-red-600">{scrapeJob.job.error_message}</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Documents List */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Parsed Documents ({documents.length})
          </h3>
        </div>
        
        {documents.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p>No documents uploaded yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{doc.filename}</h4>
                    <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                      <span>{doc.file_type.toUpperCase()}</span>
                      <span>{formatFileSize(doc.file_size)}</span>
                      {doc.token_count && (
                        <span>{doc.token_count.toLocaleString()} tokens</span>
                      )}
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        doc.is_vectorized 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {doc.is_vectorized ? 'Vectorized' : 'Raw'}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedDocument(doc)}
                    className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 transition-colors"
                  >
                    <Eye className="h-4 w-4" />
                    <span>Preview</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document Preview Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                {selectedDocument.filename}
              </h2>
              <button
                onClick={() => setSelectedDocument(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-96">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                {selectedDocument.raw_content}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParserTab;