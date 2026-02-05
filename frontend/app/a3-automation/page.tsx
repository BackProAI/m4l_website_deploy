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
  Loader2
} from 'lucide-react';
import PdfPreviewModal from '@/components/PdfPreviewModal';

export default function A3AutomationPage() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
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
      const API_BASE = process.env.NEXT_PUBLIC_A3_API || '';
      const processUrl = (API_BASE ? API_BASE : '') + '/api/a3/process';

      const form = new FormData();
      form.append('file', uploadedFile);

      // Start processing - returns immediately with job ID
      const resp = await fetch(processUrl, {
        method: 'POST',
        body: form,
      });

      if (!resp.ok) {
        let msg = `Processing failed: ${resp.status}`;
        try { const j = await resp.json(); if (j && j.detail) msg = j.detail; } catch (_) {}
        throw new Error(msg);
      }

      const { jobId } = await resp.json();
      if (!jobId) throw new Error('No job ID returned');

      // Poll for status
      const statusUrl = (API_BASE ? API_BASE : '') + `/api/a3/status/${jobId}`;
      let attempts = 0;
      const maxAttempts = 120; // 4 minutes max (2 second intervals)

      const pollStatus = async (): Promise<void> => {
        if (attempts >= maxAttempts) {
          throw new Error('Processing timeout - please try again');
        }

        attempts++;
        const statusResp = await fetch(statusUrl);
        if (!statusResp.ok) throw new Error('Failed to check status');

        const statusData = await statusResp.json();
        
        if (statusData.status === 'completed') {
          const outputPath = statusData?.result?.output_pdf_path || statusData?.result?.output_pdf || null;
          if (!outputPath) throw new Error('Processing did not return processed PDF');

          let pdfUrl = outputPath;
          if (API_BASE && pdfUrl.startsWith('/')) pdfUrl = API_BASE.replace(/\/$/, '') + pdfUrl;

          setProcessedPdfUrl(pdfUrl);
          setShowPdfModal(true);
          setProgress(100);
          toast.success('A3 form processed successfully!', { id: toastId });
        } else if (statusData.status === 'failed') {
          throw new Error(statusData.error || 'Processing failed');
        } else {
          // Still processing - update progress and poll again
          const progressPercent = Math.min(95, (attempts / maxAttempts) * 100);
          setProgress(progressPercent);
          await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
          await pollStatus(); // Recursive poll
        }
      };

      await pollStatus();
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Processing failed';
      setError(errorMessage);
      toast.error(errorMessage, { id: toastId });
    } finally {
      setProcessing(false);
    }
  };

  const handleFlatten = async (editedPdfFile: File): Promise<string> => {
    if (!editedPdfFile || editedPdfFile.type !== 'application/pdf') {
      throw new Error('Invalid PDF file');
    }

    const toastId = toast.loading('Flattening PDF...');

    try {
      const form = new FormData();
      form.append('file', editedPdfFile);

      const API_BASE = process.env.NEXT_PUBLIC_A3_API || '';
      const flattenUrl = (API_BASE ? API_BASE : '') + '/api/a3/flatten';

      const uploadResp = await fetch(flattenUrl, {
        method: 'POST',
        body: form,
      });

      if (!uploadResp.ok) {
        let msg = `Flatten failed: ${uploadResp.status}`;
        try {
          const j = await uploadResp.json();
          if (j && j.detail) msg = String(j.detail);
        } catch (_) {}
        throw new Error(msg);
      }

      const result = await uploadResp.json();
      const downloadUrl = result?.downloadUrl || null;
      if (!downloadUrl) throw new Error('Flatten did not return download URL');

      toast.success('PDF flattened successfully!', { id: toastId });

      // For inline preview in the modal, use the `/view/{filename}` endpoint
      const fileName = downloadUrl.split('/').pop() || '';
      let previewUrl = `/view/${fileName}`;
      if (API_BASE) {
        previewUrl = API_BASE.replace(/\/$/, '') + previewUrl;
      }
      return previewUrl;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Flatten failed';
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

      {/* PDF Preview Modal with Instructions Box */}
      {showPdfModal && processedPdfUrl && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="flex gap-4 max-w-[1600px] w-full h-[90vh]">
            {/* Modal - Left Side */}
            <div className="flex-1">
              <PdfPreviewModal
                pdfUrl={processedPdfUrl}
                onClose={() => setShowPdfModal(false)}
                onFlatten={handleFlatten}
              />
            </div>
            
            {/* Instructions Box - Right Side */}
            <div className="w-80 bg-white rounded-xl shadow-2xl p-6 flex flex-col">
              <div className="flex items-start gap-3 mb-4">
                <svg className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="font-bold text-gray-900 text-lg">How to Edit & Flatten</h3>
              </div>
              
              <div className="flex-1 overflow-y-auto">
                <ol className="space-y-4 text-sm text-gray-700">
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 font-semibold flex items-center justify-center text-xs">1</span>
                    <span className="pt-0.5">Make your edits in the PDF viewer</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 font-semibold flex items-center justify-center text-xs">2</span>
                    <span className="pt-0.5">Click the download button in the PDF toolbar and select <strong>"With your changes"</strong></span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 font-semibold flex items-center justify-center text-xs">3</span>
                    <span className="pt-0.5">Save the edited PDF to your computer</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 font-semibold flex items-center justify-center text-xs">4</span>
                    <span className="pt-0.5">Click the <strong>"Flatten PDF"</strong> button in the modal</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 font-semibold flex items-center justify-center text-xs">5</span>
                    <span className="pt-0.5">Upload the edited PDF you just downloaded</span>
                  </li>
                </ol>
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                  💡 Tip: The browser's PDF editor lets you fill forms directly
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
