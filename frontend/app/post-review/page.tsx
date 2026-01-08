'use client';

import { useState } from 'react';
import { Upload, FileText, CheckCircle2, Settings, Download, Eye, AlertCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';

export default function PostReviewPage() {
  // State management
  const [files, setFiles] = useState<{pdf: File | null, word: File | null}>({pdf: null, word: null});
  const [enableOCR, setEnableOCR] = useState(true);
  const [createBackup, setCreateBackup] = useState(true);
  const [preserveFormatting, setPreserveFormatting] = useState(true);
  const [showPreview, setShowPreview] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Combined dropzone for both PDF and Word files
  const {
    getRootProps,
    getInputProps,
    isDragActive
  } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length === 0) return;

      // Auto-detect which file is PDF and which is Word
      let pdfFile: File | null = null;
      let wordFile: File | null = null;

      acceptedFiles.forEach(file => {
        const ext = file.name.toLowerCase();
        if (ext.endsWith('.pdf')) {
          pdfFile = file;
        } else if (ext.endsWith('.docx') || ext.endsWith('.doc')) {
          wordFile = file;
        }
      });

      // Merge with existing files (allow replacing individual files)
      setFiles(prev => ({
        pdf: pdfFile || prev.pdf,
        word: wordFile || prev.word
      }));
      setError(null);
      
      // Show success toast
      if (pdfFile && wordFile) {
        toast.success('Both files uploaded successfully!');
      } else if (pdfFile) {
        toast.success('PDF file uploaded!');
      } else if (wordFile) {
        toast.success('Word document uploaded!');
      }
    },
    onDropRejected: (fileRejections) => {
      const rejection = fileRejections[0];
      if (rejection.errors[0].code === 'file-too-large') {
        const errorMsg = 'Files must be less than 50MB each';
        setError(errorMsg);
        toast.error(errorMsg);
      } else {
        const errorMsg = 'Please upload valid PDF and Word documents';
        setError(errorMsg);
        toast.error(errorMsg);
      }
    }
  });

  const handleProcess = async () => {
    if (!files.pdf || !files.word) {
      const errorMsg = 'Please upload both PDF (annotations) and Word document before processing';
      setError(errorMsg);
      toast.error(errorMsg);
      return;
    }

    setIsProcessing(true);
    setProcessingStep(0);
    setError(null);

    const toastId = toast.loading('Processing documents...');

    try {
      // Simulate processing steps
      const steps = [
        'Extracting PDF sections...',
        'Running OCR on annotations...',
        'Analyzing changes...',
        'Applying modifications to Word document...',
        'Finalizing document...'
      ];

      for (let i = 0; i < steps.length; i++) {
        setProcessingStep(i);
        toast.loading(steps[i], { id: toastId });
        await new Promise(resolve => setTimeout(resolve, 1500));
      }

      // Mock results
      setResults({
        sectionsProcessed: 18,
        changesDetected: 24,
        modificationsApplied: 22,
        processingTime: '12.4s',
        outputFile: `${files.word!.name.replace('.docx', '').replace('.doc', '')}_updated.docx`
      });

      toast.success('Documents processed successfully!', { id: toastId });
    } catch (err) {
      const errorMsg = 'Processing failed. Please try again.';
      setError(errorMsg);
      toast.error(errorMsg, { id: toastId });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setFiles({pdf: null, word: null});
    setResults(null);
    setError(null);
    setProcessingStep(0);
  };

  return (
    <main className="flex-1 overflow-y-auto">
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-m4l-blue mb-2">Post Review Document Processor</h1>
        <p className="text-gray-600">
          Process handwritten annotations from PDF and apply changes to Word documents
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Upload & Options */}
        <div className="space-y-6">
          {/* Combined Upload Area */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Upload className="h-5 w-5 text-m4l-blue" />
              <h3 className="text-lg font-semibold text-m4l-blue">Upload Documents</h3>
            </div>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-m4l-orange bg-orange-50'
                  : (files.pdf && files.word)
                  ? 'border-green-400 bg-green-50'
                  : 'border-gray-300 hover:border-m4l-blue'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              
              {(files.pdf || files.word) ? (
                <div className="space-y-3">
                  <p className="text-sm font-medium text-gray-700 mb-2">Uploaded Files:</p>
                  
                  {files.pdf && (
                    <div className="bg-white border border-green-300 rounded-lg p-3 flex items-center gap-3">
                      <FileText className="h-5 w-5 text-red-600 flex-shrink-0" />
                      <div className="flex-1 text-left">
                        <p className="text-sm font-medium text-gray-900">{files.pdf.name}</p>
                        <p className="text-xs text-gray-500">
                          PDF • {(files.pdf.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    </div>
                  )}
                  
                  {files.word && (
                    <div className="bg-white border border-green-300 rounded-lg p-3 flex items-center gap-3">
                      <FileText className="h-5 w-5 text-blue-600 flex-shrink-0" />
                      <div className="flex-1 text-left">
                        <p className="text-sm font-medium text-gray-900">{files.word.name}</p>
                        <p className="text-xs text-gray-500">
                          Word • {(files.word.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    </div>
                  )}
                  
                  {(!files.pdf || !files.word) && (
                    <p className="text-xs text-orange-600 mt-2">
                      {!files.pdf && 'Still need: PDF with annotations'}
                      {!files.word && !files.pdf && ' and '}
                      {!files.word && 'Word document'}
                    </p>
                  )}
                  
                  <p className="text-xs text-gray-500 mt-3">
                    Drop more files or click to replace
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-sm text-gray-600 mb-2">
                    Drag & drop both files here
                  </p>
                  <p className="text-xs text-gray-500 mb-1">
                    1. PDF with annotations
                  </p>
                  <p className="text-xs text-gray-500 mb-3">
                    2. Word document to be updated
                  </p>
                  <p className="text-xs text-gray-400">
                    or click to browse (max 50MB each)
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Processing Options */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Settings className="h-5 w-5 text-m4l-blue" />
              <h3 className="text-lg font-semibold text-m4l-blue">Processing Options</h3>
            </div>

            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableOCR}
                  onChange={(e) => setEnableOCR(e.target.checked)}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
                <div>
                  <p className="text-sm font-medium text-gray-700">Enable OCR</p>
                  <p className="text-xs text-gray-500">Use GPT-4o Vision to extract handwriting</p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={createBackup}
                  onChange={(e) => setCreateBackup(e.target.checked)}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
                <div>
                  <p className="text-sm font-medium text-gray-700">Create backup</p>
                  <p className="text-xs text-gray-500">Save original document before processing</p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preserveFormatting}
                  onChange={(e) => setPreserveFormatting(e.target.checked)}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
                <div>
                  <p className="text-sm font-medium text-gray-700">Preserve formatting</p>
                  <p className="text-xs text-gray-500">Maintain original document styles</p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showPreview}
                  onChange={(e) => setShowPreview(e.target.checked)}
                  className="w-4 h-4 text-m4l-orange focus:ring-m4l-orange rounded"
                />
                <div>
                  <p className="text-sm font-medium text-gray-700">Show preview</p>
                  <p className="text-xs text-gray-500">Display changes before final save</p>
                </div>
              </label>
            </div>
          </div>

          {/* Process Button */}
          {!isProcessing && !results && (
            <button
              onClick={handleProcess}
              disabled={!files.pdf || !files.word}
              className="w-full bg-m4l-orange text-white px-6 py-3 rounded-lg font-medium hover:bg-orange-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center"
            >
              Process Documents
            </button>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
        </div>

        {/* Right Column - Processing Status & Results */}
        <div className="space-y-6">
          {/* Processing Status */}
          {isProcessing && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-m4l-blue mb-4">Processing Documents</h3>
              
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">Progress</span>
                  <span className="text-gray-900 font-medium">{Math.round(((processingStep + 1) / 5) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-m4l-orange h-2 rounded-full transition-all duration-500"
                    style={{ width: `${((processingStep + 1) / 5) * 100}%` }}
                  />
                </div>
              </div>

              <div className="space-y-3">
                {[
                  'Extracting PDF sections...',
                  'Running OCR on annotations...',
                  'Analyzing changes...',
                  'Applying modifications to Word document...',
                  'Finalizing document...'
                ].map((step, index) => (
                  <div key={index} className="flex items-center gap-3">
                    {index < processingStep ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : index === processingStep ? (
                      <div className="h-5 w-5 border-2 border-m4l-orange border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <div className="h-5 w-5 border-2 border-gray-300 rounded-full" />
                    )}
                    <span className={`text-sm ${
                      index <= processingStep ? 'text-gray-900 font-medium' : 'text-gray-500'
                    }`}>
                      {step}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Results */}
          {results && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <h3 className="text-lg font-semibold text-m4l-blue">Processing Complete</h3>
              </div>

              <div className="space-y-4 mb-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">Sections Processed</p>
                    <p className="text-2xl font-bold text-m4l-blue">{results.sectionsProcessed}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">Changes Detected</p>
                    <p className="text-2xl font-bold text-m4l-blue">{results.changesDetected}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">Modifications Applied</p>
                    <p className="text-2xl font-bold text-green-600">{results.modificationsApplied}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">Processing Time</p>
                    <p className="text-2xl font-bold text-gray-700">{results.processingTime}</p>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-blue-900 mb-1">Output File</p>
                  <p className="text-sm text-blue-700">{results.outputFile}</p>
                </div>
              </div>

              <div className="space-y-3">
                <button
                  className="w-full bg-m4l-blue text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-800 transition-colors flex items-center justify-center gap-2"
                >
                  <Eye className="h-5 w-5" />
                  Preview Changes
                </button>
                <button
                  className="w-full bg-m4l-orange text-white px-4 py-2 rounded-lg font-medium hover:bg-orange-600 transition-colors flex items-center justify-center gap-2"
                >
                  <Download className="h-5 w-5" />
                  Download Updated Document
                </button>
                <button
                  onClick={handleReset}
                  className="w-full bg-[var(--surface)] text-[var(--foreground)] px-4 py-2 rounded-lg font-medium hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                >
                  Process Another Document
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
                  Upload your original Word document and annotated PDF
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  2
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  M4L VL Model extracts handwriting from 18+ PDF sections
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  3
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  AI analyzes changes using 3-strategy text matching
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  4
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  Modifications are applied to your Word document
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  5
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  Download the updated document with all changes applied
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </main>
  );
}
