#!/usr/bin/env python3
"""
Unified Post Review Processor - UI Interface
This module provides a clean interface between the post review UI and the master unified processor.
It handles dynamic PDF and Word document inputs and provides progress callbacks for the UI.
"""

import os
import json
import time
from pathlib import Path
from .master_unified_processor import MasterUnifiedProcessor

def process_post_review_documents(pdf_path: str, word_path: str, output_dir: str = None, progress_callback: callable = None) -> dict:
    """
    Main entry point for processing post review documents from the UI.
    
    Args:
        pdf_path (str): Path to the annotated PDF document
        word_path (str): Path to the blank Word document  
        output_dir (str, optional): Output directory. Defaults to 'post_review_output/'
        progress_callback (callable, optional): Function to call for progress updates
                                              Format: progress_callback(current, total, section_name, details)
    
    Returns:
        dict: Processing results with success status, final document path, and detailed summary
        {
            'success': bool,
            'final_document': str,  # Path to output document
            'processing_summary': {
                'total_sections': int,
                'successful_sections': int, 
                'failed_sections': int,
                'skipped_sections': int,
                'no_change_sections': int,
                'total_changes_applied': int
            },
            'errors': list,  # Any errors encountered
            'section_details': dict  # Per-section results
        }
    """
    
    start_time = time.time()
    
    # Set default output directory
    if output_dir is None:
        output_dir = "post_review_output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize results structure
    results = {
        'success': False,
        'final_document': None,
        'processing_summary': {
            'total_sections': 17,
            'successful_sections': 0,
            'failed_sections': 0,
            'skipped_sections': 0,
            'no_change_sections': 0,
            'total_changes_applied': 0
        },
        'errors': [],
        'section_details': {}
    }
    
    try:
        # Initialize the master processor with dynamic inputs
        processor = MasterUnifiedProcessor(
            pdf_path=pdf_path,
            word_path=word_path,
            output_dir=output_dir
        )
        
        # Call progress callback for initialization
        if progress_callback:
            progress_callback(0, 4, "Initialization", "Setting up processing environment...")
        
        # Step 1: Extract and analyze all sections
        if progress_callback:
            progress_callback(1, 4, "Section Analysis", "Extracting images and analyzing handwriting for all sections...")
        
        collected_count = processor.run_analysis_extraction_only(progress_callback)
        
        if collected_count == 0:
            error_msg = "No section analyses found - PDF processing failed"
            results['errors'].append(error_msg)
            return results
        
        # Step 2: Apply unified implementations
        if progress_callback:
            progress_callback(2, 4, "Implementation", "Applying all changes to Word document...")
        
        final_document, processing_summary = processor.apply_unified_implementations(progress_callback)
        
        if final_document:
            results['success'] = True
            results['final_document'] = final_document
            results['processing_summary'].update(processing_summary)
            
            # Step 3: Finalization
            if progress_callback:
                progress_callback(3, 4, "Finalization", f"Processing complete! Output saved to {Path(final_document).name}")
        else:
            error_msg = "Failed to apply implementations to Word document"
            results['errors'].append(error_msg)
            
    except Exception as e:
        error_msg = f"Critical error during processing: {str(e)}"
        results['errors'].append(error_msg)
        
    # Calculate processing time
    end_time = time.time()
    processing_time = end_time - start_time
    results['processing_time'] = round(processing_time, 2)
    
    # Final progress callback
    if progress_callback:
        if results['success']:
            progress_callback(4, 4, "Complete", f"All processing finished successfully in {results['processing_time']}s")
        else:
            progress_callback(4, 4, "Failed", f"Processing failed after {results['processing_time']}s")
    
    return results

class UnifiedPostReviewProcessor:
    """
    Class-based interface for the unified post review processor.
    Provides more granular control over the processing workflow.
    """
    
    def __init__(self, pdf_path: str, word_path: str, output_dir: str = None):
        """Initialize the processor with document paths"""
        self.pdf_path = pdf_path
        self.word_path = word_path
        self.output_dir = output_dir or "post_review_output"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the master processor
        self.master_processor = MasterUnifiedProcessor(
            pdf_path=pdf_path,
            word_path=word_path,
            output_dir=self.output_dir
        )
        
    def process_with_progress(self, progress_callback: callable = None) -> dict:
        """
        Process documents with detailed progress reporting.
        
        Args:
            progress_callback (callable): Function for progress updates
            
        Returns:
            dict: Detailed processing results
        """
        return process_post_review_documents(
            pdf_path=self.pdf_path,
            word_path=self.word_path,
            output_dir=self.output_dir,
            progress_callback=progress_callback
        )
        
    def validate_inputs(self) -> dict:
        """
        Validate input files before processing.
        
        Returns:
            dict: Validation results with success status and any errors
        """
        validation_results = {
            'success': True,
            'errors': []
        }
        
        # Check if PDF exists and is readable
        if not os.path.exists(self.pdf_path):
            validation_results['success'] = False
            validation_results['errors'].append(f"PDF file not found: {self.pdf_path}")
        elif not self.pdf_path.lower().endswith('.pdf'):
            validation_results['success'] = False
            validation_results['errors'].append(f"Invalid PDF file extension: {self.pdf_path}")
            
        # Check if Word document exists and is readable
        if not os.path.exists(self.word_path):
            validation_results['success'] = False
            validation_results['errors'].append(f"Word document not found: {self.word_path}")
        elif not self.word_path.lower().endswith(('.docx', '.doc')):
            validation_results['success'] = False
            validation_results['errors'].append(f"Invalid Word document extension: {self.word_path}")
            
        return validation_results
