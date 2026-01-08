#!/usr/bin/env python3
"""
Production-Ready Document Processing Orchestrator
Integrates your 3-strategy cascading system with the existing template-based pipeline
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# FORCE RELOAD ENVIRONMENT VARIABLES
load_dotenv(override=True)

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.document_parser import DocumentParser
from src.core.chunk_analyzer import ChunkAnalyzer
from src.processors.unified_section_processor import UnifiedSectionProcessor

class ProductionDocumentOrchestrator:
    """
    Master orchestrator that ties together:
    1. Your existing template system (10 chunks instead of 188)
    2. GPT-4o Vision analysis 
    3. New unified section processor with 3-strategy implementation
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the production-ready orchestrator with dynamic configuration"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Production Document Orchestrator")
        
        # STEP 1: Project Root Detection (Cross-Platform Path Handling)
        project_root = Path(__file__).parent.parent
        
        # STEP 2: Config Path Resolution
        if config_path is None:
            config_path = project_root / "data" / "templates" / "config.yaml"
        
        self.config_path = str(config_path)
        self.project_root = project_root
        
        # STEP 3: Load Configuration
        self.config = self._load_config(self.config_path)
        
        # STEP 4: Component Initialization with Error Handling
        try:
            self.logger.info("Step 1: Initializing DocumentParser...")
            self.document_parser = DocumentParser(self.config_path)
            
            self.logger.info("Step 2: Initializing ChunkAnalyzer...")
            self.chunk_analyzer = ChunkAnalyzer(self.config)
            
            self.logger.info("Step 3: Initializing UnifiedSectionProcessor...")
            self.section_processor = UnifiedSectionProcessor(self.config_path)
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            # Comprehensive error logging for debugging
            import traceback
            full_traceback = traceback.format_exc()
            
            self.logger.error("=" * 60)
            self.logger.error("COMPONENT INITIALIZATION FAILED")
            self.logger.error("=" * 60)
            self.logger.error(f"Error type: {type(e).__name__}")
            self.logger.error(f"Error message: {str(e)}")
            self.logger.error(f"Config path: {self.config_path}")
            self.logger.error(f"Project root: {self.project_root}")
            self.logger.error(f"Config file exists: {Path(self.config_path).exists()}")
            
            # Show config structure if file exists
            if Path(self.config_path).exists():
                try:
                    import yaml
                    with open(self.config_path, 'r') as f:
                        config_content = yaml.safe_load(f)
                    self.logger.error(f"Config keys: {list(config_content.keys()) if config_content else 'Empty config'}")
                    if 'document' in config_content:
                        self.logger.error(f"Document config: {config_content['document']}")
                    else:
                        self.logger.error("ERROR: 'document' key missing from config!")
                except Exception as config_error:
                    self.logger.error(f"Failed to read config: {config_error}")
            else:
                self.logger.error("ERROR: Config file does not exist!")
            
            self.logger.error("Full traceback:")
            self.logger.error(full_traceback)
            self.logger.error("=" * 60)
            
            print("=" * 60)
            print("COMPONENT INITIALIZATION FAILED")
            print("=" * 60)
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Config path: {self.config_path}")
            print(f"Project root: {self.project_root}")
            print(f"Config file exists: {Path(self.config_path).exists()}")
            
            if Path(self.config_path).exists():
                try:
                    import yaml
                    with open(self.config_path, 'r') as f:
                        config_content = yaml.safe_load(f)
                    print(f"Config keys: {list(config_content.keys()) if config_content else 'Empty config'}")
                    if 'document' in config_content:
                        print(f"Document config: {config_content['document']}")
                    else:
                        print("ERROR: 'document' key missing from config!")
                except Exception as config_error:
                    print(f"Failed to read config: {config_error}")
            else:
                print("ERROR: Config file does not exist!")
            
            print("Full traceback:")
            print(full_traceback)
            print("=" * 60)
            
            raise Exception(f"Component initialization failed: {str(e)}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration file with fallback handling"""
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    import yaml
                    return yaml.safe_load(f)
            else:
                self.logger.warning(f"Config file not found: {config_path}, using defaults")
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Default configuration for the system"""
        return {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': 'gpt-4o',
                'max_tokens': 1000
            },
            'processing': {
                'similarity_threshold': 0.6,
                'max_retries': 3,
                'enable_logging': True
            },
            'output': {
                'include_change_summary': True,
                'timestamp_format': '%Y%m%d_%H%M%S'
            }
        }
    
    def process_value_creator_document_with_sizing(self, pdf_path: str, word_template_path: str, 
                                                 output_path: str, target_width: int = 595, 
                                                 target_height: int = 841, update_chunks: bool = True) -> Dict:
        """
        Process Value Creator document with specific A4 sizing and chunk updating
        
        Args:
            pdf_path: Path to PDF file 
            word_template_path: Path to Word template
            output_path: Path for processed output
            target_width: Target width in pixels (default 595 for A4)
            target_height: Target height in pixels (default 841 for A4)
            update_chunks: Whether to update chunk storage on new uploads
            
        Returns:
            Processing results dictionary
        """
        self.logger.info(f"Starting Value Creator document processing with A4 sizing ({target_width}x{target_height})")
        
        # Step 1: File validation with A4 sizing parameters
        try:
            # Validate input files
            if not Path(pdf_path).exists():
                return {'status': 'error', 'stage': 'validation', 'error': f'PDF not found: {pdf_path}'}
            if not Path(word_template_path).exists():
                return {'status': 'error', 'stage': 'validation', 'error': f'Word template not found: {word_template_path}'}
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"PDF: {pdf_path}")
            self.logger.info(f"Word template: {word_template_path}")
            self.logger.info(f"Output: {output_path}")
            self.logger.info(f"Target size: {target_width}x{target_height} pixels")
            self.logger.info("File validation complete")
            
        except Exception as e:
            return {
                'status': 'error',
                'stage': 'validation',
                'error': f'Validation failed: {str(e)}'
            }
        
        # Step 2: Clear and update chunk storage if requested
        if update_chunks:
            try:
                self.logger.info("Clearing previous chunk storage...")
                chunk_dir = Path("chunk_previews")
                if chunk_dir.exists():
                    import shutil
                    shutil.rmtree(chunk_dir)
                chunk_dir.mkdir(exist_ok=True)
                self.logger.info("Chunk storage cleared and ready for new chunks")
            except Exception as e:
                self.logger.warning(f"Could not clear chunk storage: {e}")
        
        # Step 3: PDF processing with A4 sizing
        try:
            self.logger.info("Stage 1: PDF chunk extraction with A4 sizing")
            
            # Force automatic selection for Value Creator app
            original_selection_method = self.config.get('analysis', {}).get('selection_method', 'manual')
            self.config['analysis']['selection_method'] = 'automatic'
            self.config['analysis']['auto_select_all'] = True
            
            # Update document preprocessor config for A4 sizing
            self.config['document']['target_width'] = target_width
            self.config['document']['target_height'] = target_height
            self.config['document']['resize_to_a4'] = True
            
            # Process PDF with updated sizing
            pdf_results = self.document_parser.parse_document(
                input_path=pdf_path,
                output_path=output_path,
                template_docx=word_template_path
            )
            
            # Restore original selection method
            self.config['analysis']['selection_method'] = original_selection_method
            
            self.logger.info(f"PDF processing complete: {pdf_results.get('chunks_processed', 0)} chunks")
            
        except Exception as e:
            return {
                'status': 'error', 
                'stage': 'pdf_processing',
                'error': f'PDF processing failed: {str(e)}'
            }
        
        # Step 4: Word document implementation
        try:
            self.logger.info("Stage 2: Word document implementation")
            
            # DEBUG: Log the pdf_results structure
            self.logger.info(f"DEBUG: pdf_results keys: {list(pdf_results.keys()) if isinstance(pdf_results, dict) else 'Not a dict'}")
            if isinstance(pdf_results, dict):
                if 'analysis_results' in pdf_results:
                    self.logger.info(f"DEBUG: Found analysis_results with {len(pdf_results['analysis_results'])} items")
                elif 'chunks' in pdf_results:
                    self.logger.info(f"DEBUG: Found chunks with {len(pdf_results['chunks'])} items")
                else:
                    self.logger.info(f"DEBUG: No analysis_results or chunks found in pdf_results")
            
            # Process through test_production_system approach
            # Convert pdf_results to the format expected by process_all_sections
            section_analyses = {}
            
            # Extract analyses from PDF results - adapt based on actual pdf_results structure
            if 'analysis_results' in pdf_results:
                for i, analysis in enumerate(pdf_results['analysis_results']):
                    section_name = f"chunk_{i+1}"
                    section_analyses[section_name] = analysis
                    self.logger.info(f"DEBUG: Added analysis for {section_name}")
            elif 'chunks' in pdf_results:
                for i, chunk in enumerate(pdf_results['chunks']):
                    section_name = f"chunk_{i+1}"
                    # Create analysis structure if chunk has analysis data
                    section_analyses[section_name] = chunk.get('analysis', {})
                    self.logger.info(f"DEBUG: Added chunk analysis for {section_name}")
            else:
                # Fallback - create empty analyses for each expected chunk
                self.logger.info("DEBUG: Using fallback - creating empty analyses")
                for i in range(10):  # Expected 10 chunks
                    section_name = f"chunk_{i+1}"
                    section_analyses[section_name] = {}
            
            self.logger.info(f"DEBUG: Final section_analyses has {len(section_analyses)} sections")
            
            word_results = self.section_processor.process_all_sections(
                section_analyses=section_analyses,
                base_document_path=word_template_path,
                output_path=output_path
            )
            
            self.logger.info("Word document implementation complete")
            
        except Exception as e:
            return {
                'status': 'error',
                'stage': 'word_processing', 
                'error': f'Word processing failed: {str(e)}'
            }
        
        # Step 5: Success response
        return {
            'status': 'success',
            'output_path': output_path,
            'pdf_results': pdf_results,
            'word_results': word_results,
            'sizing': {
                'width': target_width,
                'height': target_height,
                'chunks_updated': update_chunks
            }
        }

    def process_value_creator_document(self, pdf_path: str, word_template_path: str, 
                                     output_path: str) -> Dict[str, Any]:
        """
        Complete end-to-end processing using your proven architecture
        
        Args:
            pdf_path: Path to PDF with handwritten annotations
            word_template_path: Path to base Word document template
            output_path: Path for final processed document
            
        Returns:
            Comprehensive processing results with full audit trail
        """
        self.logger.info(f"Starting Value Creator document processing")
        
        processing_start = datetime.now()
        
        # STEP 1: Pre-Processing Validation (Following your working pattern)
        try:
            # File Existence Checks
            if not Path(pdf_path).exists():
                return {
                    'status': 'error',
                    'stage': 'validation',
                    'error': f'PDF file not found: {pdf_path}',
                    'processing_time': 0
                }
                
            if not Path(word_template_path).exists():
                return {
                    'status': 'error', 
                    'stage': 'validation',
                    'error': f'Word template not found: {word_template_path}',
                    'processing_time': 0
                }
            
            # File Type Validation
            if not pdf_path.lower().endswith('.pdf'):
                return {
                    'status': 'error',
                    'stage': 'validation',
                    'error': f'Invalid PDF file type: {pdf_path}',
                    'processing_time': 0
                }
                
            if not word_template_path.lower().endswith(('.doc', '.docx')):
                return {
                    'status': 'error',
                    'stage': 'validation', 
                    'error': f'Invalid Word document type: {word_template_path}',
                    'processing_time': 0
                }
            
            # Output Directory Creation
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"PDF: {pdf_path}")
            self.logger.info(f"Word template: {word_template_path}")
            self.logger.info(f"Output: {output_path}")
            self.logger.info("File validation complete")
            
        except Exception as e:
            return {
                'status': 'error',
                'stage': 'validation',
                'error': f'File validation failed: {str(e)}',
                'processing_time': (datetime.now() - processing_start).total_seconds()
            }
        
        try:
            # ===== STAGE 1: PDF CHUNK EXTRACTION (Template-based) =====
            self.logger.info("Stage 1: PDF chunk extraction using template system")
            
            pdf_results = self.document_parser.parse_document(
                input_path=pdf_path,
                output_path=output_path,
                template_docx=word_template_path
            )
            
            if pdf_results.get('status') != 'success':
                return {
                    'status': 'error',
                    'stage': 'pdf_processing', 
                    'error': pdf_results.get('error', 'PDF processing failed'),
                    'processing_time': (datetime.now() - processing_start).total_seconds()
                }
            
            # Extract analysis results from PDF processing
            analysis_results = pdf_results.get('analysis_results', {})
            self.logger.info(f"Stage 1 complete: {len(analysis_results)} chunks analyzed")
            
            # ===== STAGE 2: CONVERT TO SECTION-BASED ANALYSIS =====
            self.logger.info("Stage 2: Converting chunk analysis to section-based format")
            
            section_analyses = self._convert_chunks_to_sections(analysis_results)
            self.logger.info(f"Stage 2 complete: {len(section_analyses)} sections prepared")
            
            # ===== STAGE 3: UNIFIED WORD PROCESSING =====
            self.logger.info("Stage 3: Applying changes using 3-strategy cascading system")
            
            word_results = self.section_processor.process_all_sections(
                section_analyses=section_analyses,
                base_document_path=word_template_path,
                output_path=output_path
            )
            
            if word_results.get('status') != 'success':
                return {
                    'status': 'error',
                    'stage': 'word_processing',
                    'error': word_results.get('error', 'Word processing failed'),
                    'processing_time': (datetime.now() - processing_start).total_seconds()
                }
            
            self.logger.info(f"Stage 3 complete: {word_results.get('changes', {}).get('total_changes_applied', 0)} changes applied")
            
            # ===== FINAL RESULTS =====
            processing_time = (datetime.now() - processing_start).total_seconds()
            
            final_results = {
                'status': 'success',
                'processing_timestamp': processing_start.isoformat(),
                'processing_time_seconds': processing_time,
                'input_files': {
                    'pdf': pdf_path,
                    'word_template': word_template_path
                },
                'output_file': output_path,
                'stages': {
                    'pdf_analysis': {
                        'chunks_processed': len(analysis_results),
                        'template_used': pdf_results.get('template_used', False),
                        'analysis_results': analysis_results
                    },
                    'section_conversion': {
                        'sections_created': len(section_analyses),
                        'conversion_method': 'chunk_to_section_mapping'
                    },
                    'word_processing': word_results
                },
                'performance_metrics': {
                    'total_processing_time': f"{processing_time:.2f} seconds",
                    'avg_time_per_chunk': f"{processing_time / len(analysis_results):.2f} seconds" if analysis_results else "N/A",
                    'success_rate': f"{word_results.get('sections', {}).get('success_rate', 0) * 100:.1f}%"
                }
            }
            
            self.logger.info(f"Processing complete! Time: {processing_time:.2f}s")
            self.logger.info(f"Success rate: {final_results['performance_metrics']['success_rate']}")
            
            return final_results
            
        except Exception as e:
            processing_time = (datetime.now() - processing_start).total_seconds()
            self.logger.error(f"Critical error in document processing: {str(e)}")
            
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': processing_time,
                'stage': 'orchestration'
            }
    
    def _convert_chunks_to_sections(self, analysis_results: Dict) -> Dict[str, Dict]:
        """
        Convert aggregated analysis results to section-based format
        This maps detected items to the section-specific business rules
        """
        section_analyses = {}
        
        # Map chunk-specific items to their corresponding section handlers
        # Check for chunk-specific detections and create appropriate sections
        
        # Chunk 1: Date replacement in greeting section
        chunk_1_items = self._extract_chunk_items(analysis_results, chunk_index=1)
        if chunk_1_items:
            section_analyses['chunk_1_date_replacement'] = {
                'section_type': 'chunk_1_date_replacement',
                'chunk_index': 1,
                'detected_items': chunk_1_items,
                'business_rules': ['replace_xxxx_with_date'],
                'target_text': 'XXXX',
                'replacement_source': 'handwritten_date'
            }
        
        # Chunk 2: Bullet point filling for concerns section
        chunk_2_items = self._extract_chunk_items(analysis_results, chunk_index=2)
        if chunk_2_items:
            section_analyses['chunk_2_bullet_points'] = {
                'section_type': 'chunk_2_bullet_points',
                'chunk_index': 2,
                'detected_items': chunk_2_items,
                'business_rules': ['fill_bullet_points', 'add_new_bullets'],
                'target_section': 'concerns_bullet_points',
                'bullet_count': 3  # Default empty bullets to fill
            }
        
        # Chunk 3: Bullet point filling for opportunities section
        chunk_3_items = self._extract_chunk_items(analysis_results, chunk_index=3)
        if chunk_3_items:
            section_analyses['chunk_3_bullet_points'] = {
                'section_type': 'chunk_3_bullet_points',
                'chunk_index': 3,
                'detected_items': chunk_3_items,
                'business_rules': ['fill_bullet_points', 'add_new_bullets'],
                'target_section': 'opportunities_bullet_points',
                'bullet_count': 3  # Default empty bullets to fill
            }
        
        # Chunk 4: Always analyze content independently but avoid competing with chunk 5
        chunk_4_items = self._extract_chunk_items(analysis_results, chunk_index=4)
        chunk_5_items = self._extract_chunk_items(analysis_results, chunk_index=5)
        
        if chunk_4_items:
            # Check if chunk 5 also has strengths content
            chunk_5_has_strengths = self._chunk_contains_strengths_section(chunk_5_items) if chunk_5_items else False
            
            if chunk_5_has_strengths:
                # If chunk 5 has strengths, chunk 4 should be treated as additional opportunities content
                # to avoid competing for the same strengths bullet points
                section_analyses['chunk_4_additional_opportunities'] = {
                    'section_type': 'chunk_4_additional_opportunities',
                    'chunk_index': 4,
                    'detected_items': chunk_4_items,
                    'business_rules': ['append_to_opportunities', 'add_after_existing_bullets'],
                    'target_section': 'opportunities_additional',
                    'routing_reason': 'chunk_5_has_main_strengths'
                }
            else:
                # If chunk 5 doesn't have strengths, chunk 4 can be the main strengths
                chunk_4_has_strengths = self._chunk_contains_strengths_section(chunk_4_items)
                if chunk_4_has_strengths:
                    section_analyses['chunk_4_strengths'] = {
                        'section_type': 'chunk_4_strengths',
                        'chunk_index': 4,
                        'detected_items': chunk_4_items,
                        'business_rules': ['fill_bullet_points', 'add_new_bullets'],
                        'target_section': 'strengths_bullet_points',
                        'routing_reason': 'chunk_4_is_main_strengths'
                    }
                else:
                    section_analyses['chunk_4_standalone'] = {
                        'section_type': 'chunk_4_standalone',
                        'chunk_index': 4,
                        'detected_items': chunk_4_items,
                        'business_rules': ['determine_section_type', 'flexible_routing'],
                        'target_section': 'flexible',
                        'routing_reason': 'chunk_4_not_strengths'
                    }
        
        # Chunk 5: Always analyze content independently
        chunk_5_items = self._extract_chunk_items(analysis_results, chunk_index=5)
        if chunk_5_items:
            chunk_5_has_strengths = self._chunk_contains_strengths_section(chunk_5_items)
            if chunk_5_has_strengths:
                section_analyses['chunk_5_strengths'] = {
                    'section_type': 'chunk_5_strengths',
                    'chunk_index': 5,
                    'detected_items': chunk_5_items,
                    'business_rules': ['fill_bullet_points', 'add_new_bullets'],
                    'target_section': 'strengths_bullet_points',
                    'routing_reason': 'chunk_5_content_is_strengths'
                }
            else:
                section_analyses['chunk_5_general'] = {
                    'section_type': 'chunk_5_general',
                    'chunk_index': 5,
                    'detected_items': chunk_5_items,
                    'business_rules': ['determine_section_type', 'flexible_routing'],
                    'target_section': 'flexible',
                    'routing_reason': 'chunk_5_not_strengths'
                }
        
        # Chunk 6: Handle strikethrough, crosses, and $AMOUNT replacement
        chunk_6_items = self._extract_chunk_items(analysis_results, chunk_index=6)
        if chunk_6_items:
            section_analyses['chunk_6_editing'] = {
                'section_type': 'chunk_6_editing',
                'chunk_index': 6,
                'detected_items': chunk_6_items,
                'business_rules': ['delete_crossed_bullets', 'strikethrough_word_deletion', 'amount_replacement'],
                'target_section': 'strategies_section',
                'routing_reason': 'chunk_6_editing_operations'
            }
        
        # Chunk 7: Handle strikethrough and dot point deletion
        chunk_7_items = self._extract_chunk_items(analysis_results, chunk_index=7)
        if chunk_7_items:
            section_analyses['chunk_7_editing'] = {
                'section_type': 'chunk_7_editing',
                'chunk_index': 7,
                'detected_items': chunk_7_items,
                'business_rules': ['strikethrough_word_deletion', 'delete_crossed_bullets'],
                'target_section': 'cash_flow_section',
                'routing_reason': 'chunk_7_editing_operations'
            }
        
        # Chunk 8: Handle table row deletion based on crosses and lines
        chunk_8_items = self._extract_chunk_items(analysis_results, chunk_index=8)
        if chunk_8_items:
            section_analyses['chunk_8_editing'] = {
                'section_type': 'chunk_8_editing',
                'chunk_index': 8,
                'detected_items': chunk_8_items,
                'business_rules': ['delete_table_rows', 'append_handwritten_notes', 'ignore_small_diagonal_lines'],
                'target_section': 'business_plan_table',
                'routing_reason': 'chunk_8_table_row_deletion'
            }
        
        # Chunk 9: Handle $AMOUNT replacement and tax returns text substitution
        chunk_9_items = self._extract_chunk_items(analysis_results, chunk_index=9)
        if chunk_9_items:
            section_analyses['chunk_9_editing'] = {
                'section_type': 'chunk_9_editing',
                'chunk_index': 9,
                'detected_items': chunk_9_items,
                'business_rules': ['amount_replacement', 'text_substitution', 'color_correction'],
                'target_section': 'fee_section',
                'routing_reason': 'chunk_9_fee_and_tax_editing'
            }
        
        # Add other chunks as needed
        # For now, handle remaining items as general analysis
        remaining_items = self._get_non_chunk_specific_items(analysis_results)
        if remaining_items:
            section_analyses['general_analysis'] = {
                'section_type': 'general_analysis',
                'detected_items': remaining_items,
                'metadata': analysis_results.get('metadata', {}),
                'total_detections': sum(len(remaining_items.get(key, [])) for key in 
                    ['handwritten_text', 'strikethrough_text', 'crosses', 'arrows', 'highlights', 'annotations'])
            }
        
        return section_analyses
    
    def _extract_chunk_items(self, analysis_results: Dict, chunk_index: int) -> Dict:
        """Extract items that belong to a specific chunk"""
        chunk_items = {
            'handwritten_text': [],
            'strikethrough_text': [],
            'crosses': [],
            'arrows': [],
            'highlights': [],
            'annotations': []
        }
        
        # Filter items by chunk_index
        for category, items in analysis_results.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and item.get('chunk_index') == chunk_index:
                        chunk_items[category].append(item)
        
        return chunk_items
    
    def _get_non_chunk_specific_items(self, analysis_results: Dict) -> Dict:
        """Get items that don't belong to specific chunk handlers"""
        remaining_items = {
            'handwritten_text': [],
            'strikethrough_text': [],
            'crosses': [],
            'arrows': [],
            'highlights': [],
            'annotations': []
        }
        
        # For now, include items from chunks 1+ (index 1+) as general
        for category, items in analysis_results.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        chunk_idx = item.get('chunk_index', -1)
                        if chunk_idx != 1:  # Not chunk 1 (now 1-based)
                            remaining_items[category].append(item)
        
        return remaining_items
    
    def _chunk_contains_strengths_section(self, chunk_items: Dict) -> bool:
        """
        Check if a chunk contains the strengths section text
        
        Args:
            chunk_items: Detected items from the chunk
            
        Returns:
            bool: True if chunk contains strengths section indicators
        """
        if not chunk_items:
            return False
        
        # Check all detected text for strengths section indicators (headers and content)
        strengths_section_headers = [
            'reinforcing and maximizing your existing strengths',
            'established the following important strengths',
            'existing strengths',
            'important strengths',
            'maximizing.*strengths',
            'reinforcing.*strengths'
        ]
        
        # Also check for strengths content indicators (not just headers)
        strengths_content_indicators = [
            'educated', 'overachieving', 'daughters', 'plan', 'succeed', 'resources',
            'age', 'still', 'independent', 'freed up', 'cash', 'invest', 'future',
            'well', 'benefits', 'saving', 'manage', 'capable', 'financial',
            'established', 'expertise', 'skilled', 'experienced', 'good at',
            # Enhanced indicators for cash flow and financial strengths
            'increase in cash flow', 'cash flow', 'finishing high school', 'saving',
            'investment property', 'cash resources', 'financially independent',
            'free up', 'resources to invest', 'towards becoming', 'approx'
        ]
        
        # Check handwritten text for section headers
        handwritten_items = chunk_items.get('handwritten_text', [])
        for item in handwritten_items:
            text = item.get('text', item.get('description', '')).lower()
            # Check for section headers first
            for indicator in strengths_section_headers:
                if indicator.lower() in text:
                    return True
        
        # Check annotations for section headers
        annotations = chunk_items.get('annotations', [])
        for item in annotations:
            text = item.get('text', item.get('description', '')).lower()
            for indicator in strengths_section_headers:
                if indicator.lower() in text:
                    return True
        
        # If no section headers found, check for strengths content indicators
        all_text = ""
        for item in handwritten_items:
            all_text += item.get('text', item.get('description', '')).lower() + " "
        for item in annotations:
            all_text += item.get('text', item.get('description', '')).lower() + " "
        
        # Count strengths content indicators
        content_matches = sum(1 for indicator in strengths_content_indicators if indicator in all_text)
        
        # Lower threshold for strengths detection - cash flow content is clearly strengths
        if content_matches >= 2:
            self.logger.info(f"Chunk contains strengths section based on content indicators: {content_matches} matches")
            return True
        
        return False
    
    def _determine_section_type(self, chunk_id: str, chunk_data: Dict) -> str:
        """
        Determine which section type this chunk represents
        Customize this based on your specific document structure
        """
        # Example mapping logic - customize for your specific chunks
        chunk_content = chunk_data.get('analysis_results', {})
        
        # Check for two-box layout indicators
        if ('left_box' in str(chunk_content).lower() or 
            'right_box' in str(chunk_content).lower() or
            'items discussed' in str(chunk_content).lower()):
            return "section_1_4"
        
        # Check for handwritten text near bullets
        if (chunk_data.get('analysis_results', {}).get('handwritten_text') and
            'bullet' in str(chunk_content).lower()):
            return "section_1_2"
        
        # Check for portfolio selection indicators
        if ('portfolio' in str(chunk_content).lower() or
            'selection' in str(chunk_content).lower()):
            return "section_1_3"
        
        # Check for checkbox/circle patterns
        if (chunk_data.get('analysis_results', {}).get('crosses') or
            chunk_data.get('analysis_results', {}).get('highlights')):
            return "section_1_1"
        
        # Default to generic section
        return f"section_generic_{chunk_id}"
    
    def _convert_chunk_to_section_format(self, chunk_data: Dict, section_name: str) -> Optional[Dict]:
        """
        Convert chunk analysis results to section-specific format
        """
        analysis_results = chunk_data.get('analysis_results', {})
        
        if section_name == "section_1_4":
            # Convert to two-box format
            return {
                'left_box_analysis': {
                    'sentences_to_delete': self._extract_deletion_items(analysis_results, 'left'),
                    'sentences_to_replace': self._extract_replacement_items(analysis_results, 'left'),
                    'all_sentences_have_deletion_marks': self._check_all_marked(analysis_results, 'left')
                },
                'right_box_analysis': {
                    'sentences_to_delete': self._extract_deletion_items(analysis_results, 'right'),
                    'sentences_to_replace': self._extract_replacement_items(analysis_results, 'right'),
                    'all_sentences_have_deletion_marks': self._check_all_marked(analysis_results, 'right')
                },
                'row_deletion_rule': {
                    'delete_entire_row': self._should_delete_entire_row(analysis_results),
                    'deletion_reason': "Both boxes marked for deletion"
                }
            }
        
        elif section_name == "section_1_2":
            # Convert to handwritten text format
            handwritten_items = analysis_results.get('handwritten_text', [])
            return {
                'handwritten_text': [
                    {
                        'text': item.get('text', ''),
                        'nearby_bullet_text': item.get('nearby_text', ''),
                        'confidence': item.get('confidence', 0.8)
                    }
                    for item in handwritten_items
                ]
            }
        
        elif section_name == "section_1_3":
            # Convert to portfolio selection format
            return {
                'circled_items': self._extract_circled_items(analysis_results),
                'crossed_items': self._extract_crossed_items(analysis_results),
                'marked_bullet_points': self._extract_marked_bullets(analysis_results)
            }
        
        elif section_name == "section_1_1":
            # Convert to checkbox format
            return {
                'checkboxes': self._extract_checkbox_items(analysis_results)
            }
        
        else:
            # Generic format
            return {
                'items_to_delete': self._extract_generic_deletions(analysis_results),
                'items_to_replace': self._extract_generic_replacements(analysis_results)
            }
    
    def _extract_deletion_items(self, analysis: Dict, box_side: str) -> List[Dict]:
        """Extract items marked for deletion"""
        deletions = []
        
        # Look for strikethrough text
        strikethrough_items = analysis.get('strikethrough_text', [])
        for item in strikethrough_items:
            deletions.append({
                'sentence_text': item.get('text', ''),
                'mark_type': 'strikethrough',
                'confidence': item.get('confidence', 0.8)
            })
        
        # Look for crossed out items
        crosses = analysis.get('crosses', [])
        for item in crosses:
            if item.get('nearby_text'):
                deletions.append({
                    'sentence_text': item.get('nearby_text', ''),
                    'mark_type': 'cross',
                    'confidence': item.get('confidence', 0.8)
                })
        
        return deletions
    
    def _extract_replacement_items(self, analysis: Dict, box_side: str) -> List[Dict]:
        """Extract items marked for replacement"""
        replacements = []
        
        # Look for handwritten text that might be replacements
        handwritten_items = analysis.get('handwritten_text', [])
        for item in handwritten_items:
            if item.get('nearby_text'):  # Original text to replace
                replacements.append({
                    'original_text': item.get('nearby_text', ''),
                    'replacement_text': item.get('text', ''),
                    'mark_type': 'handwritten_replacement',
                    'confidence': item.get('confidence', 0.8)
                })
        
        return replacements
    
    def _check_all_marked(self, analysis: Dict, box_side: str) -> bool:
        """Check if all sentences in a box are marked for deletion"""
        # This would need more sophisticated logic based on your analysis structure
        strikethrough_count = len(analysis.get('strikethrough_text', []))
        cross_count = len(analysis.get('crosses', []))
        
        # Simple heuristic - if we have multiple deletion marks, assume all are marked
        return (strikethrough_count + cross_count) >= 2
    
    def _should_delete_entire_row(self, analysis: Dict) -> bool:
        """Determine if entire row should be deleted"""
        # Check if both left and right sides are heavily marked
        total_deletion_marks = (len(analysis.get('strikethrough_text', [])) + 
                               len(analysis.get('crosses', [])))
        
        return total_deletion_marks >= 3  # Threshold for row deletion
    
    def _extract_circled_items(self, analysis: Dict) -> List[Dict]:
        """Extract items that are circled (to keep)"""
        # Look for highlights that might represent circles
        highlights = analysis.get('highlights', [])
        return [
            {
                'text': item.get('text', ''),
                'confidence': item.get('confidence', 0.8)
            }
            for item in highlights
        ]
    
    def _extract_crossed_items(self, analysis: Dict) -> List[Dict]:
        """Extract items that are crossed out (to delete)"""
        crosses = analysis.get('crosses', [])
        return [
            {
                'text': item.get('nearby_text', ''),
                'confidence': item.get('confidence', 0.8)
            }
            for item in crosses if item.get('nearby_text')
        ]
    
    def _extract_marked_bullets(self, analysis: Dict) -> List[Dict]:
        """Extract bullet points marked for deletion"""
        # This would look for specific patterns in your analysis
        strikethrough_items = analysis.get('strikethrough_text', [])
        return [
            {
                'text': item.get('text', ''),
                'confidence': item.get('confidence', 0.8)
            }
            for item in strikethrough_items
            if 'bullet' in item.get('nearby_text', '').lower()
        ]
    
    def _extract_checkbox_items(self, analysis: Dict) -> List[Dict]:
        """Extract checkbox-style items"""
        items = []
        
        # Crosses indicate deletion
        crosses = analysis.get('crosses', [])
        for item in crosses:
            items.append({
                'item': item.get('nearby_text', ''),
                'status': 'crossed',
                'action': 'delete',
                'confidence': item.get('confidence', 0.8)
            })
        
        # Highlights might indicate selection
        highlights = analysis.get('highlights', [])
        for item in highlights:
            items.append({
                'item': item.get('text', ''),
                'status': 'highlighted',
                'action': 'keep',
                'confidence': item.get('confidence', 0.8)
            })
        
        return items
    
    def _extract_generic_deletions(self, analysis: Dict) -> List[str]:
        """Extract generic deletion items"""
        deletions = []
        
        # Add strikethrough text
        strikethrough_items = analysis.get('strikethrough_text', [])
        deletions.extend([item.get('text', '') for item in strikethrough_items])
        
        # Add crossed items
        crosses = analysis.get('crosses', [])
        deletions.extend([item.get('nearby_text', '') for item in crosses if item.get('nearby_text')])
        
        return [d for d in deletions if d]  # Filter out empty strings
    
    def _extract_generic_replacements(self, analysis: Dict) -> List[Dict]:
        """Extract generic replacement items"""
        replacements = []
        
        # Look for handwritten text as potential replacements
        handwritten_items = analysis.get('handwritten_text', [])
        for item in handwritten_items:
            if item.get('nearby_text'):
                replacements.append({
                    'original': item.get('nearby_text', ''),
                    'replacement': item.get('text', '')
                })
        
        return replacements


def main():
    """Example usage of the production orchestrator"""
    # Configure logging with UTF-8 support for emojis on Windows
    import sys
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize orchestrator
    orchestrator = ProductionDocumentOrchestrator()
    
    # Process a document
    result = orchestrator.process_value_creator_document(
        pdf_path="data/input/sample_value_creator.pdf",
        word_template_path="data/input/value_creator_template.docx",
        output_path="data/output/processed_value_creator.docx"
    )
    
    # Display results
    print("=" * 60)
    print(" PRODUCTION PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"Processing Time: {result['performance_metrics']['total_processing_time']}")
        print(f"Success Rate: {result['performance_metrics']['success_rate']}")
        print(f"Output File: {result['output_file']}")
        
        # Display stage results
        for stage_name, stage_data in result['stages'].items():
            print(f"\n{stage_name.title()}:")
            for key, value in stage_data.items():
                if key != 'analysis_results':  # Skip large data
                    print(f"  {key}: {value}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Failed at stage: {result.get('stage', 'Unknown')}")


if __name__ == "__main__":
    main()