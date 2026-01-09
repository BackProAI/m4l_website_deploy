'use client';

import React, { useRef, useState } from 'react';
import { X, Upload, FileCheck } from 'lucide-react';

interface PdfPreviewModalProps {
  pdfUrl: string;
  onClose: () => void;
  // onFlatten accepts a File object (the edited PDF uploaded by user) and returns the URL of the flattened PDF
  onFlatten: (editedPdfFile: File) => Promise<string>;
}

function PdfPreviewModal({ pdfUrl, onClose, onFlatten }: PdfPreviewModalProps): JSX.Element {
  const [isFlattening, setIsFlattening] = useState(false);
  const [flattenedPdfUrl, setFlattenedPdfUrl] = useState<string | null>(null);
  const [showUploadZone, setShowUploadZone] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFlattenClick = () => {
    // Show the upload zone instead of trying to flatten directly
    setShowUploadZone(true);
  };

  const handleFileSelect = async (file: File) => {
    if (!file || file.type !== 'application/pdf') {
      alert('Please upload a PDF file');
      return;
    }

    setIsFlattening(true);
    try {
      const flattenedUrl = await onFlatten(file);
      if (flattenedUrl) {
        setFlattenedPdfUrl(flattenedUrl);
        setShowUploadZone(false);
      }
    } catch (error) {
      console.error('Flattening failed:', error);
      alert('Failed to flatten PDF. Please try again.');
    } finally {
      setIsFlattening(false);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDownload = () => {
    let downloadUrl = flattenedPdfUrl;
    if (downloadUrl && downloadUrl.includes('/view/')) {
      downloadUrl = downloadUrl.replace('/view/', '/downloads/');
    }
    const link = document.createElement('a');
    link.href = downloadUrl!;
    link.download = 'a3-form-flattened.pdf';
    link.click();
  };

  return (
    <div className="bg-white rounded-xl shadow-2xl w-full h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div>
          <h2 className="text-xl font-bold text-m4l-blue">
            {flattenedPdfUrl ? 'Flattened PDF Preview' : showUploadZone ? 'Upload Edited PDF' : 'Edit PDF Form'}
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            {flattenedPdfUrl 
              ? 'PDF fields are now non-editable. Download to save.' 
              : showUploadZone
              ? 'Upload the edited PDF you just downloaded to flatten it.'
              : 'Make your edits, then use the browser\'s download button to save "With your changes".'}
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

        {/* Content Area */}
        <div className="flex-1 bg-gray-100 overflow-hidden relative">
          {flattenedPdfUrl ? (
            // Flattened PDF: Show result with native browser toolbar
            <iframe
              src={flattenedPdfUrl}
              className="w-full h-full"
              title="Flattened PDF Preview"
            />
          ) : showUploadZone ? (
            // Upload Zone: Drop edited PDF here
            <div className="flex items-center justify-center h-full p-8">
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`
                  border-4 border-dashed rounded-2xl p-12 w-full max-w-2xl
                  cursor-pointer transition-all duration-200
                  ${isDragging 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                  }
                  ${isFlattening ? 'pointer-events-none opacity-50' : ''}
                `}
              >
                <div className="text-center">
                  {isFlattening ? (
                    <>
                      <div className="h-16 w-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                      <p className="text-xl font-semibold text-gray-700 mb-2">Flattening PDF...</p>
                      <p className="text-gray-500">Please wait while we process your file</p>
                    </>
                  ) : (
                    <>
                      <Upload className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-xl font-semibold text-gray-700 mb-2">
                        Drop your edited PDF here
                      </p>
                      <p className="text-gray-500 mb-4">
                        or click to browse files
                      </p>
                      <div className="text-sm text-gray-400">
                        Supported format: PDF
                      </div>
                    </>
                  )}
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  onChange={handleFileInputChange}
                  className="hidden"
                />
              </div>
            </div>
          ) : (
            // Edit Mode: Native browser PDF viewer (instructions are in separate box outside)
            <iframe
              src={pdfUrl}
              className="w-full h-full"
              title="Edit PDF Form"
            />
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
              ) : showUploadZone ? (
                <span>Upload the edited PDF to continue</span>
              ) : (
                <span>Follow the instructions above to edit and flatten your PDF</span>
              )}
            </div>

            <div className="flex gap-3">
              {showUploadZone && (
                <button
                  onClick={() => setShowUploadZone(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  Back to Edit
                </button>
              )}

              {flattenedPdfUrl ? (
                <button
                  onClick={handleDownload}
                  className="px-6 py-2 bg-m4l-blue text-white rounded-lg hover:bg-blue-800 transition-colors flex items-center gap-2"
                >
                  <Upload className="h-5 w-5 rotate-180" />
                  Download Flattened PDF
                </button>
              ) : !showUploadZone && (
                <button
                  onClick={handleFlattenClick}
                  className="px-6 py-2 bg-m4l-blue text-white rounded-lg hover:bg-blue-800 transition-colors flex items-center gap-2"
                >
                  <FileCheck className="h-5 w-5" />
                  Flatten PDF
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
  );
}

export default PdfPreviewModal;