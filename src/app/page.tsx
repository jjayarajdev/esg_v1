'use client';

import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import QuestionAnswering from './components/QuestionAnswering';
import ESGDashboard from './components/ESGDashboard';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'document' | 'qa' | 'metrics'>('document');
  const [documentId, setDocumentId] = useState<string | null>(null);

  const handleUploadSuccess = (newDocumentId: string) => {
    setDocumentId(newDocumentId);
    setActiveTab('qa');
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <span className="text-2xl">📊</span>
            ESG AI Analysis Platform
          </h1>
          <p className="mt-2 text-gray-600">
            Powered by LLM & ReactJS
          </p>
        </div>

        {!documentId ? (
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
        ) : (
          <div className="space-y-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                <button
                  onClick={() => setActiveTab('document')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'document'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Document Analysis
                </button>
                <button
                  onClick={() => setActiveTab('qa')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'qa'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  ESG Reports
                </button>
                <button
                  onClick={() => setActiveTab('metrics')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'metrics'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  ESG Performance Dashboard
                </button>
              </nav>
            </div>

            <div className="py-4">
              {activeTab === 'document' && (
                <div className="text-center py-8">
                  <button
                    onClick={() => setDocumentId(null)}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Upload New Document
                  </button>
                </div>
              )}
              {activeTab === 'qa' && documentId && (
                <QuestionAnswering documentId={documentId} />
              )}
              {activeTab === 'metrics' && documentId && (
                <ESGDashboard documentId={documentId} />
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
