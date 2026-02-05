'use client';

import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import { GlobalWorkerOptions, getDocument } from 'pdfjs-dist/build/pdf.mjs';
import type { PDFDocumentProxy } from 'pdfjs-dist';
// Minimal runtime viewer stack from PDF.js
import { EventBus, PDFViewer, PDFLinkService } from 'pdfjs-dist/web/pdf_viewer.mjs';
// Required viewer CSS for layout of pages/annotation layers
import 'pdfjs-dist/web/pdf_viewer.css';

// Use the worker from public to avoid version string coupling
GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';

export interface PdfJsViewerHandle {
  saveUpdatedPdf: () => Promise<Uint8Array>;
  getFormData: () => Promise<Record<string, string>>;
}

interface PdfJsViewerProps {
  pdfUrl: string;
  onReady?: (numPages: number) => void;
  // Control initial zoom. Defaults to 'page-width' for better readability in modal.
  initialScale?: 'page-fit' | 'page-width' | 'auto' | number;
}

const PdfJsViewer = forwardRef<PdfJsViewerHandle, PdfJsViewerProps>(function PdfJsViewer(
  { pdfUrl, onReady, initialScale = 'page-width' },
  ref
) {
  const outerContainerRef = useRef<HTMLDivElement | null>(null);
  const innerViewerRef = useRef<HTMLDivElement | null>(null);
  const eventBusRef = useRef<EventBus | null>(null);
  const linkServiceRef = useRef<PDFLinkService | null>(null);
  const viewerRef = useRef<PDFViewer | null>(null);
  const pdfDocRef = useRef<PDFDocumentProxy | null>(null);

  useImperativeHandle(ref, () => ({
    async saveUpdatedPdf() {
      const pdfDoc = pdfDocRef.current;
      if (!pdfDoc) throw new Error('PDF not loaded');
      const data = await pdfDoc.saveDocument();
      return data; // Uint8Array
    },
    async getFormData() {
      const pdfDoc = pdfDocRef.current;
      if (!pdfDoc) return {};
      const formData: Record<string, string> = {};
      for (let i = 1; i <= pdfDoc.numPages; i++) {
        const page = await pdfDoc.getPage(i);
        const annotations = await page.getAnnotations();
        for (const a of annotations) {
          // Prefer annotationStorage value if present
          const id = (a as any).id as string | undefined;
          const name = (a as any).fieldName as string | undefined;
          if (!name) continue;
          let value: any = (a as any).fieldValue ?? (a as any).defaultFieldValue ?? '';
          if (id && pdfDoc.annotationStorage) {
            const stored = pdfDoc.annotationStorage.getRawValue(id);
            if (stored && stored.value !== undefined && stored.value !== null) {
              value = stored.value;
            }
          }
          if (value !== undefined && value !== null && value !== '') {
            formData[name] = String(value);
          }
        }
      }
      return formData;
    },
  }));

  useEffect(() => {
    let cancelled = false;
    async function setup() {
      try {
        const loadingTask = getDocument({ url: pdfUrl });
        const pdfDoc = await loadingTask.promise;
        if (cancelled) return;
        pdfDocRef.current = pdfDoc;

        const eventBus = new EventBus();
        eventBusRef.current = eventBus;
        const linkService = new PDFLinkService({ eventBus });
        linkServiceRef.current = linkService;

        const outer = outerContainerRef.current!;
        const inner = innerViewerRef.current!;

        // PDFViewer expects the scrollable container with a child 
        // element (usually class "pdfViewer") where pages are rendered.
        const viewer = new PDFViewer({
          container: outer,
          viewer: inner,
          removePageBorders: true,
          eventBus,
          linkService,
          // Ensure interactive form fields are enabled so edits persist in annotationStorage
          renderInteractiveForms: true,
          // Note: PDFViewer requires the container to be absolutely positioned.
        } as any);
        viewerRef.current = viewer;
        linkService.setViewer(viewer);

        // Ensure the initial scale fits the page within the modal.
        eventBus.on('pagesinit', () => {
          try {
            // Options: 'page-fit', 'page-width', 'auto' or a numeric scale.
            if (typeof initialScale === 'number') {
              (viewer as any).currentScale = initialScale;
            } else {
              (viewer as any).currentScaleValue = initialScale;
            }
          } catch {}
        });

        // Set the document
        viewer.setDocument(pdfDoc);
        linkService.setDocument(pdfDoc);

        onReady?.(pdfDoc.numPages);
      } catch (e) {
        console.error('[PdfJsViewer] failed to initialize', e);
      }
    }
    setup();
    return () => {
      cancelled = true;
      try {
        viewerRef.current?.setDocument(null);
        linkServiceRef.current?.setDocument(null);
        pdfDocRef.current = null;
      } catch {}
    };
  }, [pdfUrl, onReady]);

  return (
    <div
      className="w-full h-full overflow-auto"
      ref={outerContainerRef}
      // PDF.js PDFViewer requires the container to be absolutely positioned
      // (see web/pdf_viewer.js). Fill the parent with inset: 0.
      style={{ position: 'absolute', inset: 0 }}
    >
      <div className="pdfViewer" ref={innerViewerRef} />
    </div>
  );
});

export default PdfJsViewer;
