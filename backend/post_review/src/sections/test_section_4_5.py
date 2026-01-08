#!/usr/bin/env python3
"""
Test Section 4_5 Implementation
Tests diagonal deletions + horizontal strikethroughs + arrow replacements
"""

import sys
import os
import json
from pathlib import Path
from docx import Document

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.section_implementations_reference import SectionImplementationsReference
from post_review_config_adapter import get_scaling_for_pdf

# Import EnhancedSectionedGPT4oOCR directly 
try:
    from sectioned_gpt4o_ocr import EnhancedSectionedGPT4oOCR
except ImportError:
    print("❌ Could not import EnhancedSectionedGPT4oOCR - using reference methods instead")
    EnhancedSectionedGPT4oOCR = None

def run_analysis_only(pdf_path=None, progress_callback=None):
    """Run Section 4_5 analysis only (no Word processing)"""
    print("Starting Section 4_5 Analysis")
    print("Analysis only - Word processing handled by unified processor")
    print("=" * 80)
    
    # This test section works with pre-extracted PNG images only
    # PDF sectioning is handled by PDFSectionSplitter
    
    # Make test directory relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_dir = os.path.join(project_root, "data", "test_sections", "section_4_5_test")
    section_name = "Section_4_5"
    
    if progress_callback:
        progress_callback(1, 3, section_name, "Extracting section image...")
    
    # Load pre-extracted section image
    try:
        os.makedirs(test_dir, exist_ok=True)
        
        # Check for pre-extracted image
        section_image_path = f"{test_dir}/section_4_5_extracted.png"
        
        if os.path.exists(section_image_path):
            print(f"✅ Found pre-extracted image: {section_image_path}")
        else:
            print(f"❌ Pre-extracted image not found: {section_image_path}")
            print(f"   💡 Make sure to run pdf_section_splitter.py first!")
            return False
        
    except Exception as e:
        print(f"Error loading pre-extracted image: {e}")
        return False
    
    if progress_callback:
        progress_callback(2, 3, section_name, "Analyzing with GPT-4o...")
    
    # Analyze with GPT-4o
    try:
        print(f"🤖 Analyzing Section 4_5 with GPT-4o...")
        
        # Import reference for GPT-4o analysis
        reference = SectionImplementationsReference()
        
        # Load the extracted image
        from PIL import Image
        section_image = Image.open(section_image_path)
        
        # Get the analysis prompt and run GPT-4o analysis
        prompt = reference.get_section_4_5_analysis_prompt()
        analysis_result = reference.analyze_section_with_gpt4o(section_image, prompt)
        
        if not analysis_result["success"]:
            print(f"❌ GPT-4o analysis failed: {analysis_result['raw_analysis']}")
            return False
        
        print(f"✅ GPT-4o analysis completed")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False
    
    if progress_callback:
        progress_callback(3, 3, section_name, "Saving analysis results...")
    
    # Save analysis results
    try:
        analysis_file = f"{test_dir}/section_4_5_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        print(f"Analysis saved: {analysis_file}")
        
    except Exception as e:
        print(f"Error saving analysis: {e}")
        return False
    
    print(f"Section 4_5 Analysis Complete!")
    return True

def main():
    """Run 4 5 test"""
    import argparse

    parser = argparse.ArgumentParser(description="4 5 Tester")
    parser.add_argument("--pdf-path", help="Path to PDF file for analysis")
    parser.add_argument("--analysis-only", action="store_true",
                       help="Run only analysis (no Word processing)")
    args = parser.parse_args()

    if args.analysis_only:
        success = run_analysis_only(pdf_path=args.pdf_path)
        print(f"Analysis {'completed successfully' if success else 'failed'}")
    else:
        success = run_analysis_only(pdf_path=args.pdf_path)  # Function-based, no separate test method
        print(f"Analysis {'completed successfully' if success else 'failed'}")

if __name__ == "__main__":
    main()

