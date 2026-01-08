'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Download,
  FileCheck,
  Settings,
  Loader2
} from 'lucide-react';
import PdfPreviewModal from '@/components/PdfPreviewModal';

export default function A3AutomationPage() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState('default');
  const [spellCheckEnabled, setSpellCheckEnabled] = useState(true);
  const [customFieldsEnabled, setCustomFieldsEnabled] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [processedPdfUrl, setProcessedPdfUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showPdfModal, setShowPdfModal] = useState(false);

  // Available templates (will be fetched from backend later)
  const templates = [
    { id: 'default', name: 'Default A3 Template' },
    { id: 'custom', name: 'Custom Field Positions' },
  ];

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setUploadedFile(acceptedFiles[0]);
      setError(null);
      setProcessedPdfUrl(null);
      toast.success(`File uploaded: ${acceptedFiles[0].name}`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
    onDropRejected: (fileRejections) => {
      const rejection = fileRejections[0];
      if (rejection.errors[0].code === 'file-too-large') {
        toast.error('File is too large. Maximum size is 50MB.');
      } else if (rejection.errors[0].code === 'file-invalid-type') {
        toast.error('Invalid file type. Please upload PDF or image files.');
      } else {
        toast.error('File upload failed. Please try again.');
      }
    },
  });

  const handleProcess = async () => {
    if (!uploadedFile) return;

    setProcessing(true);
    setProgress(0);
    setError(null);

    const toastId = toast.loading('Processing A3 form...');

    try {
      // TODO: Replace with actual API call
      // Simulate processing for now
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 5000));
      clearInterval(progressInterval);
      setProgress(100);

      // Mock result
      setProcessedPdfUrl('/mock-processed-a3.pdf');
      setShowPdfModal(true);
      
      toast.success('A3 form processed successfully!', { id: toastId });
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Processing failed';
      setError(errorMessage);
      toast.error(errorMessage, { id: toastId });
    } finally {
      setProcessing(false);
    }
  };

  const handleFlatten = async () => {
    if (!processedPdfUrl) return;

    const toastId = toast.loading('Flattening PDF...');

    try {
      // TODO: Call backend flatten API
      // const response = await fetch('/api/a3/flatten', {
      //   method: 'POST',
      //   body: JSON.stringify({ pdfUrl: processedPdfUrl }),
      // });
      // const data = await response.json();
      
      // For now, just simulate
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success('PDF flattened successfully!', { id: toastId });
    } catch (err) {
      const errorMessage = 'Flattening failed';
      setError(errorMessage);
      toast.error(errorMessage, { id: toastId });
      throw err;
    }
  };

  return (
    <main className="flex-1 overflow-y-auto">
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-m4l-blue mb-2">A3 Form Processing</h1>
          <p className="text-gray-600">
            Extract handwriting from A3 forms and populate PDF templates
          </p>
        </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Upload & Options */}
        <div className="space-y-6">
          {/* File Upload */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Upload className="h-5 w-5 text-m4l-blue" />
              <h3 className="text-lg font-semibold text-m4l-blue">Upload Documents</h3>
            </div>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                ${isDragActive 
                  ? 'border-m4l-orange bg-orange-50' 
                  : 'border-gray-300 hover:border-m4l-orange hover:bg-gray-50'
                }
                ${uploadedFile ? 'bg-green-50 border-green-300' : ''}`}
            >
              <input {...getInputProps()} />
              <div className="flex flex-col items-center gap-4">
                {uploadedFile ? (
                  <FileCheck className="h-12 w-12 text-green-600" />
                ) : (
                  <Upload className="h-12 w-12 text-gray-400" />
                )}
                <div>
                  {uploadedFile ? (
                    <>
                      <p className="text-lg font-medium text-green-700">
                        {uploadedFile.name}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </>
                  ) : (
                    <>
                      <p className="text-lg font-medium text-gray-700">
                        {isDragActive ? 'Drop the file here' : 'Drag & drop A3 form here'}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        or click to browse (PDF, PNG, JPG, TIFF - max 50MB)
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>

            {uploadedFile && (
              <button
                onClick={() => {
                  setUploadedFile(null);
                  setProcessedPdfUrl(null);
                  setError(null);
                }}
                className="mt-4 text-sm text-gray-600 hover:text-gray-800 underline"
              >
                Remove file
              </button>
            )}
          </div>

          {/* Processing Options */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Settings className="h-5 w-5 text-m4l-blue" />
              <h3 className="text-lg font-semibold text-m4l-blue">Processing Options</h3>
            </div>

            <div className="space-y-4">
              <div>
                <label htmlFor="template" className="block text-sm font-medium text-gray-700 mb-2">
                  Template Configuration
                </label>
                <select
                  id="template"
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-m4l-orange focus:border-transparent"
                >
                  {templates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </div>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={spellCheckEnabled}
                  onChange={(e) => setSpellCheckEnabled(e.target.checked)}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
                <span className="text-sm text-gray-700">Enable spell checking</span>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={customFieldsEnabled}
                  onChange={(e) => setCustomFieldsEnabled(e.target.checked)}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
                <span className="text-sm text-gray-700">Use custom field positions</span>
              </label>
            </div>
          </div>

          {/* Process Button */}
          {!processing && !processedPdfUrl && (
            <button
              onClick={handleProcess}
              disabled={!uploadedFile}
              className="w-full bg-m4l-orange hover:bg-orange-600 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              Process A3 Form
            </button>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Right Column - Results & How it works */}
        <div className="space-y-6">
          {/* Processing Status */}
          {processing && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-m4l-blue mb-4">Processing...</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-m4l-orange h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Extracting handwriting and populating PDF template...</span>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {processedPdfUrl && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <h3 className="text-lg font-semibold text-m4l-blue">Processing Complete</h3>
              </div>

              <div className="space-y-3">
                <button
                  onClick={() => setShowPdfModal(true)}
                  className="w-full bg-m4l-blue hover:bg-blue-800 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <FileText className="h-5 w-5" />
                  View/Edit PDF
                </button>

                <button
                  onClick={() => {
                    setUploadedFile(null);
                    setProcessedPdfUrl(null);
                    setProgress(0);
                  }}
                  className="w-full bg-[var(--surface)] hover:bg-[rgba(255,255,255,0.02)] text-[var(--foreground)] font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Process Another Form
                </button>
              </div>
            </div>
          )}

          {/* How it works */}
          <div className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm">
            <h4 className="text-lg font-bold text-m4l-blue mb-4">How it works</h4>
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  1
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  Upload your handwritten A3 financial planning form
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  2
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  Select template and configure options
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  3
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  M4L VL Model extracts handwriting from each section
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  4
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  Review and edit the populated PDF if needed
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  5
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  Flatten the PDF to make fields non-editable (final step)
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

      {/* PDF Preview Modal */}
      {showPdfModal && processedPdfUrl && (
        <PdfPreviewModal
          pdfUrl={processedPdfUrl}
          onClose={() => setShowPdfModal(false)}
          onFlatten={handleFlatten}
        />
      )}
    </main>
  );
}
