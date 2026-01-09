'use client';

import { useState, useEffect } from 'react';
import { X, Download, Loader2 } from 'lucide-react';
import mammoth from 'mammoth';

interface WordPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentUrl: string;
  fileName: string;
  onDownload: () => void;
}

export default function WordPreviewModal({
  isOpen,
  onClose,
  documentUrl,
  fileName,
  onDownload
}: WordPreviewModalProps) {
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const loadDocument = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Fetch the Word document
        const response = await fetch(documentUrl);
        if (!response.ok) {
          throw new Error('Failed to load document');
        }

        // Convert to ArrayBuffer
        const arrayBuffer = await response.arrayBuffer();

        // Convert Word to HTML using mammoth
        const result = await mammoth.convertToHtml({ arrayBuffer });
        setHtmlContent(result.value);

        // Log any warnings
        if (result.messages.length > 0) {
          console.warn('Mammoth conversion warnings:', result.messages);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load document');
      } finally {
        setIsLoading(false);
      }
    };

    loadDocument();
  }, [isOpen, documentUrl]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Document Preview</h2>
            <p className="text-sm text-gray-500">{fileName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6 bg-gray-50">
          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-8 w-8 text-m4l-blue animate-spin" />
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-red-600 font-medium mb-2">Failed to load document</p>
                <p className="text-sm text-gray-500">{error}</p>
              </div>
            </div>
          )}

          {!isLoading && !error && (
            <div className="bg-white rounded-lg shadow-sm p-8 max-w-4xl mx-auto">
              <div 
                className="prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: htmlContent }}
                style={{
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                  lineHeight: '1.6',
                }}
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-white flex justify-between items-center">
          <p className="text-sm text-gray-500">
            Preview only - Download to edit
          </p>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Close
            </button>
            <button
              onClick={onDownload}
              className="px-4 py-2 bg-m4l-orange text-white rounded-lg hover:bg-orange-600 transition-colors flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Download Word Document
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
