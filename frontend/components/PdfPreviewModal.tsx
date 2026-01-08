'use client';

import { X, Download, FileCheck } from 'lucide-react';
import { useState } from 'react';

interface PdfPreviewModalProps {
  pdfUrl: string;
  onClose: () => void;
  onFlatten: () => Promise<void>;
}

export default function PdfPreviewModal({ pdfUrl, onClose, onFlatten }: PdfPreviewModalProps) {
  const [isFlattening, setIsFlattening] = useState(false);
  const [flattenedPdfUrl, setFlattenedPdfUrl] = useState<string | null>(null);

  const handleFlatten = async () => {
    setIsFlattening(true);
    try {
      await onFlatten();
      // TODO: Get flattened PDF URL from backend
      setFlattenedPdfUrl('/mock-flattened.pdf');
    } catch (error) {
      console.error('Flattening failed:', error);
    } finally {
      setIsFlattening(false);
    }
  };

  const handleDownload = () => {
    const downloadUrl = flattenedPdfUrl || pdfUrl;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = flattenedPdfUrl ? 'a3-form-flattened.pdf' : 'a3-form-editable.pdf';
    link.click();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-bold text-m4l-blue">
              {flattenedPdfUrl ? 'Flattened PDF Preview' : 'Edit PDF Form'}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {flattenedPdfUrl 
                ? 'PDF fields are now non-editable. Download to save.' 
                : 'Review and edit the form fields, then flatten to finalize.'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="h-6 w-6 text-gray-600" />
          </button>
        </div>

        {/* PDF Viewer */}
        <div className="flex-1 p-4 bg-gray-100 overflow-hidden">
          {(pdfUrl.startsWith('http') || pdfUrl.startsWith('blob:') || pdfUrl.startsWith('data:')) ? (
            <iframe
              src={flattenedPdfUrl || pdfUrl}
              className="w-full h-full rounded-lg border-2 border-gray-300 bg-white"
              title="PDF Preview"
            />
          ) : (
            <div className="w-full h-full rounded-lg border-2 border-gray-300 bg-white flex items-center justify-center">
              <div className="text-center p-8">
                <FileCheck className="h-16 w-16 text-m4l-blue mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-m4l-blue mb-2">PDF Preview</h3>
                <p className="text-gray-600 mb-4">
                  Your processed A3 form will appear here for editing.
                </p>
                <p className="text-sm text-gray-500">
                  (Demo mode - Connect to backend to view actual PDF)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between gap-4">
            <div className="text-sm text-gray-600">
              {flattenedPdfUrl ? (
                <span className="flex items-center gap-2 text-green-700 font-medium">
                  <FileCheck className="h-4 w-4" />
                  PDF has been flattened
                </span>
              ) : (
                <span>Edit the form fields in the PDF above before flattening</span>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
              >
                Close
              </button>

              {!flattenedPdfUrl ? (
                <button
                  onClick={handleFlatten}
                  disabled={isFlattening}
                  className="px-6 py-2 bg-m4l-blue text-white rounded-lg hover:bg-blue-800 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isFlattening ? (
                    <>
                      <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Flattening...
                    </>
                  ) : (
                    <>
                      <FileCheck className="h-5 w-5" />
                      Flatten PDF
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={handleDownload}
                  className="px-6 py-2 bg-m4l-orange text-white rounded-lg hover:bg-orange-600 transition-colors flex items-center gap-2"
                >
                  <Download className="h-5 w-5" />
                  Download Flattened PDF
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
