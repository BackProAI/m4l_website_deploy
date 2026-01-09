'use client';

import { useEffect, useRef, useState } from 'react';
import { GlobalWorkerOptions, getDocument } from 'pdfjs-dist/build/pdf.mjs';
import type { PDFDocumentProxy, PDFPageProxy } from 'pdfjs-dist/types/src/pdf';

// Configure PDF.js worker from local public path for reliability
if (typeof window !== 'undefined') {
  GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';
}

interface PdfFormViewerProps {
  pdfUrl: string;
  onFormDataChange?: (formData: Record<string, string>) => void;
}

export default function PdfFormViewer({ pdfUrl, onFormDataChange }: PdfFormViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [pdfDoc, setPdfDoc] = useState<PDFDocumentProxy | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [numPages, setNumPages] = useState(0);
  const [status, setStatus] = useState<string>('Initializing PDF viewer...');
  const [debugMessages, setDebugMessages] = useState<string[]>([]);

  const logDebug = (msg: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugMessages(prev => [...prev.slice(-99), `[${timestamp}] ${msg}`]);
  };

  // Update parent when form data changes
  useEffect(() => {
    if (onFormDataChange) {
      onFormDataChange(formData);
    }
  }, [formData, onFormDataChange]);

  useEffect(() => {
    let isMounted = true;

    const loadPdf = async () => {
      if (!pdfUrl) return;

      try {
        setLoading(true);
        setError(null);
        setStatus('Fetching PDF...');
        logDebug(`Fetch start: ${pdfUrl}`);

        // Prefer url-based loading (streaming) with CORS; fallback to arrayBuffer on failure
        console.info('[PdfFormViewer] Loading PDF via url:', pdfUrl);
        logDebug('Attempting getDocument({ url })');
        let loadingTask;
        try {
          loadingTask = getDocument({ url: pdfUrl, disableStream: false, disableAutoFetch: false });
        } catch (e) {
          console.warn('[PdfFormViewer] url load failed, falling back to arrayBuffer:', e);
          logDebug(`URL load failed; falling back to arrayBuffer: ${e instanceof Error ? e.message : String(e)}`);
          const response = await fetch(pdfUrl);
          if (!response.ok) throw new Error(`Failed to fetch PDF: ${response.status}`);
          const arrayBuffer = await response.arrayBuffer();
          loadingTask = getDocument({ data: arrayBuffer });
        }
        const pdf = await loadingTask.promise;

        if (!isMounted) return;

        setPdfDoc(pdf);
        setNumPages(pdf.numPages);
        setStatus(`Loaded ${pdf.numPages} page(s). Rendering...`);
        logDebug(`PDF loaded: ${pdf.numPages} pages`);

        // Extract initial form data
        const initialFormData: Record<string, string> = {};
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
          const page = await pdf.getPage(pageNum);
          logDebug(`Render start: page ${pageNum}`);
          const annotations = await page.getAnnotations();
          logDebug(`Page ${pageNum}: ${annotations.length} annotations`);
          
          for (const annotation of annotations) {
            if (annotation.fieldName && annotation.fieldType) {
              const value = annotation.fieldValue || annotation.defaultFieldValue || '';
              if (value) {
                initialFormData[annotation.fieldName] = String(value);
              }
            }
          }
        }

        if (isMounted) {
          setFormData(initialFormData);
          setLoading(false);
          setStatus('PDF rendered');
          logDebug('Render complete for all pages');
        }

      } catch (err) {
        if (isMounted) {
          console.error('Failed to load PDF:', err);
          logDebug(`Error loading PDF: ${err instanceof Error ? err.message : String(err)}`);
          setError(err instanceof Error ? err.message : 'Failed to load PDF');
          setLoading(false);
          setStatus('Error loading PDF');
        }
      }
    };

    loadPdf();

    return () => {
      isMounted = false;
    };
  }, [pdfUrl]);

  // Render PDF pages
  useEffect(() => {
    if (!pdfDoc || !containerRef.current) return;

    const renderPages = async () => {
      const container = containerRef.current;
      if (!container) return;

      // Clear previous content
      container.innerHTML = '';
      logDebug('Cleared previous content; starting page rendering');

      for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
        const page = await pdfDoc.getPage(pageNum);
        await renderPage(page, container, pageNum);
        logDebug(`Render end: page ${pageNum}`);
      }
    };

    renderPages();
  }, [pdfDoc]);

  const renderPage = async (page: PDFPageProxy, container: HTMLElement, pageNum: number) => {
    const viewport = page.getViewport({ scale: 1.5 });
    const dpr = typeof window !== 'undefined' ? Math.max(1, window.devicePixelRatio || 1) : 1;
    logDebug(`Page ${pageNum} viewport: ${Math.round(viewport.width)}x${Math.round(viewport.height)} @scale ${viewport.scale}, dpr=${dpr}`);

    // Create page container
    const pageDiv = document.createElement('div');
    pageDiv.className = 'relative mb-4';
    pageDiv.style.width = `${viewport.width}px`;
    pageDiv.style.height = `${viewport.height}px`;

    // Create canvas for PDF content
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    if (!context) return;

    // Scale canvas for device pixel ratio to ensure crisp rendering
    canvas.width = Math.floor(viewport.width * dpr);
    canvas.height = Math.floor(viewport.height * dpr);
    canvas.className = 'border border-gray-300';
    // Make it obvious if canvas is present but not rendering content
    canvas.style.backgroundColor = '#ffffff';
    // CSS size remains in CSS pixels
    canvas.style.width = `${viewport.width}px`;
    canvas.style.height = `${viewport.height}px`;

    // Render PDF page
    const transform = dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : undefined;
    await page.render({
      canvasContext: context,
      viewport,
      intent: 'display',
      transform,
    }).promise;
    logDebug(`Page ${pageNum} canvas appended: css=${Math.round(viewport.width)}x${Math.round(viewport.height)} px, buffer=${canvas.width}x${canvas.height}`);

    pageDiv.appendChild(canvas);

    // Get annotations (form fields)
    const annotations = await page.getAnnotations();

    // Create form layer
    const formLayer = document.createElement('div');
    formLayer.className = 'absolute top-0 left-0 w-full h-full pointer-events-none';
    formLayer.style.width = `${viewport.width}px`;
    formLayer.style.height = `${viewport.height}px`;

    // Add form fields
    for (const annotation of annotations) {
      if (!annotation.fieldName) continue;

      // Only handle text fields for now
      if (annotation.fieldType === 'Tx') {
        const rect = annotation.rect;
        if (!rect || rect.length < 4) continue;

        // Convert PDF coordinates to viewport coordinates
        const [x1, y1, x2, y2] = viewport.convertToViewportRectangle(rect);

        const input = document.createElement(annotation.multiLine ? 'textarea' : 'input');
        input.className = 'absolute bg-transparent border border-blue-300 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 px-1 pointer-events-auto';
        input.style.left = `${Math.min(x1, x2)}px`;
        input.style.top = `${Math.min(y1, y2)}px`;
        input.style.width = `${Math.abs(x2 - x1)}px`;
        input.style.height = `${Math.abs(y2 - y1)}px`;
        input.style.fontSize = '12px';
        
        if (!annotation.multiLine) {
          (input as HTMLInputElement).type = 'text';
        }

        // Set initial value
        const fieldName = annotation.fieldName;
        if (formData[fieldName]) {
          input.value = formData[fieldName];
        } else if (annotation.fieldValue) {
          input.value = String(annotation.fieldValue);
        }

        // Track changes
        input.addEventListener('input', (e) => {
          const target = e.target as HTMLInputElement | HTMLTextAreaElement;
          setFormData(prev => ({
            ...prev,
            [fieldName]: target.value
          }));
        });

        formLayer.appendChild(input);
      }
    }

    pageDiv.appendChild(formLayer);
    container.appendChild(pageDiv);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          <p className="text-gray-700 text-sm">{status}</p>
          <p className="text-gray-500 text-xs mt-1">If this takes long, the worker may be blocked; rendering will fall back without a worker.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center p-4 max-w-lg">
          <p className="text-red-700 font-semibold mb-2">Failed to load PDF</p>
          <p className="text-gray-700 text-sm break-words">{error}</p>
          <p className="text-gray-500 text-xs mt-2">Check that the URL is accessible and CORS is enabled on the backend.</p>
          <div className="mt-3 text-left bg-black/70 text-white text-xs rounded-md p-2 max-h-40 overflow-auto">
            <div className="font-semibold mb-1">Viewer Debug</div>
            <div>Status: {status}</div>
            <ul className="mt-1 list-disc list-inside">
              {debugMessages.slice(-20).map((m, i) => (
                <li key={i}>{m}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full">
      <div 
        ref={containerRef} 
        className="overflow-auto h-full p-4 bg-gray-100"
        style={{ maxHeight: '100%', minHeight: '50vh' }}
      />
      <div className="absolute bottom-2 right-2 w-80 max-h-48 overflow-auto bg-black/70 text-white text-xs rounded-md p-2 shadow-lg">
        <div className="font-semibold mb-1">Viewer Debug</div>
        <div>Status: {status}</div>
        <div>Pages: {numPages}</div>
        <ul className="mt-1 list-disc list-inside">
          {debugMessages.slice(-20).map((m, i) => (
            <li key={i}>{m}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
