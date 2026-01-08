#!/usr/bin/env python3
"""
Document Preprocessor
Handles converting documents to image chunks for analysis
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from PIL import Image
import PyPDF2
from pdf2image import convert_from_path

class DocumentPreprocessor:
    """Preprocesses documents into analyzable chunks"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.chunk_size = config['document']['chunk_size']
        self.overlap = config['document']['overlap']
        self.supported_formats = config['document']['supported_formats']
    
    def process_document(self, input_path: str) -> List[Dict]:
        """
        Process a document into chunks
        
        Args:
            input_path: Path to input document
            
        Returns:
            List of chunk dictionaries with image data and metadata
        """
        file_path = Path(input_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Convert to images if PDF
        if file_path.suffix.lower() == '.pdf':
            images = self._pdf_to_images(input_path)
        else:
            # Load single image
            image = Image.open(input_path)
            images = [np.array(image)]
        
        # Create chunks from all images
        all_chunks = []
        for page_idx, image in enumerate(images):
            page_chunks = self._create_chunks(image, page_idx)
            all_chunks.extend(page_chunks)
        
        self.logger.info(f"Created {len(all_chunks)} chunks from {len(images)} pages")
        return all_chunks
    
    def _pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF to list of images with A4 sizing"""
        try:
            # Try to find local Poppler installation first
            poppler_path = self._find_poppler_path()
            
            # Get target dimensions from config (default to A4: 595x841)
            target_width = self.config.get('document', {}).get('target_width', 595)
            target_height = self.config.get('document', {}).get('target_height', 841)
            resize_to_a4 = self.config.get('document', {}).get('resize_to_a4', True)
            
            if poppler_path:
                # Use pdf2image with local Poppler path
                images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
            else:
                # Try without specifying path (system PATH)
                images = convert_from_path(pdf_path, dpi=300)
            
            # Convert to numpy arrays and resize to A4 if requested
            processed_images = []
            for img in images:
                np_img = np.array(img)
                
                if resize_to_a4:
                    # Resize to A4 dimensions (595x841 pixels)
                    from PIL import Image
                    pil_img = Image.fromarray(np_img)
                    resized_img = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    np_img = np.array(resized_img)
                    
                processed_images.append(np_img)
            
            self.logger.info(f"Converted {len(processed_images)} pages to A4 size ({target_width}x{target_height})")
            return processed_images
            
        except Exception as e:
            self.logger.error(f"Error converting PDF to images: {e}")
            # Provide helpful error message
            if "poppler" in str(e).lower():
                self.logger.error("Poppler is required for PDF processing. Please run: python install_poppler.py")
            raise
    
    def _find_poppler_path(self) -> Optional[str]:
        """Find Poppler installation path"""
        # Get project root (go up from src/core to project root)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        
        # Check local installation first - use absolute paths
        local_poppler_paths = [
            project_root / "poppler" / "poppler-23.08.0" / "Library" / "bin",
            project_root / "poppler" / "Library" / "bin", 
            project_root / "poppler" / "bin",
            Path("poppler") / "poppler-23.08.0" / "Library" / "bin",
            Path("poppler") / "Library" / "bin",
            Path("poppler") / "bin"
        ]
        
        for path in local_poppler_paths:
            try:
                abs_path = path.resolve()
                pdftoppm_exe = abs_path / "pdftoppm.exe"
                if abs_path.exists() and pdftoppm_exe.exists():
                    self.logger.info(f"Found local Poppler at: {abs_path}")
                    return str(abs_path)
            except Exception as e:
                self.logger.debug(f"Error checking path {path}: {e}")
                continue
        
        # Check common installation paths
        common_paths = [
            Path("C:/poppler/bin"),
            Path("C:/Program Files/poppler/bin"),
            Path("C:/Program Files (x86)/poppler/bin")
        ]
        
        for path in common_paths:
            if path.exists() and (path / "pdftoppm.exe").exists():
                self.logger.info(f"Found system Poppler at: {path}")
                return str(path)
        
        return None
    
    def _create_chunks(self, image: np.ndarray, page_idx: int) -> List[Dict]:
        """
        Create overlapping chunks from an image
        
        Args:
            image: Input image as numpy array
            page_idx: Page index for metadata
            
        Returns:
            List of chunk dictionaries
        """
        height, width = image.shape[:2]
        chunks = []
        chunk_idx = 0
        
        # Calculate step size (chunk_size - overlap)
        step_size = self.chunk_size - self.overlap
        
        for y in range(0, height - self.chunk_size + 1, step_size):
            for x in range(0, width - self.chunk_size + 1, step_size):
                # Extract chunk
                chunk_image = image[y:y+self.chunk_size, x:x+self.chunk_size]
                
                # Create chunk metadata
                chunk_data = {
                    "chunk_id": f"page_{page_idx}_chunk_{chunk_idx}",
                    "page_index": page_idx,
                    "chunk_index": chunk_idx,
                    "position": {
                        "x": x,
                        "y": y,
                        "width": self.chunk_size,
                        "height": self.chunk_size
                    },
                    "image": chunk_image,
                    "image_shape": chunk_image.shape
                }
                
                chunks.append(chunk_data)
                chunk_idx += 1
        
        # Handle edge cases - chunks at the borders
        self._add_edge_chunks(image, chunks, page_idx, chunk_idx)
        
        return chunks
    
    def _add_edge_chunks(self, image: np.ndarray, chunks: List[Dict], page_idx: int, start_idx: int):
        """Add chunks for edge areas that might be missed"""
        height, width = image.shape[:2]
        chunk_idx = start_idx
        
        # Right edge
        if width % self.chunk_size != 0:
            for y in range(0, height - self.chunk_size + 1, self.chunk_size - self.overlap):
                x = width - self.chunk_size
                chunk_image = image[y:y+self.chunk_size, x:x+self.chunk_size]
                
                chunk_data = {
                    "chunk_id": f"page_{page_idx}_edge_chunk_{chunk_idx}",
                    "page_index": page_idx,
                    "chunk_index": chunk_idx,
                    "position": {
                        "x": x,
                        "y": y,
                        "width": self.chunk_size,
                        "height": self.chunk_size
                    },
                    "image": chunk_image,
                    "image_shape": chunk_image.shape,
                    "edge_chunk": True
                }
                
                chunks.append(chunk_data)
                chunk_idx += 1
        
        # Bottom edge
        if height % self.chunk_size != 0:
            for x in range(0, width - self.chunk_size + 1, self.chunk_size - self.overlap):
                y = height - self.chunk_size
                chunk_image = image[y:y+self.chunk_size, x:x+self.chunk_size]
                
                chunk_data = {
                    "chunk_id": f"page_{page_idx}_edge_chunk_{chunk_idx}",
                    "page_index": page_idx,
                    "chunk_index": chunk_idx,
                    "position": {
                        "x": x,
                        "y": y,
                        "width": self.chunk_size,
                        "height": self.chunk_size
                    },
                    "image": chunk_image,
                    "image_shape": chunk_image.shape,
                    "edge_chunk": True
                }
                
                chunks.append(chunk_data)
                chunk_idx += 1
    
    def save_chunk_preview(self, chunks: List[Dict], output_folder: str):
        """Save chunk images for debugging/preview"""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for chunk in chunks:
            chunk_image = chunk["image"]
            filename = f"{chunk['chunk_id']}.png"
            
            # Convert numpy array to PIL Image and save
            if len(chunk_image.shape) == 3:
                pil_image = Image.fromarray(chunk_image.astype('uint8'))
            else:
                pil_image = Image.fromarray(chunk_image.astype('uint8'), mode='L')
            
            pil_image.save(output_path / filename)
        
        self.logger.info(f"Saved {len(chunks)} chunk previews to {output_folder}")
    
    def get_document_metadata(self, input_path: str) -> Dict:
        """Extract metadata from document"""
        file_path = Path(input_path)
        
        metadata = {
            "filename": file_path.name,
            "file_size": file_path.stat().st_size,
            "format": file_path.suffix.lower(),
            "path": str(file_path.absolute())
        }
        
        if file_path.suffix.lower() == '.pdf':
            try:
                with open(input_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    metadata["page_count"] = len(pdf_reader.pages)
                    
                    if pdf_reader.metadata:
                        metadata["title"] = pdf_reader.metadata.get("/Title", "")
                        metadata["author"] = pdf_reader.metadata.get("/Author", "")
                        metadata["subject"] = pdf_reader.metadata.get("/Subject", "")
            except Exception as e:
                self.logger.warning(f"Could not extract PDF metadata: {e}")
        
        return metadata