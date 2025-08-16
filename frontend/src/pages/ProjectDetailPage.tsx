import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, FileText, Database, Search, Upload, Globe, Play, Settings } from 'lucide-react';
import { Project, Document } from '../types';
import { projectsApi } from '../services/api';
import ParserTab from '../components/ParserTab';
import IndexingTab from '../components/IndexingTab';
import QueryTab from '../components/QueryTab';

type TabType = 'parser' | 'indexing' | 'query';

const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const projectId = parseInt(id || '0');

  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('parser');

  useEffect(() => {
    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  const fetchProjectData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [projectResponse, documentsResponse] = await Promise.all([
        projectsApi.get(projectId),
        projectsApi.getDocuments(projectId)
      ]);
      
      setProject(projectResponse.data);
      setDocuments(documentsResponse.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch project data');
    } finally {
      setLoading(false);
    }
  };

  const refreshDocuments = async () => {
    try {
      const response = await projectsApi.getDocuments(projectId);
      setDocuments(response.data);
    } catch (err: any) {
      console.error('Failed to refresh documents:', err);
    }
  };

  const tabs = [
    {
      id: 'parser' as TabType,
      name: 'Parser',
      icon: FileText,
      description: 'Upload and parse documents'
    },
    {
      id: 'indexing' as TabType,
      name: 'Indexing',
      icon: Database,
      description: 'Index documents for search'
    },
    {
      id: 'query' as TabType,
      name: 'Query Test',
      icon: Search,
      description: 'Test search queries'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
          <p className="text-red-800">{error || 'Project not found'}</p>
          <Link
            to="/"
            className="mt-4 inline-flex items-center text-primary-600 hover:text-primary-700"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Projects
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center space-x-4 mb-4">
          <Link
            to="/"
            className="flex items-center text-gray-500 hover:text-gray-700 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 mr-1" />
            Projects
          </Link>
        </div>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
            {project.description && (
              <p className="text-gray-600 mt-2">{project.description}</p>
            )}
            <div className="flex items-center space-x-4 mt-4 text-sm text-gray-500">
              <span>Project ID: {project.id}</span>
              <span>•</span>
              <span>{documents.length} documents</span>
              <span>•</span>
              <span>
                {documents.filter(d => d.is_vectorized).length} vectorized
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  isActive
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className={`mr-2 h-5 w-5 ${
                  isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                }`} />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {activeTab === 'parser' && (
          <ParserTab
            projectId={projectId}
            documents={documents}
            onDocumentsChange={refreshDocuments}
          />
        )}
        {activeTab === 'indexing' && (
          <IndexingTab
            projectId={projectId}
            documents={documents}
            onDocumentsChange={refreshDocuments}
          />
        )}
        {activeTab === 'query' && (
          <QueryTab
            projectId={projectId}
            documents={documents}
          />
        )}
      </div>
    </div>
  );
};

export default ProjectDetailPage;