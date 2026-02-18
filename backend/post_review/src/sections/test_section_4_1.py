#!/usr/bin/env python3
"""

# This file requires pre-extracted images from pdf_section_splitter.py
# Run: splitter = PDFSectionSplitter(pdf_path); splitter.extract_all_sections()
# Then this file will work with the pre-extracted section image

Test Section 4_1 Implementation
Uses all existing rules + NEW arrow-based text replacement
"""

import os
import json
import base64
import requests
from pathlib import Path

from PIL import Image

from docx import Document
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.section_implementations_reference import SectionImplementationsReference

# This file is designed to work only through the Post-Review UI system
# Run: python post_review_modern_ui.py
# Do not run this file directly

class Section4_1Tester:
    def __init__(self, pdf_path=None):
        self.section_name = "Section_4_1"
        
        # Two-part section - no main test directory needed, uses part directories only
        project_root = os.path.dirname(os.path.abspath(__file__))
        # self.test_dir no longer used - parts save to their own directories
        # This test section works with pre-extracted PNG images only
        # PDF sectioning is handled by PDFSectionSplitter
        # Word processing is handled by unified_section_implementations.py
        
        # Note: No longer creating main test directory - using part directories only
        # os.makedirs(self.test_dir, exist_ok=True)
        
        # Load OpenAI API key
        from dotenv import load_dotenv
        # Load environment variables from project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_path = os.path.join(project_root, '.env')
        load_dotenv(env_path)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def load_part1_image(self) -> str:
        """Load part1 specific image"""
        try:
            # Get project root (go up from src/sections/ to project root)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(project_root, "data", "test_sections", "section_4_1_part1_test", "section_4_1_part1_extracted.png")
            
            if os.path.exists(image_path):
                print(f"✅ Found Part 1 image: {image_path}")
                # Verify it's a valid image
                try:
                    with Image.open(image_path) as img:
                        print(f"   📏 Part 1 image size: {img.size}")
                        return image_path
                except Exception as e:
                    print(f"❌ Invalid Part 1 image file: {e}")
                    return None
            else:
                print(f"❌ Part 1 image not found: {image_path}")
                return None
                
        except Exception as e:
            print(f"Error loading Part 1 image: {e}")
            return None
    
    def load_part2_image(self) -> str:
        """Load part2 specific image"""
        try:
            # Get project root (go up from src/sections/ to project root)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(project_root, "data", "test_sections", "section_4_1_part2_test", "section_4_1_part2_extracted.png")
            
            if os.path.exists(image_path):
                print(f"✅ Found Part 2 image: {image_path}")
                # Verify it's a valid image
                try:
                    with Image.open(image_path) as img:
                        print(f"   📏 Part 2 image size: {img.size}")
                        return image_path
                except Exception as e:
                    print(f"❌ Invalid Part 2 image file: {e}")
                    return None
            else:
                print(f"❌ Part 2 image not found: {image_path}")
                return None
                
        except Exception as e:
            print(f"Error loading Part 2 image: {e}")
            return None

    def load_extracted_image(self) -> str:
        """Load pre-extracted section image (extracted by pdf_section_splitter.py) - LEGACY METHOD"""
        try:
            # Get project root (go up from src/sections/ to project root)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Check multiple possible locations for the extracted images
            possible_locations = [
                # New format: separate part directories
                os.path.join(project_root, "data", "test_sections", "section_4_1_part1_test", "section_4_1_part1_extracted.png"),
                os.path.join(project_root, "data", "test_sections", "section_4_1_part2_test", "section_4_1_part2_extracted.png"),
                # No legacy format needed - removed main directory
            ]
            
            for image_path in possible_locations:
                if os.path.exists(image_path):
                    print(f"✅ Found pre-extracted image: {image_path}")
                    
                    # Verify it's a valid image
                    try:
                        with Image.open(image_path) as img:
                            print(f"   📏 Image size: {img.size}")
                            return image_path
                    except Exception as e:
                        print(f"❌ Invalid image file: {e}")
                        continue  # Try next location
            
            print(f"❌ Pre-extracted image not found in any of these locations:")
            for location in possible_locations:
                print(f"   - {location}")
            print(f"   💡 Make sure to run pdf_section_splitter.py first!")
            return None
                
        except Exception as e:
            print(f"Error loading pre-extracted image: {e}")
            return None
    
    def get_section_4_1_part1_analysis_prompt(self) -> str:
        """
        PROMPT for Section 4_1 PART 1 - Pay off debt + first dot point
        """
        return """
        Analyze this Section 4_1 PART 1 for DELETION MARKS AND TEXT REPLACEMENT:
        
        SECTION LAYOUT: This section has TWO BOXES side by side (LEFT BOX and RIGHT BOX)
        
        PART 1 CONTENT EXPECTED:
        - Left box: "Pay off debt" 
        - Right box: "We have moved funds from various accounts to pay off ..."
        
        CRITICAL RULES FOR PART 1:
        
        RULE 1: INDIVIDUAL DELETIONS
        - Look for handwritten diagonal lines or X marks (crosses) that interrupt ANY text
        - If diagonal/cross interrupts a sentence within a dot point → DELETE that specific sentence
        - CONTINUOUS DIAGONAL LINES: A single diagonal line may start at one sentence, pass through others, and end at another
        - ALL sentences that the continuous line passes through should be marked for deletion
        - For single dot points with multiple sentences, delete only the interrupted sentences
        
        RULE 2: ENHANCED ROW DELETION (Critical Override)
        - If BOTH left box AND right box have ANY diagonal/cross marks (even in white space)
        - Then note this for potential ENTIRE ROW deletion (will be combined with Part 2 analysis)
        - This rule triggers when BOTH boxes have marks, regardless of what content is interrupted
        
        RULE 3: ARROW-BASED TEXT REPLACEMENT (Critical)
        - Look for STRIKETHROUGH text with an ARROW pointing to replacement text
        - Pattern: [Original text with line through it] → [Arrow] → [New handwritten text]
        - The strikethrough text should be REPLACED with the handwritten text the arrow points to
        - Example: "~~old text~~" → "new handwritten text"
        
        RESPONSE FORMAT (JSON):
        {
            "left_box_analysis": {
                "has_deletion_marks": boolean,
                "has_replacement_marks": boolean,
                "total_items": number,
                "interrupted_items": number,
                "replacement_items": number,
                "all_items_interrupted": boolean,
                "deletion_details": [
                    {
                        "item_number": number,
                        "item_text": "exact text content",
                        "has_diagonal_cross": boolean,
                        "should_delete": boolean
                    }
                ],
                "replacement_details": [
                    {
                        "item_number": number,
                        "original_text": "text with strikethrough",
                        "replacement_text": "handwritten replacement text",
                        "has_arrow_indicator": boolean,
                        "should_replace": boolean
                    }
                ]
            },
            "right_box_analysis": {
                "has_deletion_marks": boolean,
                "has_replacement_marks": boolean,
                "total_items": number,
                "interrupted_items": number,
                "replacement_items": number,
                "all_items_interrupted": boolean,
                "continuous_line_detected": boolean,
                "continuous_line_description": "description if applicable",
                "deletion_details": [
                    {
                        "item_number": number,
                        "item_text": "exact text content", 
                        "has_diagonal_cross": boolean,
                        "should_delete": boolean
                    }
                ],
                "replacement_details": [
                    {
                        "item_number": number,
                        "original_text": "text with strikethrough",
                        "replacement_text": "handwritten replacement text",
                        "has_arrow_indicator": boolean,
                        "should_replace": boolean
                    }
                ]
            },
            "part1_row_deletion_assessment": {
                "left_box_has_marks": boolean,
                "right_box_has_marks": boolean,
                "part1_contribution_to_row_deletion": boolean,
                "explanation": "explanation for Part 1's contribution"
            },
            "visual_description": "comprehensive description of all deletion marks and replacement arrows detected in Part 1"
        }
        """
    
    def get_section_4_1_part2_analysis_prompt(self) -> str:
        """
        PROMPT for Section 4_1 PART 2 - Empty left box + mortgage dot point
        """
        return """
        Analyze this Section 4_1 PART 2 for DELETION MARKS AND TEXT REPLACEMENT:
        
        SECTION LAYOUT: This section has TWO BOXES side by side (LEFT BOX and RIGHT BOX)
        
        PART 2 CONTENT EXPECTED:
        - Left box: Empty/no content 
        - Right box: "Continue to pay down your principal mortgage. Please refer to the Debt Reduction Calculator on our website. http://www.mlfs.com.au/debt-reduction-calculator/"
        
        CRITICAL RULES FOR PART 2:
        
        RULE 1: INDIVIDUAL DELETIONS
        - Look for handwritten diagonal lines or X marks (crosses) that interrupt ANY text
        - If diagonal/cross interrupts a sentence within a dot point → DELETE that specific sentence
        - CONTINUOUS DIAGONAL LINES: A single diagonal line may start at one sentence, pass through others, and end at another
        - ALL sentences that the continuous line passes through should be marked for deletion
        - For single dot points with multiple sentences, delete only the interrupted sentences
        
        RULE 2: ENHANCED ROW DELETION (Critical Override)
        - If left box has ANY diagonal/cross marks (even if empty) AND right box has marks
        - Then note this for potential ENTIRE ROW deletion (will be combined with Part 1 analysis)
        - This rule triggers when BOTH boxes have marks, regardless of what content is interrupted
        
        RULE 3: ARROW-BASED TEXT REPLACEMENT (Critical)
        - Look for STRIKETHROUGH text with an ARROW pointing to replacement text
        - Pattern: [Original text with line through it] → [Arrow] → [New handwritten text]
        - The strikethrough text should be REPLACED with the handwritten text the arrow points to
        - Example: "~~old text~~" → "new handwritten text"
        
        RESPONSE FORMAT (JSON):
        {
            "left_box_analysis": {
                "has_content": false,
                "has_deletion_marks": boolean,
                "has_replacement_marks": boolean,
                "description": "Left box is empty for Part 2"
            },
            "right_box_analysis": {
                "has_deletion_marks": boolean,
                "has_replacement_marks": boolean,
                "total_items": number,
                "interrupted_items": number,
                "replacement_items": number,
                "all_items_interrupted": boolean,
                "continuous_line_detected": boolean,
                "continuous_line_description": "description if applicable",
                "deletion_details": [
                    {
                        "item_number": number,
                        "item_text": "exact text content", 
                        "has_diagonal_cross": boolean,
                        "should_delete": boolean
                    }
                ],
                "replacement_details": [
                    {
                        "item_number": number,
                        "original_text": "text with strikethrough",
                        "replacement_text": "handwritten replacement text",
                        "has_arrow_indicator": boolean,
                        "should_replace": boolean
                    }
                ]
            },
            "part2_row_deletion_assessment": {
                "left_box_has_marks": boolean,
                "right_box_has_marks": boolean,
                "part2_contribution_to_row_deletion": boolean,
                "explanation": "explanation for Part 2's contribution"
            },
            "visual_description": "comprehensive description of all deletion marks and replacement arrows detected in Part 2"
        }
        """
    
    def analyze_section_4_1_part1(self, image_path: str) -> dict:
        """Analyze Section 4_1 Part 1 with GPT-4o"""
        try:
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            prompt = self.get_section_4_1_part1_analysis_prompt()
            
            payload = {
                "model": "gpt-4.1",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.1
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=90)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return {
                "raw_analysis": content,
                "success": True
                }
                
        except Exception as e:
            return {
                "raw_analysis": f"Error analyzing Section 4_1 Part 1: {str(e)}",
                "success": False
            }
    
    def analyze_section_4_1_part2(self, image_path: str) -> dict:
        """Analyze Section 4_1 Part 2 with GPT-4o"""
        try:
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            prompt = self.get_section_4_1_part2_analysis_prompt()
            
            payload = {
                "model": "gpt-4.1",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.1
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=90)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            return {
                "raw_analysis": content,
                "success": True
            }
            
        except Exception as e:
            return {
                "raw_analysis": f"Error analyzing Section 4_1 Part 2: {str(e)}",
                "success": False
            }
    
    def extract_json_from_analysis(self, raw_analysis: str) -> dict:
        """Extract JSON from GPT-4o analysis response"""
        try:
            # Look for JSON in code blocks
            if "```json" in raw_analysis:
                start = raw_analysis.find("```json") + 7
                end = raw_analysis.find("```", start)
                json_str = raw_analysis[start:end].strip()
                return json.loads(json_str)
            
            # Look for JSON without code blocks
            import re
            json_match = re.search(r'\{.*\}', raw_analysis, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
                
            return {}
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return {}

    def save_analysis_results(self, analysis_data: dict):
        """Save analysis results to JSON file for unified processing - LEGACY METHOD"""
        try:
            # Note: This method is legacy - two-part sections save to part directories
            print("⚠️ save_analysis_results is legacy for two-part sections")
            return  # Skip saving to main directory
            # analysis_file = os.path.join(self.test_dir, "section_4_1_analysis.json")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Analysis saved: {analysis_file}")
        except Exception as e:
            print(f"❌ Error saving analysis: {e}")
    
    def run_analysis_only(self, progress_callback=None):
        """Run only image extraction and analysis (no Word processing) - now handles two parts"""
        print(f"Starting Section_4_1 Analysis - TWO-PART FORMAT")
        print("Analysis only - Word processing handled by unified processor")
        print("=" * 80)
        
        # Step 1A: Load Part 1 image and analyze
        if progress_callback:
            progress_callback(1, 4, self.section_name, "Loading Part 1 image...")
        
        print(f"📊 Step 1A: Loading Part 1 image...")
        part1_image_path = self.load_part1_image()
        if not part1_image_path:
            print(f"❌ Section_4_1 Part 1 Analysis Failed!")
            return False
        print(f"✅ Part 1 image loaded: {part1_image_path}")
        
        # Step 2A: Run Part 1 analysis
        if progress_callback:
            progress_callback(2, 4, self.section_name, "Analyzing Part 1 with GPT-4o...")
        
        print(f"🤖 Step 2A: Analyzing Section_4_1 Part 1 with GPT-4o...")
        part1_result = self.analyze_section_4_1_part1(part1_image_path)
        
        if not part1_result["success"]:
            print(f"❌ Part 1 GPT-4o analysis failed: {part1_result.get('raw_analysis', 'Unknown error')}")
            return False
        
        part1_data = self.extract_json_from_analysis(part1_result["raw_analysis"])
        
        # Save Part 1 results to part1 directory
        part1_analysis = {
            "section_name": "Section_4_1_Part1",
            "raw_analysis": part1_result["raw_analysis"],
            "parsed_data": part1_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get project root (go up from src/sections/ to project root)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        part1_dir = os.path.join(project_root, "data", "test_sections", "section_4_1_part1_test")
        os.makedirs(part1_dir, exist_ok=True)
        part1_file = os.path.join(part1_dir, "section_4_1_part1_analysis.json")
        with open(part1_file, 'w', encoding='utf-8') as f:
            json.dump(part1_analysis, f, indent=2, ensure_ascii=False)
        print(f"💾 Part 1 analysis saved: {part1_file}")
        
        # Step 1B: Load Part 2 image
        print(f"📊 Step 1B: Loading Part 2 image...")
        part2_image_path = self.load_part2_image()
        if not part2_image_path:
            print(f"❌ Section_4_1 Part 2 Analysis Failed!")
            return False
        print(f"✅ Part 2 image loaded: {part2_image_path}")
        
        # Step 2B: Run Part 2 analysis
        if progress_callback:
            progress_callback(3, 4, self.section_name, "Analyzing Part 2 with GPT-4o...")
        
        print(f"🤖 Step 2B: Analyzing Section_4_1 Part 2 with GPT-4o...")
        part2_result = self.analyze_section_4_1_part2(part2_image_path)
        
        if not part2_result["success"]:
            print(f"❌ Part 2 GPT-4o analysis failed: {part2_result.get('raw_analysis', 'Unknown error')}")
            return False
        
        part2_data = self.extract_json_from_analysis(part2_result["raw_analysis"])
        
        # Save Part 2 results to part2 directory
        part2_analysis = {
            "section_name": "Section_4_1_Part2",
            "raw_analysis": part2_result["raw_analysis"],
            "parsed_data": part2_data,
            "timestamp": datetime.now().isoformat()
        }
        
        part2_dir = os.path.join(project_root, "data", "test_sections", "section_4_1_part2_test")
        os.makedirs(part2_dir, exist_ok=True)
        part2_file = os.path.join(part2_dir, "section_4_1_part2_analysis.json")
        with open(part2_file, 'w', encoding='utf-8') as f:
            json.dump(part2_analysis, f, indent=2, ensure_ascii=False)
        print(f"💾 Part 2 analysis saved: {part2_file}")
        
        if progress_callback:
            progress_callback(4, 4, self.section_name, "Analysis complete...")
        
        print(f"✅ Section_4_1 Two-Part Analysis Complete!")
        print(f"📄 Saved: section_4_1_part1_analysis.json")
        print(f"📄 Saved: section_4_1_part2_analysis.json")
        print("💼 Ready for unified Word processing (parts will be combined)")
        
        return True
    
    def run_section_4_1_test(self):
        """Run complete Section 4_1 test - now split into Part 1 and Part 2"""
        print("🧪 Section 4_1 Individual Test - TWO-PART FORMAT")
        print("=" * 70)
        
        # Step 1: Extract section image
        print("📷 Step 1: Extracting Section 4_1 image...")
        section_image_path = self.load_extracted_image()
        if not section_image_path:
            print("❌ Failed to extract Section 4_1 image")
            return
        
        print(f"   💾 Section image loaded: {section_image_path}")
        
        # Step 2A: Analyze PART 1 with GPT-4o
        print("\n🔍 Step 2A: Analyzing PART 1 with GPT-4o (Pay off debt + first dot point)...")
        part1_result = self.analyze_section_4_1_part1(section_image_path)
        
        if not part1_result["success"]:
            print("❌ Part 1 Analysis failed")
            return
        
        part1_data = self.extract_json_from_analysis(part1_result["raw_analysis"])
        
        # Save Part 1 analysis results to part1 directory
        # Get project root (go up from src/sections/ to project root)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        part1_dir = os.path.join(project_root, "data", "test_sections", "section_4_1_part1_test")
        os.makedirs(part1_dir, exist_ok=True)
        part1_file = os.path.join(part1_dir, "section_4_1_part1_analysis.json")
        with open(part1_file, 'w', encoding='utf-8') as f:
            json.dump({
                "raw_analysis": part1_result["raw_analysis"],
                "parsed_data": part1_data
            }, f, indent=2, ensure_ascii=False)
        print(f"   💾 Part 1 analysis saved: {part1_file}")
        
        # Step 2B: Analyze PART 2 with GPT-4o
        print("\n🔍 Step 2B: Analyzing PART 2 with GPT-4o (Empty left + mortgage dot point)...")
        part2_result = self.analyze_section_4_1_part2(section_image_path)
        
        if not part2_result["success"]:
            print("❌ Part 2 Analysis failed")
            return
        
        part2_data = self.extract_json_from_analysis(part2_result["raw_analysis"])
        
        # Save Part 2 analysis results to part2 directory
        part2_dir = os.path.join(project_root, "data", "test_sections", "section_4_1_part2_test")
        os.makedirs(part2_dir, exist_ok=True)
        part2_file = os.path.join(part2_dir, "section_4_1_part2_analysis.json")
        with open(part2_file, 'w', encoding='utf-8') as f:
            json.dump({
                "raw_analysis": part2_result["raw_analysis"],
                "parsed_data": part2_data
            }, f, indent=2, ensure_ascii=False)
        print(f"   💾 Part 2 analysis saved: {part2_file}")
        
        # Step 3: Display analysis results for both parts
        print("\n📊 Step 3: Analysis Results:")
        
        print("\n   🎯 PART 1 RESULTS (Pay off debt):")
        left_box = part1_data.get("left_box_analysis", {})
        right_box = part1_data.get("right_box_analysis", {})
        row_assessment = part1_data.get("part1_row_deletion_assessment", {})
        
        print(f"      📦 Left Box:")
        print(f"         • Has deletion marks: {left_box.get('has_deletion_marks', False)}")
        print(f"         • Has replacement marks: {left_box.get('has_replacement_marks', False)}")
        print(f"         • Total items: {left_box.get('total_items', 0)}")
        
        print(f"      📦 Right Box:")
        print(f"         • Has deletion marks: {right_box.get('has_deletion_marks', False)}")
        print(f"         • Has replacement marks: {right_box.get('has_replacement_marks', False)}")
        print(f"         • Total items: {right_box.get('total_items', 0)}")
        
        print(f"      🔄 Row Deletion Assessment:")
        print(f"         • Part 1 contribution to row deletion: {row_assessment.get('part1_contribution_to_row_deletion', False)}")
        
        print("\n   🎯 PART 2 RESULTS (Mortgage):")
        left_box2 = part2_data.get("left_box_analysis", {})
        right_box2 = part2_data.get("right_box_analysis", {})
        row_assessment2 = part2_data.get("part2_row_deletion_assessment", {})
        
        print(f"      📦 Left Box:")
        print(f"         • Has content: {left_box2.get('has_content', False)}")
        print(f"         • Description: {left_box2.get('description', 'None')}")
        
        print(f"      📦 Right Box:")
        print(f"         • Has deletion marks: {right_box2.get('has_deletion_marks', False)}")
        print(f"         • Has replacement marks: {right_box2.get('has_replacement_marks', False)}")
        print(f"         • Total items: {right_box2.get('total_items', 0)}")
        
        print(f"      🔄 Row Deletion Assessment:")
        print(f"         • Part 2 contribution to row deletion: {row_assessment2.get('part2_contribution_to_row_deletion', False)}")
        
        print("\n📝 Analysis-only mode: Word document processing handled by unified_section_implementations.py")
        print("✅ Both Part 1 and Part 2 analysis completed successfully!")
    
    def run_test(self):
        """Run the complete Section 4_1 test"""
        print("🚀 Starting Section 4_1 Test (All rules + Arrow-based text replacement)")
        print("📄 Test section: Section 4_1 - PNG image analysis only")
        print("🔍 Section: Section_4_1")
        print("=" * 80)
        
        # Step 1: Load PDF and cut section
        print("📊 Step 1: Loading PDF and cutting Section_4_1...")
        section_image_path = self.load_extracted_image()
        if not section_image_path:
            return
        print(f"✅ Section image loaded: {section_image_path}")
        
        # Step 2: Analyze with GPT-4o
        print("🧠 Step 2: Analyzing Section_4_1 with GPT-4o...")
        analysis_result = self.analyze_with_gpt4o(section_image_path)
        
        # Note: No longer saving to main directory - using part directories only
        # analysis_output_path = f"{self.test_dir}/section_4_1_analysis.json"
        # with open(analysis_output_path, 'w') as f:
        #     json.dump(analysis_result, f, indent=2)
        print(f"💾 Using part directories for analysis storage")
        
        if not analysis_result.get("success"):
            print("❌ GPT-4o analysis failed")
            return
        
        print("✅ GPT-4o analysis completed")
        
        # Parse and display results
        ref_impl = SectionImplementationsReference()
        json_data = ref_impl.extract_json_from_analysis(analysis_result.get("raw_analysis", ""))
        if json_data:
            print("📊 Step 3: Analysis Results:")
            
            left_analysis = json_data.get("left_box_analysis", {})
            print(f"   📦 Left Box Analysis:")
            print(f"      • Has deletion marks: {left_analysis.get('has_deletion_marks', False)}")
            print(f"      • Has replacement marks: {left_analysis.get('has_replacement_marks', False)}")
            print(f"      • Items interrupted: {left_analysis.get('interrupted_items', 0)}/{left_analysis.get('total_items', 0)}")
            print(f"      • Replacement items: {left_analysis.get('replacement_items', 0)}")
            
            right_analysis = json_data.get("right_box_analysis", {})
            print(f"   📦 Right Box Analysis:")
            print(f"      • Has deletion marks: {right_analysis.get('has_deletion_marks', False)}")
            print(f"      • Has replacement marks: {right_analysis.get('has_replacement_marks', False)}")
            print(f"      • Items interrupted: {right_analysis.get('interrupted_items', 0)}/{right_analysis.get('total_items', 0)}")
            print(f"      • Replacement items: {right_analysis.get('replacement_items', 0)}")
            if right_analysis.get('continuous_line_detected'):
                print(f"      • Continuous line detected: True")
            
            row_deletion = json_data.get("row_deletion_rule", {})
            print(f"   🚨 Row Deletion Rule:")
            print(f"      • Should delete entire row: {row_deletion.get('should_delete_entire_row', False)}")
            if row_deletion.get('explanation'):
                print(f"      • Explanation: {row_deletion.get('explanation')}")
        
        print()
        
        # Step 4: Save analysis results for unified processing
        print("💾 Step 4: Saving analysis results...")
        self.save_analysis_results(analysis_data)
        
        print("📝 Analysis-only mode: Word document processing handled by unified_section_implementations.py")

def main():
    """Run 4 1 test"""
    import argparse

    parser = argparse.ArgumentParser(description="4 1 Tester")
    parser.add_argument("--pdf-path", help="Path to PDF file for analysis")
    parser.add_argument("--analysis-only", action="store_true",
                       help="Run only analysis (no Word processing)")
    args = parser.parse_args()

    # Create tester with dynamic PDF path
    tester = Section4_1Tester(pdf_path=args.pdf_path)

    if args.analysis_only:
        success = tester.run_analysis_only()
        print(f"Analysis {'completed successfully' if success else 'failed'}")
    else:
        tester.run_section_4_1_test()

if __name__ == "__main__":
    main()

