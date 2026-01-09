declare module 'pdfjs-dist/build/pdf.mjs' {
  // Minimal type surface to satisfy TS when importing ESM entry
  // For richer types, consume from 'pdfjs-dist/types/src/pdf'
  export const GlobalWorkerOptions: { workerSrc: string };
  export function getDocument(
    src: string | {
      url?: string;
      data?: ArrayBuffer | Uint8Array;
      disableStream?: boolean;
      disableAutoFetch?: boolean;
    }
  ): { promise: Promise<any> };
}
