/**
 * Extract form field data from a PDF file using PDF.js
 */

export async function extractPdfFormData(pdfUrl: string): Promise<Record<string, string>> {
  try {
    // Dynamically import PDF.js to avoid SSR issues
    const pdfjsLib = await import('pdfjs-dist/build/pdf.mjs');
    
    // Set worker to local public file to avoid version mismatches
    pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';

    // Fetch PDF
    const response = await fetch(pdfUrl);
    const arrayBuffer = await response.arrayBuffer();
    
    // Load PDF document
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    
    const formData: Record<string, string> = {};
    
    // Iterate through all pages
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const annotations = await page.getAnnotations();
      
      // Extract form field values
      for (const annotation of annotations) {
        if (annotation.fieldType && annotation.fieldName) {
          const value = annotation.fieldValue || annotation.defaultFieldValue || '';
          if (value) {
            formData[annotation.fieldName] = String(value);
          }
        }
      }
    }
    
    return formData;
  } catch (error) {
    console.error('Failed to extract PDF form data:', error);
    return {};
  }
}
