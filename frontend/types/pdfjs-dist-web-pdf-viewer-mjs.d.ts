declare module 'pdfjs-dist/web/pdf_viewer.mjs' {
  export class EventBus {
    constructor();
    on(eventName: string, listener: (...args: any[]) => void): void;
    off(eventName: string, listener: (...args: any[]) => void): void;
    dispatch(eventName: string, data?: any): void;
  }
  export class PDFLinkService {
    constructor(options?: { eventBus?: EventBus });
    setDocument(pdfDocument: any | null): void;
    setViewer(viewer: any): void;
  }
  export class PDFViewer {
    constructor(options: {
      container: HTMLElement;
      eventBus?: EventBus;
      removePageBorders?: boolean;
    });
    setDocument(pdfDocument: any | null): void;
  }
}
