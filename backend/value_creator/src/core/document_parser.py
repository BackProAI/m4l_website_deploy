#!/usr/bin/env python3
"""
Main Document Parser
Orchestrates the document parsing workflow using GPT-4o for visual analysis
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
from dotenv import load_dotenv
import numpy as np

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.chunk_analyzer import ChunkAnalyzer
from src.processors.word_processor import WordProcessor  
from src.core.document_preprocessor import DocumentPreprocessor

load_dotenv()

class DocumentParser:
    """Main document parsing system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # Initialize components
        self.preprocessor = DocumentPreprocessor(self.config)
        self.analyzer = ChunkAnalyzer(self.config)
        self.word_processor = WordProcessor(self.config)
        
        self.logger = logging.getLogger(__name__)
        
        # Template system
        # Template file for chunk coordinates  
        project_root = Path(__file__).parent.parent.parent
        self.template_file = project_root / "data" / "templates" / "chunk_template.json"
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load configuration from YAML file"""
        # Determine project root and config path
        project_root = Path(__file__).parent.parent.parent
        if config_path is None:
            config_path = project_root / "data" / "templates" / "config.yaml"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            config = self._get_default_config()
        
        # Expand environment variables
        if 'openai' in config and 'api_key' in config['openai']:
            config['openai']['api_key'] = os.path.expandvars(config['openai']['api_key'])
            
        return config
    
    def _get_default_config(self) -> Dict:
        """Return default configuration when config file is not found"""
        return {
            'document_processing': {
                'max_file_size_mb': 50,
                'supported_formats': ['pdf', 'doc', 'docx']
            },
            'ocr': {
                'dpi': 300,
                'language': 'eng',
                'confidence_threshold': 60
            },
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY', ''),
                'model': 'gpt-4o',
                'max_tokens': 4000,
                'temperature': 0.3
            },
            'analysis': {
                'detect_handwriting': True,
                'detect_strikethrough': True,
                'detect_crosses': True,
                'detect_highlighting': True,
                'detect_annotations': True,
                'confidence_threshold': 0.7
            },
            'ai_processing': {
                'model': 'gpt-4o',
                'max_tokens': 4000,
                'temperature': 0.3
            },
            'output': {
                'format': 'docx',
                'preserve_formatting': True,
                'backup_original': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/document_processor.log'
            },
            'templates': {
                'value_creator_letter': 'templates/value_creator_template.docx'
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration with UTF-8 support for emojis on Windows"""
        import sys
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['logging']['file']),
                logging.StreamHandler()
            ]
        )
    
    def _load_template_chunks(self, pdf_path: str) -> Optional[List[Dict]]:
        """Load and apply chunk template to PDF with chunk preview clearing"""
        try:
            import json
            import shutil
            
            # STEP 1: Clear previous chunk previews (safely handle permissions)
            chunk_preview_dir = Path("chunk_previews")
            if chunk_preview_dir.exists():
                try:
                    # Try to change permissions first on Windows
                    import stat
                    for root, dirs, files in os.walk(chunk_preview_dir):
                        for d in dirs:
                            try:
                                os.chmod(os.path.join(root, d), stat.S_IWRITE)
                            except:
                                pass
                        for f in files:
                            try:
                                os.chmod(os.path.join(root, f), stat.S_IWRITE)
                            except:
                                pass
                    
                    shutil.rmtree(chunk_preview_dir)
                    self.logger.info("Cleared previous chunk previews")
                except PermissionError as e:
                    self.logger.warning(f"Could not clear chunk_previews directory: {e}")
                    # Create a unique directory name instead
                    import time
                    timestamp = int(time.time())
                    chunk_preview_dir = Path(f"chunk_previews_{timestamp}")
                except Exception as e:
                    self.logger.warning(f"Error clearing chunk_previews: {e}")
                    # Use temp directory as fallback
                    import tempfile
                    chunk_preview_dir = Path(tempfile.mkdtemp(prefix="chunk_previews_"))
            
            chunk_preview_dir.mkdir(exist_ok=True)
            
            # STEP 2: Check if template exists
            if not os.path.exists(self.template_file):
                self.logger.warning(f"Template file not found: {self.template_file}")
                return None
                
            # STEP 3: Load template
            with open(self.template_file, 'r') as f:
                template = json.load(f)
            
            self.logger.info(f"Loaded chunk template with pages: {list(template.keys())}")
            
            # STEP 4: Convert PDF to images with A4 sizing
            from pdf2image import convert_from_path
            
            # Use the same poppler detection as visual_chunk_selector
            local_poppler_paths = [
                Path("poppler") / "poppler-23.08.0" / "Library" / "bin",
                Path("poppler") / "Library" / "bin",
                Path("poppler") / "bin"
            ]
            
            poppler_path = None
            for path in local_poppler_paths:
                if path.exists() and (path / "pdftoppm.exe").exists():
                    poppler_path = str(path)
                    break
            
            # Convert PDF to images (A4 size: 595x841)
            if poppler_path:
                images = convert_from_path(
                    pdf_path,
                    dpi=200,
                    poppler_path=poppler_path,
                    first_page=1,
                    last_page=4  # Process exactly 4 pages
                )
            else:
                images = convert_from_path(
                    pdf_path,
                    dpi=200,
                    first_page=1,
                    last_page=4
                )
            
            # Resize images to A4 (595x841) if needed
            from PIL import Image
            resized_images = []
            for img in images:
                if img.size != (595, 841):
                    img_resized = img.resize((595, 841), Image.Resampling.LANCZOS)
                    resized_images.append(img_resized)
                else:
                    resized_images.append(img)
            
            chunks = []
            chunk_id = 0
            
            # STEP 5: Apply template to each page
            for page_key in sorted(template.keys()):  # page_1, page_2, page_3, page_4
                page_num = int(page_key.split('_')[1]) - 1  # Convert to 0-based index
                
                if page_num < len(resized_images):
                    page_image = resized_images[page_num]
                    
                    # Process each chunk for this page
                    for chunk_data in template[page_key]:
                        chunk_name = chunk_data["name"]
                        rect = chunk_data["rect"]  # [x1, y1, x2, y2]
                        
                        # Ensure coordinates are within image bounds
                        x1, y1, x2, y2 = rect
                        x1 = max(0, min(int(x1), 595))
                        y1 = max(0, min(int(y1), 841))
                        x2 = max(x1, min(int(x2), 595))
                        y2 = max(y1, min(int(y2), 841))
                        
                        # Extract chunk image
                        chunk_image = page_image.crop((x1, y1, x2, y2))
                        
                        # Save chunk preview
                        chunk_filename = f"{chunk_name}.png"
                        chunk_path = chunk_preview_dir / chunk_filename
                        chunk_image.save(chunk_path)
                        
                        # Create chunk data compatible with existing system
                        chunk_info = {
                            'bbox': [x1, y1, x2, y2],
                            'page': page_num,
                            'image': np.array(chunk_image),  # Use numpy array like regular chunks
                            'chunk_id': chunk_id + 1,  # Convert to 1-based indexing
                            'confidence': 1.0,  # Template chunks are always confident
                            'position': {  # Add position field that chunk_analyzer expects
                                'x': x1,
                                'y': y1,
                                'width': x2 - x1,
                                'height': y2 - y1
                            },
                            'text': '',  # Add empty text field
                            'image_path': str(chunk_path),  # Path to saved preview
                            'name': chunk_name,
                            'section': chunk_data.get('description', f'Chunk {chunk_id + 1}')
                        }
                        
                        chunks.append(chunk_info)
                        chunk_id += 1
            
            self.logger.info(f"Created {len(chunks)} chunks from template")
            self.logger.info(f"Chunk previews saved to: {chunk_preview_dir}")
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to load template chunks: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
        
    def parse_document(self, input_path: str, output_path: str, template_docx: Optional[str] = None) -> Dict:
        """
        Parse a document and create an annotated Word document
        
        Args:
            input_path: Path to input document (PDF, image)
            output_path: Path for output Word document
            template_docx: Optional template Word document to modify
            
        Returns:
            Dictionary with parsing results and statistics
        """
        self.logger.info(f"Starting document parsing: {input_path}")
        
        try:
            # Step 1: Force template usage for consistent 10-chunk output
            force_template = self.config.get('analysis', {}).get('force_template_usage', True)
            
            self.logger.info("Loading chunk template for consistent 10-chunk processing...")
            chunks = self._load_template_chunks(input_path)
            template_used = False
            
            if chunks and len(chunks) > 0:
                self.logger.info(f"Template applied: Created {len(chunks)} chunks from template")
                template_used = True
            elif force_template:
                # If no template loaded but we're forcing template usage, try to load it anyway
                self.logger.warning("Template not found but force_template_usage is enabled. Creating fallback chunks...")
                chunks = self.preprocessor.process_document(input_path)
                self.logger.info(f"Created {len(chunks)} fallback chunks for analysis")
            else:
                # Fallback to regular preprocessing
                self.logger.info("No template found. Preprocessing document into chunks...")
                chunks = self.preprocessor.process_document(input_path)
                self.logger.info(f"Created {len(chunks)} chunks for analysis")
            
            # Save chunk previews for debugging
            try:
                chunk_preview_dir = "chunk_previews"
                Path(chunk_preview_dir).mkdir(exist_ok=True)
                self.preprocessor.save_chunk_preview(chunks, chunk_preview_dir)
                self.logger.info(f"Saved chunk previews to {chunk_preview_dir}/")
            except Exception as e:
                self.logger.warning(f"Could not save chunk previews: {e}")
            
            # Step 2: Determine chunk selection method
            if template_used:
                # Template chunks - use all of them automatically
                self.logger.info(f"Using all {len(chunks)} template chunks automatically (no manual selection needed)")
                selected_chunks = chunks
            else:
                # Regular chunks - check selection method
                selection_method = self.config.get('analysis', {}).get('selection_method', 'manual')
                
                if selection_method == 'manual':
                    self.logger.info("Manual chunk selection - choose specific chunks to analyze")
                    selected_chunks = self._manual_chunk_selection(chunks)
                    self.logger.info(f"Manual selection: {len(selected_chunks)}/{len(chunks)} chunks selected")
                else:
                    # Default to all chunks if not manual
                    selected_chunks = chunks
            
            # Step 3: Analyze selected chunks with GPT-4o
            self.logger.info(f"Analyzing {len(selected_chunks)} selected chunks with GPT-4o...")
            analysis_results = []
            
            # Create results for all chunks (selected ones get real analysis, others get empty results)
            chunk_to_result = {}
            
            for i, chunk in enumerate(selected_chunks):
                self.logger.info(f"Analyzing chunk {i+1}/{len(selected_chunks)} (chunk {chunk['chunk_id']})")
                result = self.analyzer.analyze_chunk(chunk)
                chunk_to_result[chunk['chunk_id']] = result
            
            # Fill in results for all chunks (empty results for non-selected chunks)
            for chunk in chunks:
                if chunk['chunk_id'] in chunk_to_result:
                    analysis_results.append(chunk_to_result[chunk['chunk_id']])
                else:
                    # Empty result for skipped chunk
                    empty_result = {
                        "chunk_id": chunk['chunk_id'],
                        "detections": [],
                        "handwriting": [],
                        "strikethrough_text": [],
                        "crosses": [],
                        "arrows": [],
                        "highlights": [],
                        "annotations": [],
                        "skipped": True,
                        "reason": "Not selected for analysis"
                    }
                    analysis_results.append(empty_result)
                
                # Debug output for each chunk
                total_detections = sum([
                    len(result.get('handwritten_text', [])),
                    len(result.get('strikethrough_text', [])),
                    len(result.get('crosses', [])),
                    len(result.get('arrows', [])),
                    len(result.get('highlights', [])),
                    len(result.get('annotations', []))
                ])
                self.logger.info(f"Chunk {i+1} analysis: {total_detections} total detections")
                
                # Log specific detections
                for category in ['handwritten_text', 'strikethrough_text', 'crosses', 'arrows', 'highlights', 'annotations']:
                    items = result.get(category, [])
                    if items:
                        self.logger.info(f"  - {category}: {len(items)} items")
                        for item in items[:3]:  # Show first 3 items
                            text = item.get('text', item.get('description', 'N/A'))[:50]
                            confidence = item.get('confidence', 0.0)
                            self.logger.info(f"    * {text}... (confidence: {confidence:.2f})")
            
            # Step 3: Aggregate results
            self.logger.info("Aggregating analysis results...")
            aggregated_results = self._aggregate_results(analysis_results, chunks)
            
            # Step 4: Create/modify Word document
            self.logger.info("Creating annotated Word document...")
            word_doc = self.word_processor.create_annotated_document(
                aggregated_results, 
                output_path, 
                template_docx
            )
            
            # Verify output file was created
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                self.logger.info(f"Output file created: {output_path} ({file_size} bytes)")
            else:
                self.logger.warning(f"Output file was not created: {output_path}")
            
            # Step 5: Generate summary
            summary = self._generate_summary(aggregated_results)
            
            # Save detailed debug results
            try:
                debug_results = {
                    "input_path": input_path,
                    "output_path": output_path,
                    "chunks_analyzed": len(chunks),
                    "chunk_details": [
                        {
                            "chunk_id": chunk["chunk_id"],
                            "position": chunk["position"],
                            "detections": analysis_results[i] if i < len(analysis_results) else {}
                        }
                        for i, chunk in enumerate(chunks)
                    ],
                    "summary": summary,
                    "aggregated_results": aggregated_results
                }
                
                debug_file = Path(output_path).with_suffix('.debug.json')
                import json
                with open(debug_file, 'w') as f:
                    json.dump(debug_results, f, indent=2, default=str)
                self.logger.info(f"Debug results saved to: {debug_file}")
            except Exception as e:
                self.logger.warning(f"Could not save debug results: {e}")
            
            self.logger.info(f"Document parsing completed: {output_path}")
            
            return {
                "status": "success",
                "input_path": input_path,
                "output_path": output_path,
                "chunks_analyzed": len(chunks),
                "detections": summary,
                "analysis_results": aggregated_results
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing document: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "input_path": input_path
            }
    
    def _aggregate_results(self, analysis_results: List[Dict], chunks: List[Dict]) -> Dict:
        """Aggregate analysis results from all chunks with deduplication"""
        aggregated = {
            "handwritten_text": [],
            "strikethrough_text": [],
            "crosses": [],
            "arrows": [],
            "highlights": [],
            "annotations": [],
            "metadata": {
                "total_chunks": len(chunks),
                "processed_chunks": len(analysis_results)
            }
        }
        
        def _is_similar_item(item1, item2, category):
            """Check if two items are similar enough to be considered duplicates"""
            # Text-based categories
            if category in ["handwritten_text", "strikethrough_text", "highlights", "annotations"]:
                if "text" in item1 and "text" in item2:
                    # Same text content
                    if item1["text"].strip().lower() == item2["text"].strip().lower():
                        return True
                    # Very similar text (85% similarity)
                    import difflib
                    similarity = difflib.SequenceMatcher(None, 
                        item1["text"].strip().lower(), 
                        item2["text"].strip().lower()).ratio()
                    if similarity >= 0.85:
                        return True
            
            # Position-based categories (crosses, arrows)
            elif category in ["crosses", "arrows"]:
                if "position" in item1 and "position" in item2:
                    pos1 = item1["position"]
                    pos2 = item2["position"]
                    # Similar positions (within 0.1 relative distance)
                    if (abs(pos1.get("x", 0) - pos2.get("x", 0)) < 0.1 and 
                        abs(pos1.get("y", 0) - pos2.get("y", 0)) < 0.1):
                        return True
            
            return False
        
        for i, result in enumerate(analysis_results):
            chunk_info = chunks[i]
            
            # Add position information and deduplicate
            for category in ["handwritten_text", "strikethrough_text", "crosses", "arrows", "highlights", "annotations"]:
                if category in result:
                    for item in result[category]:
                        # Add chunk metadata
                        item["chunk_index"] = i + 1  # Convert to 1-based indexing
                        item["chunk_position"] = chunk_info["position"]
                        
                        # Check for duplicates
                        is_duplicate = False
                        for existing_item in aggregated[category]:
                            if _is_similar_item(item, existing_item, category):
                                is_duplicate = True
                                break
                        
                        # Only add if not a duplicate
                        if not is_duplicate:
                            aggregated[category].append(item)
        
        return aggregated
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate summary statistics"""
        return {
            "handwritten_items": len(results["handwritten_text"]),
            "strikethrough_items": len(results["strikethrough_text"]),
            "crosses": len(results["crosses"]),
            "arrows": len(results["arrows"]),
            "highlights": len(results["highlights"]),
            "annotations": len(results["annotations"]),
            "total_detections": sum([
                len(results["handwritten_text"]),
                len(results["strikethrough_text"]),
                len(results["crosses"]),
                len(results["arrows"]),
                len(results["highlights"]),
                len(results["annotations"])
            ])
        }
    
    def batch_process(self, input_folder: str, output_folder: str, template_docx: Optional[str] = None) -> List[Dict]:
        """
        Process multiple documents in batch
        
        Args:
            input_folder: Folder containing input documents
            output_folder: Folder for output documents
            template_docx: Optional template Word document
            
        Returns:
            List of processing results for each document
        """
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        supported_formats = self.config['document']['supported_formats']
        results = []
        
        for file_path in input_path.iterdir():
            if file_path.suffix.lower() in supported_formats:
                output_file = output_path / f"{file_path.stem}_annotated.docx"
                result = self.parse_document(str(file_path), str(output_file), template_docx)
                results.append(result)
        
        return results
    
    def _manual_chunk_selection(self, chunks):
        """Simple manual chunk selection via command line"""
        print(f"\n=== Manual Chunk Selection ===")
        print(f"Total chunks: {len(chunks)}")
        print("Choose which chunks to analyze with GPT-4o:")
        print("1. Enter specific chunk numbers (e.g., 1,5,10-15)")
        print("2. Enter 'every N' to select every Nth chunk (e.g., 'every 5')")
        print("3. Enter 'first N' to select first N chunks (e.g., 'first 20')")
        print("4. Enter 'all' to analyze all chunks (slow!)")
        print("5. Enter 'none' to skip GPT analysis entirely")
        
        while True:
            try:
                selection = input("\nYour choice: ").strip().lower()
                
                if selection == 'all':
                    return chunks
                elif selection == 'none':
                    return []
                elif selection.startswith('every '):
                    # Every Nth chunk
                    n = int(selection.split()[1])
                    return chunks[::n]
                elif selection.startswith('first '):
                    # First N chunks
                    n = int(selection.split()[1])
                    return chunks[:n]
                elif ',' in selection or '-' in selection:
                    # Parse range/list of numbers
                    selected_indices = set()
                    parts = selection.split(',')
                    
                    for part in parts:
                        part = part.strip()
                        if '-' in part:
                            # Range like 10-15
                            start, end = map(int, part.split('-'))
                            selected_indices.update(range(start-1, end))  # Convert to 0-based
                        else:
                            # Single number
                            selected_indices.add(int(part) - 1)  # Convert to 0-based
                    
                    # Filter valid indices
                    valid_indices = [i for i in selected_indices if 0 <= i < len(chunks)]
                    return [chunks[i] for i in sorted(valid_indices)]
                else:
                    print("Invalid input. Please try again.")
                    
            except (ValueError, IndexError) as e:
                print(f"Error parsing input: {e}. Please try again.")


def main():
    """Example usage"""
    parser = DocumentParser()
    
    # Single document processing
    result = parser.parse_document(
        "input_document.pdf",
        "output_annotated.docx"
    )
    
    print(f"Processing result: {result}")


if __name__ == "__main__":
    main()