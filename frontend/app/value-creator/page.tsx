'use client';

import { useState } from 'react';
import { Upload, FileText, CheckCircle2, Download, Eye, AlertCircle, TrendingUp } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';

export default function ValueCreatorPage() {
  // State management
  const [files, setFiles] = useState<{pdf: File | null, word: File | null}>({pdf: null, word: null});
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

    const toastId = toast.loading('Uploading documents...');

    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('pdf', files.pdf);
      formData.append('docx', files.word);

      const API_BASE = process.env.NEXT_PUBLIC_A3_API || '';
      const processUrl = (API_BASE ? API_BASE : '') + '/api/value-creator/process';

      // Processing steps for user feedback
      const steps = [
        'Uploading documents...',
        'Parsing PDF and chunking document...',
        'Analysing 10 chunks with M4L VL Model...',
        'Detecting strikethroughs and changes...',
        'Extracting amounts and dates...',
        'Generating Word document...'
      ];

      // Update toast with upload status
      setProcessingStep(0);
      toast.loading(steps[0], { id: toastId });

      // Make API call
      const response = await fetch(processUrl, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorMsg = `Processing failed: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData && errorData.detail) {
            errorMsg = String(errorData.detail);
          }
        } catch (_) {}
        throw new Error(errorMsg);
      }

      const data = await response.json();
      
      // Simulate progress updates for better UX
      for (let i = 1; i < steps.length; i++) {
        setProcessingStep(i);
        toast.loading(steps[i], { id: toastId });
        await new Promise(resolve => setTimeout(resolve, 800));
      }

      // Extract results
      const result = data.result || {};
      const stages = result.stages || {};
      const pdfAnalysis = stages.pdf_analysis || {};
      const wordProcessing = stages.word_processing || {};
      const changes = wordProcessing.changes || {};
      const operationBreakdown = changes.operation_breakdown || {};
      
      // Check if processing was successful
      if (result.status !== 'success') {
        throw new Error(result.error || 'Processing failed');
      }

      // Set results for display
      const sections = wordProcessing.sections || {};
      const strategyBreakdown = changes.strategy_breakdown || {};
      const totalChanges = (strategyBreakdown.exact_matches || 0) + 
                          (strategyBreakdown.similarity_matches || 0) + 
                          (strategyBreakdown.keyword_matches || 0);
      
      setResults({
        chunksProcessed: pdfAnalysis.chunks_processed || 0,
        sectionsProcessed: sections.successful_sections || 0,
        changesApplied: totalChanges,
        finalDocument: result.output_file,
        jobId: data.jobId,
        processingTime: result.processing_time_seconds ? `${result.processing_time_seconds.toFixed(1)}s` : 'N/A',
        outputFile: result.output_file ? result.output_file.split(/[/\\]/).pop() : 'value_creator_output.docx'
      });

      toast.success('Value Creator letter processed successfully!', { id: toastId });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Processing failed. Please try again.';
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

  const handleDownload = () => {
    if (!results?.finalDocument || !results?.jobId) {
      toast.error('No processed document available');
      return;
    }

    // Extract just the filename from the full path
    const fileName = results.finalDocument.split(/[/\\]/).pop() || 'value_creator_output.docx';
    
    // The file is in a subdirectory: outputs/{jobId}/{filename}
    const API_BASE = process.env.NEXT_PUBLIC_A3_API || '';
    const downloadUrl = `${API_BASE}/downloads/${results.jobId}/${fileName}`;
    
    // Create temporary link and trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = fileName;
    link.click();
    
    toast.success('Download started!');
  };

  return (
    <main className="flex-1 overflow-y-auto">
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
        <h1 className="text-3xl font-bold text-m4l-blue mb-2">Value Creator Letter Automation</h1>
        <p className="text-gray-600">
          Parse financial documents, detect changes, and generate updated Word letters
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

          {/* Process Button */}
          {!isProcessing && !results && (
            <button
              onClick={handleProcess}
              disabled={!files.pdf || !files.word}
              className="w-full bg-m4l-orange text-white px-6 py-3 rounded-lg font-medium hover:bg-orange-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center"
            >
              Process Value Creator Letter
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
              <h3 className="text-lg font-semibold text-m4l-blue mb-4">Processing Document</h3>
              
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
                  'Parsing PDF and chunking document...',
                  'Analysing 10 chunks with M4L VL Model...',
                  'Detecting strikethroughs and changes...',
                  'Extracting amounts and dates...',
                  'Generating Word document...'
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
                    <p className="text-xs text-gray-500 mb-1">Chunks Processed</p>
                    <p className="text-2xl font-bold text-m4l-blue">{results.chunksProcessed}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 mb-1">Sections Processed</p>
                    <p className="text-2xl font-bold text-m4l-blue">{results.sectionsProcessed}</p>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-green-900 mb-2">
                    Total Changes: {results.changesApplied}
                  </p>
                  <p className="text-xs text-green-700">
                    Processing completed in {results.processingTime}
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-blue-900 mb-1">Generated Document</p>
                  <p className="text-sm text-blue-700">{results.outputFile}</p>
                </div>
              </div>

              <div className="space-y-3">
                <button
                  onClick={handleDownload}
                  className="w-full bg-m4l-orange text-white px-4 py-2 rounded-lg font-medium hover:bg-orange-600 transition-colors flex items-center justify-center gap-2"
                >
                  <Download className="h-5 w-5" />
                  Download Word Document
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
                  Upload your financial document PDF
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  2
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  Document is parsed and split into 10 strategic chunks
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  3
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  M4L VL Model analyses each chunk for changes and strikethroughs
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  4
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  3-strategy cascading system matches and applies changes
                </p>
              </div>

              <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-7 h-7 bg-m4l-blue text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  5
                </div>
                <p className="text-sm text-gray-700 pt-1">
                  Word document is generated with all detected changes
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
