#!/usr/bin/env python3
"""
Master Unified Processor
This script collects all section analyses and extracted images, then applies
all implementations to a single Word document using the unified implementation system.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from PIL import Image
from .unified_section_implementations import UnifiedSectionImplementations
from .pdf_section_splitter import PDFSectionSplitter

try:
    from ..utils.cv_mark_detection import (
        detect_diagonal_cross,
        detect_diagonal_cross_in_regions,
        split_left_right_regions,
    )
except Exception:
    detect_diagonal_cross = None
    detect_diagonal_cross_in_regions = None
    split_left_right_regions = None

class MasterUnifiedProcessor:
    def __init__(self, pdf_path: str = None, word_path: str = None, output_dir: str = None):
        """
        Initialize the Master Unified Processor.
        
        Args:
            pdf_path (str, optional): Path to the annotated PDF. If None, uses command-line mode.
            word_path (str, optional): Path to the base Word document. If None, uses default.
            output_dir (str, optional): Output directory. If None, uses 'unified_implementation_output'.
        """
        # Handle dynamic inputs for UI integration
        # Get project root (go up from src/core/ to project root)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        if word_path:
            self.base_document = word_path
        else:
            # Default for command-line use - use relative path
            self.base_document = os.path.join(project_root, "BLANK Post_Review_Action_Plan(6).docx")
            
        self.pdf_path = pdf_path
        self.output_dir = output_dir or "unified_implementation_output"
        self.analysis_collection = {}
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Updated section mapping to use relative paths and new section names from post_review_sections_part2.json
        self.section_mapping = {
            "section_1_1": os.path.join(project_root, "data", "test_sections", "section_1_1_test"),
            "section_1_2": os.path.join(project_root, "data", "test_sections", "section_1_2_test"),
            "section_1_3": os.path.join(project_root, "data", "test_sections", "section_1_3_test"),
            "section_1_4": os.path.join(project_root, "data", "test_sections", "section_1_4_test"),
            "section_2_1": os.path.join(project_root, "data", "test_sections", "section_2_1_test"),
            "section_2_2_part1": os.path.join(project_root, "data", "test_sections", "section_2_2_part1_test"),  # Individual part directories
            "section_2_2_part2": os.path.join(project_root, "data", "test_sections", "section_2_2_part2_test"),  # Individual part directories
            "section_2_3": os.path.join(project_root, "data", "test_sections", "section_2_3_test"),
            "section_2_4": os.path.join(project_root, "data", "test_sections", "section_2_4_test"),
            "section_2_5": os.path.join(project_root, "data", "test_sections", "section_2_5_test"),
            "section_3_2": os.path.join(project_root, "data", "test_sections", "section_3_2_test"),
            "section_3_3": os.path.join(project_root, "data", "test_sections", "section_3_3_test"),
            "section_3_4": os.path.join(project_root, "data", "test_sections", "section_3_4_test"),
            "section_4_1_part1": os.path.join(project_root, "data", "test_sections", "section_4_1_part1_test"),  # Individual part directories
            "section_4_1_part2": os.path.join(project_root, "data", "test_sections", "section_4_1_part2_test"),  # Individual part directories
            "section_4_2": os.path.join(project_root, "data", "test_sections", "section_4_2_test"),
            "section_4_3": os.path.join(project_root, "data", "test_sections", "section_4_3_test"),
            "section_4_4": os.path.join(project_root, "data", "test_sections", "section_4_4_test"),
            "section_4_5": os.path.join(project_root, "data", "test_sections", "section_4_5_test"),
            "section_4_6": os.path.join(project_root, "data", "test_sections", "section_4_6_test"),  # New section
        }
    
    def run_analysis_extraction_only(self, progress_callback: callable = None):
        """
        Step 1: Run all section test files to extract images and perform analysis only
        (We'll modify the test files to skip the Word document implementation part)
        
        Args:
            progress_callback (callable, optional): Function to call for UI progress updates
        """
        print("🔍 STEP 1: EXTRACTING SECTION IMAGES AND ANALYSES")
        print("=" * 80)
        
        # SUBSTEP 1A: Extract all section images from PDF in one efficient operation
        if self.pdf_path:
            print(f"\n📄 SUBSTEP 1A: Extracting all section images from PDF...")
            print(f"   📄 PDF: {os.path.basename(self.pdf_path)}")
            
            try:
                # Initialize PDF splitter and extract all sections
                splitter = PDFSectionSplitter(self.pdf_path)
                extraction_results = splitter.extract_all_sections()
                
                # Get summary of results
                summary = splitter.get_extraction_summary()
                print(f"   ✅ PDF Section Extraction Complete:")
                print(f"      📊 {summary['successful']}/{summary['total_sections']} sections extracted")
                print(f"      📈 Success rate: {summary['success_rate']:.1f}%")
                
                if summary['failed_sections']:
                    print(f"      ❌ Failed sections: {', '.join(summary['failed_sections'])}")
                
                # Call progress callback for UI updates
                if progress_callback:
                    progress_callback(1, 3, "PDF Extraction", f"Extracted {summary['successful']} section images")
                
            except Exception as e:
                print(f"   ❌ PDF section extraction failed: {e}")
                print(f"   ⚠️ Continuing with existing images if available...")
        else:
            print(f"\n📄 SUBSTEP 1A: No PDF provided - using existing section images")
        
        # SUBSTEP 1B: Process individual sections for GPT-4 analysis
        print(f"\n🧠 SUBSTEP 1B: Running GPT-4 analysis for all sections...")
        
        total_sections = len(self.section_mapping)
        current_section = 0
        
        # Group two-part sections for combined processing
        processed_two_part_sections = set()
        
        for section_name, folder_name in self.section_mapping.items():
            current_section += 1
            
            # Handle two-part sections as combined processing units
            if section_name == "section_2_2_part1":
                # Skip part1, will be processed when we reach part2
                print(f"\n⏭️ Skipping {section_name} - will process with part2...")
                continue
                
            elif section_name == "section_2_2_part2":
                # Process both parts together as "section_2_2"
                print(f"\n📷 Processing section_2_2 (combined two-part analysis)...")
                if progress_callback:
                    progress_callback(current_section, total_sections, "section_2_2", f"Extracting and analyzing section_2_2 (two-part)")
                
                # Process both parts
                self._process_two_part_section_2_2(progress_callback)
                processed_two_part_sections.add("section_2_2")
                continue
                
            elif section_name == "section_4_1_part1":
                # Skip part1, will be processed when we reach part2
                print(f"\n⏭️ Skipping {section_name} - will process with part2...")
                continue
                
            elif section_name == "section_4_1_part2":
                # Process both parts together as "section_4_1"
                print(f"\n📷 Processing section_4_1 (combined two-part analysis)...")
                if progress_callback:
                    progress_callback(current_section, total_sections, "section_4_1", f"Extracting and analyzing section_4_1 (two-part)")
                
                # Process both parts
                self._process_two_part_section_4_1(progress_callback)
                processed_two_part_sections.add("section_4_1")
                continue
                
            else:
                # Standard single-section processing
                print(f"\n📷 Processing {section_name}...")
                if progress_callback:
                    progress_callback(current_section, total_sections, section_name, f"Extracting and analyzing section {section_name}")
            
            try:

                # Check for FIXED versions first, then fall back to most recent regular versions
                analysis_file, image_file = self._find_most_recent_files(folder_name, section_name)
                
                # Run analysis using pre-extracted section image
                if self.pdf_path:
                    print(f"   🔄 Running {section_name} analysis with pre-extracted image")
                    success = self._run_section_analysis(section_name, folder_name, progress_callback)
                    if success:
                        # Load the newly generated analysis
                        print(f"   🔍 Looking for analysis and image files for {section_name}")
                        
                        # STANDARD SINGLE-SECTION HANDLING
                        analysis_file, image_file = self._find_most_recent_files(folder_name, section_name)
                        print(f"   📋 Found analysis_file: {analysis_file}")
                        print(f"   📋 Found image_file: {image_file}")
                        if analysis_file and image_file:
                            with open(analysis_file, 'r', encoding='utf-8') as f:
                                analysis_data = json.load(f)
                            print(f"   📊 Loaded analysis data with keys: {list(analysis_data.keys())}")
                            
                            # Parse the analysis data properly (same logic as existing analysis flow)
                            parsed_analysis = analysis_data.get("parsed_data", None)
                            print(f"   📊 parsed_data found: {parsed_analysis is not None}")
                            if not parsed_analysis and "raw_analysis" in analysis_data:
                                # Try to extract JSON from raw_analysis
                                print(f"   🔧 Attempting to parse raw_analysis for {section_name}")
                                raw_analysis = analysis_data["raw_analysis"]
                                if "```json" in raw_analysis or "{" in raw_analysis:
                                    # Find the JSON object boundaries directly in the raw_analysis
                                    first_brace = raw_analysis.find('{')
                                    last_brace = raw_analysis.rfind('}')
                                    
                                    if first_brace >= 0 and last_brace >= 0 and last_brace > first_brace:
                                        json_str = raw_analysis[first_brace:last_brace + 1]
                                        try:
                                            parsed_analysis = json.loads(json_str)
                                            print(f"      ✅ Successfully parsed JSON for {section_name}")
                                        except Exception as e:
                                            print(f"      ⚠️ JSON parsing error for {section_name}: {e}")
                                            print(f"      🔍 Trying fallback parsing...")
                                            # Fallback: try to clean up the JSON string
                                            try:
                                                # Remove any extra whitespace and normalize
                                                clean_json = json_str.strip()
                                                parsed_analysis = json.loads(clean_json)
                                                print(f"      ✅ Fallback parsing successful for {section_name}")
                                            except:
                                                print(f"      ❌ All parsing attempts failed for {section_name}")
                                                parsed_analysis = analysis_data
                                    else:
                                        print(f"      ⚠️ Could not find JSON boundaries for {section_name}")
                                        parsed_analysis = analysis_data
                                else:
                                    parsed_analysis = analysis_data
                            elif not parsed_analysis:
                                parsed_analysis = analysis_data

                            parsed_analysis = self._apply_cv_diagonal_cross_overrides(
                                section_name=section_name,
                                parsed_analysis=parsed_analysis,
                                image_path=image_file,
                            )
                            
                            self.analysis_collection[section_name] = {
                                "analysis": parsed_analysis,
                                "image_path": image_file
                            }
                            print(f"   📊 Fresh analysis and image collected for {section_name}")
                            print(f"   ✅ Successfully stored {section_name} in analysis_collection")
                        else:
                            print(f"   ❌ Analysis generation failed for {section_name}")
                    else:
                        print(f"   ❌ Section analysis failed for {section_name}")
                        
                elif analysis_file and image_file and os.path.exists(analysis_file) and os.path.exists(image_file):
                    print(f"   ✅ Using existing analysis and image")
                    
                    # STANDARD SINGLE-SECTION HANDLING (two-part sections are handled separately now)
                    with open(analysis_file, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                    
                    # Parse the analysis data properly
                    parsed_analysis = analysis_data.get("parsed_data", None)
                    if not parsed_analysis and "raw_analysis" in analysis_data:
                        # Try to extract JSON from raw_analysis
                        raw_analysis = analysis_data["raw_analysis"]
                        if "```json" in raw_analysis or "{" in raw_analysis:
                            # Find the JSON object boundaries directly in the raw_analysis
                            first_brace = raw_analysis.find('{')
                            last_brace = raw_analysis.rfind('}')
                            
                            if first_brace >= 0 and last_brace >= 0 and last_brace > first_brace:
                                json_str = raw_analysis[first_brace:last_brace + 1]
                                try:
                                    parsed_analysis = json.loads(json_str)
                                    print(f"      ✅ Successfully parsed JSON for {section_name}")
                                except Exception as e:
                                    print(f"      ❌ All parsing attempts failed for {section_name}")
                                    parsed_analysis = analysis_data
                            else:
                                parsed_analysis = analysis_data
                        else:
                            parsed_analysis = analysis_data
                    elif not parsed_analysis:
                        parsed_analysis = analysis_data

                    parsed_analysis = self._apply_cv_diagonal_cross_overrides(
                        section_name=section_name,
                        parsed_analysis=parsed_analysis,
                        image_path=image_file,
                    )
                    
                    self.analysis_collection[section_name] = {
                        "analysis": parsed_analysis,
                        "image_path": image_file
                    }
                    
                else:
                    print(f"   ⚠️ Missing analysis or image files for {section_name}")
                    print(f"   ℹ️ No PDF provided and no existing files found")
                    
            except Exception as e:
                print(f"   ❌ Error processing {section_name}: {e}")
        
        print(f"\n📊 Collected analyses for {len(self.analysis_collection)} sections")
        return len(self.analysis_collection)
    
    def _run_section_analysis(self, section_name: str, folder_name: str, progress_callback: callable = None) -> bool:
        """Run individual section analysis with provided PDF"""
        try:
            # Map section names to their test files (updated for new section names from post_review_sections_part2.json)
            test_file_map = {
            "section_1_1": "src/sections/test_section_1_1.py",
            "section_1_2": "src/sections/test_section_1_2.py", 
            "section_1_3": "src/sections/test_section_1_3_fixed.py",
            "section_1_4": "src/sections/test_section_1_4_improved.py",
            "section_2_1": "src/sections/test_section_2_1.py",
            "section_2_2_part1": "src/sections/test_section_2_2.py",  # Both parts use same test file
            "section_2_2_part2": "src/sections/test_section_2_2.py",  # Both parts use same test file
            "section_2_3": "src/sections/test_section_2_3.py",
            "section_2_4": "src/sections/test_section_2_4.py",
            "section_2_5": "src/sections/test_section_2_5.py",
            "section_3_2": "src/sections/test_section_3_2.py",
            "section_3_3": "src/sections/test_section_3_3.py",
            "section_3_4": "src/sections/test_section_3_4.py",
            "section_4_1_part1": "src/sections/test_section_4_1.py",  # Both parts use same test file
            "section_4_1_part2": "src/sections/test_section_4_1.py",  # Both parts use same test file
            "section_4_2": "src/sections/test_section_4_2.py",
            "section_4_3": "src/sections/test_section_4_3.py",
            "section_4_4": "src/sections/test_section_4_4.py",
            "section_4_5": "src/sections/test_section_4_5.py",
            "section_4_6": "src/sections/test_section_4_6.py"  # New section (will need test file)
            }
            
            test_file = test_file_map.get(section_name)
            if not test_file:
                print(f"   ❌ No test file found for {section_name}")
                return False
            
            # Build command to run test section with analysis-only mode (no PDF path needed)
            cmd = [
                sys.executable, 
                test_file, 
                "--analysis-only"
            ]
            
            # Get project root (go up from src/core/ to project root)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Check if test file exists from project root
            test_file_full_path = os.path.join(project_root, test_file)
            print(f"   🔧 Running: {' '.join(cmd)}")
            print(f"   🔧 Test file path: {test_file}")
            print(f"   🔧 Full test file path: {test_file_full_path}")
            print(f"   🔧 Test file exists: {os.path.exists(test_file_full_path)}")
            print(f"   🔧 Working directory: {project_root}")
            
            # Create UTF-8 environment for subprocess
            utf8_env = os.environ.copy()
            utf8_env['PYTHONUTF8'] = '1'
            utf8_env['PYTHONIOENCODING'] = 'utf-8'
            
            # Run the test section with UTF-8 environment from project root
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                env=utf8_env,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters
                cwd=project_root,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"   ✅ {section_name} analysis completed successfully")
                return True
            else:
                print(f"   ❌ {section_name} analysis failed:")
                print(f"   📤 stdout: {result.stdout}")
                print(f"   📤 stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ {section_name} analysis timed out (5 minutes)")
            return False
        except Exception as e:
            print(f"   ❌ Error running {section_name}: {e}")
            return False
    
    def _process_two_part_section_2_2(self, progress_callback: callable = None):
        """Process Section 2_2 as combined two-part analysis"""
        try:
            # Run analysis for both parts
            part1_folder = self.section_mapping["section_2_2_part1"]
            part2_folder = self.section_mapping["section_2_2_part2"]
            
            print(f"   🔄 Running section_2_2_part1 analysis...")
            success1 = self._run_section_analysis("section_2_2_part1", part1_folder, progress_callback)
            
            print(f"   🔄 Running section_2_2_part2 analysis...")  
            success2 = self._run_section_analysis("section_2_2_part2", part2_folder, progress_callback)
            
            if success1 and success2:
                print(f"   🔍 Looking for analysis files in respective part directories...")
                
                # The test file saves JSON files to respective part directories
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                part1_test_dir = os.path.join(project_root, "data", "test_sections", "section_2_2_part1_test")
                part2_test_dir = os.path.join(project_root, "data", "test_sections", "section_2_2_part2_test")
                
                part1_analysis_file = os.path.join(part1_test_dir, "section_2_2_part1_analysis.json")
                part2_analysis_file = os.path.join(part2_test_dir, "section_2_2_part2_analysis.json")
                part1_image_file = os.path.join(part1_test_dir, "section_2_2_part1_extracted.png")
                part2_image_file = os.path.join(part2_test_dir, "section_2_2_part2_extracted.png")
                
                if os.path.exists(part1_analysis_file) and os.path.exists(part2_analysis_file):
                    print(f"   🔄 Found TWO-PART Section 2_2 files in respective part directories")
                    print(f"      📋 Part 1: {os.path.basename(part1_analysis_file)} in {os.path.basename(part1_test_dir)}")
                    print(f"      📋 Part 2: {os.path.basename(part2_analysis_file)} in {os.path.basename(part2_test_dir)}")
                    
                    # Load Part 1 data
                    with open(part1_analysis_file, 'r', encoding='utf-8') as f:
                        part1_analysis = json.load(f)
                    part1_data = part1_analysis.get("parsed_data", part1_analysis)
                    part1_data = self._apply_cv_diagonal_cross_overrides(
                        section_name="section_2_2_part1",
                        parsed_analysis=part1_data,
                        image_path=part1_image_file,
                    )
                    
                    # Load Part 2 data
                    with open(part2_analysis_file, 'r', encoding='utf-8') as f:
                        part2_analysis = json.load(f)
                    part2_data = part2_analysis.get("parsed_data", part2_analysis)
                    part2_data = self._apply_cv_diagonal_cross_overrides(
                        section_name="section_2_2_part2",
                        parsed_analysis=part2_data,
                        image_path=part2_image_file,
                    )
                    
                    # Combine into new two-part format
                    parsed_analysis = {
                        "part1_data": part1_data,
                        "part2_data": part2_data,
                        "format": "two_part_section_2_2"
                    }
                    
                    # Store under unified "section_2_2" key
                    self.analysis_collection["section_2_2"] = {
                        "analysis": parsed_analysis,
                        "image_path": part1_image_file  # Use part1 image as primary
                    }
                    
                    print(f"   ✅ Successfully combined Section 2_2 two-part analysis")
                    print(f"   ✅ Successfully stored section_2_2 in analysis_collection")
                else:
                    print(f"   ❌ Missing analysis files for Section 2_2 parts")
            else:
                print(f"   ❌ Failed to analyze one or both Section 2_2 parts")
                
        except Exception as e:
            print(f"   ❌ Error processing two-part Section 2_2: {e}")
    
    def _process_two_part_section_4_1(self, progress_callback: callable = None):
        """Process Section 4_1 as combined two-part analysis"""
        try:
            # Run analysis for both parts
            part1_folder = self.section_mapping["section_4_1_part1"]
            part2_folder = self.section_mapping["section_4_1_part2"]
            
            print(f"   🔄 Running section_4_1_part1 analysis...")
            success1 = self._run_section_analysis("section_4_1_part1", part1_folder, progress_callback)
            
            print(f"   🔄 Running section_4_1_part2 analysis...")  
            success2 = self._run_section_analysis("section_4_1_part2", part2_folder, progress_callback)
            
            if success1 and success2:
                print(f"   🔍 Looking for analysis files in respective part directories...")
                
                # The test file saves JSON files to respective part directories
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                part1_test_dir = os.path.join(project_root, "data", "test_sections", "section_4_1_part1_test")
                part2_test_dir = os.path.join(project_root, "data", "test_sections", "section_4_1_part2_test")
                
                part1_analysis_file = os.path.join(part1_test_dir, "section_4_1_part1_analysis.json")
                part2_analysis_file = os.path.join(part2_test_dir, "section_4_1_part2_analysis.json")
                part1_image_file = os.path.join(part1_test_dir, "section_4_1_part1_extracted.png")
                part2_image_file = os.path.join(part2_test_dir, "section_4_1_part2_extracted.png")
                
                if os.path.exists(part1_analysis_file) and os.path.exists(part2_analysis_file):
                    print(f"   🔄 Found TWO-PART Section 4_1 files in respective part directories")
                    print(f"      📋 Part 1: {os.path.basename(part1_analysis_file)} in {os.path.basename(part1_test_dir)}")
                    print(f"      📋 Part 2: {os.path.basename(part2_analysis_file)} in {os.path.basename(part2_test_dir)}")
                    
                    # Load Part 1 data
                    with open(part1_analysis_file, 'r', encoding='utf-8') as f:
                        part1_analysis = json.load(f)
                    part1_data = part1_analysis.get("parsed_data", part1_analysis)
                    part1_data = self._apply_cv_diagonal_cross_overrides(
                        section_name="section_4_1_part1",
                        parsed_analysis=part1_data,
                        image_path=part1_image_file,
                    )
                    
                    # Load Part 2 data
                    with open(part2_analysis_file, 'r', encoding='utf-8') as f:
                        part2_analysis = json.load(f)
                    part2_data = part2_analysis.get("parsed_data", part2_analysis)
                    part2_data = self._apply_cv_diagonal_cross_overrides(
                        section_name="section_4_1_part2",
                        parsed_analysis=part2_data,
                        image_path=part2_image_file,
                    )
                    
                    # Combine into new two-part format
                    parsed_analysis = {
                        "part1_data": part1_data,
                        "part2_data": part2_data,
                        "format": "two_part_section_4_1"
                    }
                    
                    # Store under unified "section_4_1" key
                    self.analysis_collection["section_4_1"] = {
                        "analysis": parsed_analysis,
                        "image_path": part1_image_file  # Use part1 image as primary
                    }
                    
                    print(f"   ✅ Successfully combined Section 4_1 two-part analysis")
                    print(f"   ✅ Successfully stored section_4_1 in analysis_collection")
                else:
                    print(f"   ❌ Missing analysis files for Section 4_1 parts")
            else:
                print(f"   ❌ Failed to analyze one or both Section 4_1 parts")
                
        except Exception as e:
            print(f"   ❌ Error processing two-part Section 4_1: {e}")
    
    def apply_unified_implementations(self, progress_callback: callable = None):
        """
        Step 2: Apply all collected analyses to a single Word document
        
        Args:
            progress_callback (callable, optional): Function to call for UI progress updates
            
        Returns:
            tuple: (final_document_path, processing_summary)
        """
        print("\n🔧 STEP 2: APPLYING UNIFIED IMPLEMENTATIONS")
        print("=" * 80)
        
        if not self.analysis_collection:
            print("❌ No analyses collected - cannot proceed with implementation")
            return None
        
        # Create unified processor with custom output directory
        processor = UnifiedSectionImplementations(self.base_document, output_dir=self.output_dir)
        
        # Apply all sections to single document
        final_document, total_changes = processor.process_all_sections(self.analysis_collection, progress_callback)
        
        # Create processing summary
        processing_summary = {
            'total_sections': len(self.analysis_collection),
            'successful_sections': len(self.analysis_collection),  # Will be updated based on actual results
            'failed_sections': 0,
            'skipped_sections': 0,
            'no_change_sections': 0,
            'total_changes_applied': total_changes
        }
        
        return final_document, processing_summary

    def _apply_cv_diagonal_cross_overrides(self, section_name: str, parsed_analysis, image_path: str):
        """
        Replace diagonal/cross deletion-mark decisions with OpenCV detection,
        while keeping AI-driven handwriting interpretation for everything else.
        """
        if not isinstance(parsed_analysis, dict):
            return parsed_analysis

        if not image_path or not os.path.exists(image_path):
            return parsed_analysis

        if detect_diagonal_cross is None:
            return parsed_analysis

        try:
            with Image.open(image_path) as image:
                if image.mode != "RGB":
                    image = image.convert("RGB")

                left_box_analysis = parsed_analysis.get("left_box_analysis")
                right_box_analysis = parsed_analysis.get("right_box_analysis")

                if isinstance(left_box_analysis, dict) and isinstance(right_box_analysis, dict):
                    regions = split_left_right_regions(image)
                    region_detection = detect_diagonal_cross_in_regions(image, regions)

                    left_has_marks = bool(region_detection.get("left", {}).get("has_diagonal_cross", False))
                    right_has_marks = bool(region_detection.get("right", {}).get("has_diagonal_cross", False))

                    self._apply_box_level_overrides(left_box_analysis, left_has_marks)
                    self._apply_box_level_overrides(right_box_analysis, right_has_marks)

                    row_rule = parsed_analysis.get("row_deletion_rule")
                    if not isinstance(row_rule, dict):
                        row_rule = {}
                        parsed_analysis["row_deletion_rule"] = row_rule
                    self._apply_row_rule_overrides(row_rule, left_has_marks, right_has_marks)

                    parsed_analysis["_cv_detection"] = {
                        "source": "opencv",
                        "scope": "left_right_boxes",
                        "left": region_detection.get("left", {}),
                        "right": region_detection.get("right", {}),
                        "section": section_name,
                    }
                else:
                    overall_detection = detect_diagonal_cross(image)
                    has_marks = bool(overall_detection.get("has_diagonal_cross", False))

                    self._apply_recursive_diagonal_gating(parsed_analysis, has_marks)
                    parsed_analysis["_cv_detection"] = {
                        "source": "opencv",
                        "scope": "full_section",
                        "overall": overall_detection,
                        "section": section_name,
                    }
        except Exception as e:
            print(f"   ⚠️ CV diagonal/cross override skipped for {section_name}: {e}")

        return parsed_analysis

    def _apply_box_level_overrides(self, box_analysis: dict, box_has_marks: bool):
        if not isinstance(box_analysis, dict):
            return

        existing_deletion = bool(box_analysis.get("has_deletion_marks", False))
        existing_interruptions = bool(box_analysis.get("has_interruptions", False))

        box_analysis["has_deletion_marks"] = existing_deletion or box_has_marks
        box_analysis["has_interruptions"] = existing_interruptions or box_has_marks

        self._apply_recursive_diagonal_gating(box_analysis, box_has_marks)

    def _apply_row_rule_overrides(self, row_rule: dict, left_has_marks: bool, right_has_marks: bool):
        if not isinstance(row_rule, dict):
            return

        both = left_has_marks and right_has_marks

        def _merge_bool(existing_value, detected_value: bool) -> bool:
            return bool(existing_value) or bool(detected_value)

        if "left_box_completely_marked" in row_rule:
            row_rule["left_box_completely_marked"] = _merge_bool(row_rule.get("left_box_completely_marked"), left_has_marks)
        if "right_box_completely_marked" in row_rule:
            row_rule["right_box_completely_marked"] = _merge_bool(row_rule.get("right_box_completely_marked"), right_has_marks)
        if "left_box_all_deletion_marks" in row_rule:
            row_rule["left_box_all_deletion_marks"] = _merge_bool(row_rule.get("left_box_all_deletion_marks"), left_has_marks)
        if "right_box_all_deletion_marks" in row_rule:
            row_rule["right_box_all_deletion_marks"] = _merge_bool(row_rule.get("right_box_all_deletion_marks"), right_has_marks)
        if "left_box_has_diagonal_marks" in row_rule:
            row_rule["left_box_has_diagonal_marks"] = _merge_bool(row_rule.get("left_box_has_diagonal_marks"), left_has_marks)
        if "right_box_has_diagonal_marks" in row_rule:
            row_rule["right_box_has_diagonal_marks"] = _merge_bool(row_rule.get("right_box_has_diagonal_marks"), right_has_marks)
        if "both_boxes_have_marks" in row_rule:
            row_rule["both_boxes_have_marks"] = _merge_bool(row_rule.get("both_boxes_have_marks"), both)
        if "delete_entire_row" in row_rule:
            row_rule["delete_entire_row"] = _merge_bool(row_rule.get("delete_entire_row"), both)
        if "should_delete_entire_row" in row_rule:
            row_rule["should_delete_entire_row"] = _merge_bool(row_rule.get("should_delete_entire_row"), both)

    def _apply_recursive_diagonal_gating(self, data, has_diagonal_cross: bool):
        if isinstance(data, dict):
            for _, value in data.items():
                self._apply_recursive_diagonal_gating(value, has_diagonal_cross)

            if "has_diagonal_cross" in data:
                data["has_diagonal_cross"] = has_diagonal_cross

            if self._is_diagonal_cross_context(data):
                for key, value in list(data.items()):
                    if key.startswith("should_delete") and isinstance(value, bool):
                        data[key] = value and has_diagonal_cross

        elif isinstance(data, list):
            for item in data:
                self._apply_recursive_diagonal_gating(item, has_diagonal_cross)

    def _is_diagonal_cross_context(self, item: dict) -> bool:
        if not isinstance(item, dict):
            return False

        if "has_diagonal_cross" in item:
            return True

        diagonal_terms = ("diagonal", "cross", "x_mark", "x mark", "crossed", "cross-out")
        candidate_fields = (
            "interruption_type",
            "mark_type",
            "deletion_type",
            "interruption_description",
            "mark_description",
            "deletion_reason",
        )

        for field in candidate_fields:
            value = item.get(field, "")
            if isinstance(value, str):
                lower_value = value.lower()
                if any(term in lower_value for term in diagonal_terms):
                    return True

        return False
    
    def run_complete_process(self):
        """Run the complete unified processing workflow"""
        print("🚀 MASTER UNIFIED PROCESSOR - COMPLETE WORKFLOW")
        print("📄 Base document: BLANK Post_Review_Action_Plan(6).docx")
        print("🎯 New approach: Collect all analyses → Apply to single document")
        print("=" * 80)
        
        start_time = time.time()
        
        # Step 1: Collect all analyses
        collected_count = self.run_analysis_extraction_only()
        
        if collected_count == 0:
            print("\n❌ No section analyses found - please run individual section tests first")
            return
        
        # Step 2: Apply unified implementations
        result = self.apply_unified_implementations()
        if result:
            final_document, processing_summary = result
        else:
            final_document = None
            processing_summary = None
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Summary
        print(f"\n🎉 UNIFIED PROCESSING COMPLETE!")
        print("=" * 80)
        print(f"⏱️ Total processing time: {processing_time:.1f} seconds")
        print(f"📊 Sections processed: {collected_count}")
        
        if final_document:
            print(f"💾 FINAL UNIFIED DOCUMENT: {final_document}")
            print(f"🎯 All {collected_count} section implementations applied to single document")
        else:
            print("❌ Failed to create final unified document")
        
        return final_document
    
    def _find_most_recent_files(self, folder_name: str, section_name: str) -> tuple:
        """Find the most recent analysis and image files, prioritizing FIXED versions"""
        import glob
        import os
        
        print(f"   🔍 DEBUG _find_most_recent_files:")
        print(f"      📁 folder_name: {folder_name}")  
        print(f"      📝 section_name: {section_name}")
        print(f"      📁 folder exists: {os.path.exists(folder_name)}")
        
        if os.path.exists(folder_name):
            all_files = os.listdir(folder_name)
            print(f"      📋 All files in folder: {all_files}")
        
        # Priority 1: Look for FIXED versions
        fixed_analysis = os.path.join(folder_name, f"{section_name}_analysis_FIXED.json")
        fixed_image = os.path.join(folder_name, f"{section_name}_extracted_FIXED.png")
        
        print(f"      🔧 Looking for FIXED analysis: {fixed_analysis}")
        print(f"      🔧 Looking for FIXED image: {fixed_image}")
        
        if os.path.exists(fixed_analysis) and os.path.exists(fixed_image):
            print(f"   🔧 Using FIXED versions")
            return fixed_analysis, fixed_image
        
        # Priority 2: Look for most recent regular versions
        analysis_pattern = os.path.join(folder_name, f"{section_name}_analysis*.json")
        image_pattern = os.path.join(folder_name, f"{section_name}_extracted*.png")
        
        print(f"      🔍 Analysis pattern: {analysis_pattern}")
        print(f"      🔍 Image pattern: {image_pattern}")
        
        analysis_files = glob.glob(analysis_pattern)
        image_files = glob.glob(image_pattern)
        
        print(f"      📋 Found analysis files: {analysis_files}")
        print(f"      📋 Found image files: {image_files}")
        
        # Filter out FIXED versions from regular search since we already checked them
        analysis_files = [f for f in analysis_files if "_FIXED" not in f]
        image_files = [f for f in image_files if "_FIXED" not in f]
        
        print(f"      📋 Filtered analysis files: {analysis_files}")
        print(f"      📋 Filtered image files: {image_files}")
        
        if analysis_files and image_files:
            # Get most recent files by modification time
            latest_analysis = max(analysis_files, key=os.path.getmtime)
            latest_image = max(image_files, key=os.path.getmtime)
            print(f"   📅 Using most recent files: {os.path.basename(latest_analysis)}, {os.path.basename(latest_image)}")
            return latest_analysis, latest_image
        
        # Fallback to original naming if no matches
        original_analysis = os.path.join(folder_name, f"{section_name}_analysis.json")
        original_image = os.path.join(folder_name, f"{section_name}_extracted.png")
        
        print(f"      📄 Looking for original analysis: {original_analysis}")
        print(f"      📄 Looking for original image: {original_image}")
        print(f"      📄 Original analysis exists: {os.path.exists(original_analysis)}")
        print(f"      📄 Original image exists: {os.path.exists(original_image)}")
        
        if os.path.exists(original_analysis) and os.path.exists(original_image):
            print(f"   📅 Using original files")
            return original_analysis, original_image
        
        print(f"   ❌ No matching files found!")
        return None, None

def main():
    """Run the master unified processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Master Unified Post Review Processor')
    parser.add_argument('--pdf-path', type=str, help='Path to the annotated PDF document')
    parser.add_argument('--word-path', type=str, help='Path to the base Word document')
    parser.add_argument('--output-name', type=str, help='Output file name prefix')
    parser.add_argument('--output-dir', type=str, help='Output directory')
    
    args = parser.parse_args()
    
    # Initialize processor with command-line arguments
    processor = MasterUnifiedProcessor(
        pdf_path=args.pdf_path,
        word_path=args.word_path,
        output_dir=args.output_dir
    )
    
    # Store output name for later use
    if args.output_name:
        processor.output_name_prefix = args.output_name
    
    processor.run_complete_process()

if __name__ == "__main__":
    main()
