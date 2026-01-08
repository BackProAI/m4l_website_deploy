#!/usr/bin/env python3
"""

# This file requires pre-extracted images from pdf_section_splitter.py
# Run: splitter = PDFSectionSplitter(pdf_path); splitter.extract_all_sections()
# Then this file will work with the pre-extracted section image

Test Section 3_4 Implementation (RE-ENABLED after scaling fix)
Uses all existing rules with fixed PDF coordinates
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

class Section3_4Tester:
    def __init__(self, pdf_path=None):
        self.section_name = "Section_3_4"
        
        # Make test directory relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.test_dir = os.path.join(project_root, "data", "test_sections", "section_3_4_test")
        # This test section works with pre-extracted PNG images only
        # PDF sectioning is handled by PDFSectionSplitter
        # Word processing is handled by unified_section_implementations.py
        
        # Create test directory
        os.makedirs(self.test_dir, exist_ok=True)
        
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
    
    def load_extracted_image(self) -> str:
        """Load pre-extracted section image (extracted by pdf_section_splitter.py)"""
        try:
            # Ensure test directory exists
            os.makedirs(self.test_dir, exist_ok=True)
            
            # Check for pre-extracted image
            image_filename = f"section_3_4_extracted.png"
            image_path = os.path.join(self.test_dir, image_filename)
            
            if os.path.exists(image_path):
                print(f"✅ Found pre-extracted image: {image_path}")
                
                # Verify it's a valid image
                try:
                    with Image.open(image_path) as img:
                        print(f"   📏 Image size: {img.size}")
                        return image_path
                except Exception as e:
                    print(f"❌ Invalid image file: {e}")
                    return None
            else:
                print(f"❌ Pre-extracted image not found: {image_path}")
                print(f"   💡 Make sure to run pdf_section_splitter.py first!")
                return None
                
        except Exception as e:
            print(f"Error loading pre-extracted image: {e}")
            return None
    
    def analyze_with_gpt4o(self, image_path: str) -> dict:
        """Analyze section image with GPT-4o"""
        try:
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Get analysis prompt from reference implementation
            ref_impl = SectionImplementationsReference()
            prompt = ref_impl.get_section_3_4_analysis_prompt()
            
            payload = {
                "model": "gpt-4o",
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
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.1
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "raw_analysis": content
                }
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Error analyzing with GPT-4o: {e}")
            return {"success": False, "error": str(e)}
    
        # Word processing methods removed - now handled by unified_section_implementations.py

    def extract_json_from_analysis(self, raw_analysis):
        """Universal JSON extraction method for all sections"""
        try:
            import json
            import re
            
            # Step 1: Remove markdown code blocks
            cleaned = re.sub(r'```json\s*|\s*```', '', raw_analysis)
            
            # Step 2: Find JSON-like content
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Step 3: Fallback parsing
                lines = cleaned.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        return json.loads(line)
                        
            raise ValueError("No valid JSON found in analysis")
            
        except Exception as e:
            print(f"JSON extraction failed: {e}")
            # Return safe default structure
            return {
                "has_deletion_marks": False,
                "has_replacement_marks": False,
                "has_additions": False,
                "has_any_handwriting": False,
                "main_dot_points": [],
                "deletion_details": [],
                "replacement_details": [],
                "explanation": f"Analysis parsing failed: {str(e)}"
            }

    def save_analysis_results(self, analysis_data: dict):
        """Save analysis results to JSON file for unified processing"""
        try:
            analysis_file = os.path.join(self.test_dir, "section_3_4_analysis.json")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Analysis saved: {analysis_file}")
        except Exception as e:
            print(f"❌ Error saving analysis: {e}")
    
    def run_analysis_only(self, progress_callback=None):
        """Run only image extraction and analysis (no Word processing)"""
        print(f"Starting Section_3_4 Analysis")
        print("Analysis only - Word processing handled by unified processor")
        print("=" * 80)
        
        if progress_callback:
            progress_callback(1, 3, self.section_name, "Extracting section image...")
        
        # Step 1: Load PDF and cut section
        print(f"📊 Step 1: Loading PDF and cutting Section_3_4...")
        section_image_path = self.load_extracted_image()
        if not section_image_path:
            print(f"❌ Section_3_4 Analysis Failed!")
            return False
        print(f"✅ Section image loaded: {section_image_path}")
        
        if progress_callback:
            progress_callback(2, 3, self.section_name, "Analyzing with GPT-4o...")
        
        # Step 2: Analyze with GPT-4o
        print(f"🧠 Step 2: Analyzing Section_3_4 with GPT-4o...")
        analysis_result = self.analyze_with_gpt4o(section_image_path)
        
        if not analysis_result.get("success"):
            print("❌ GPT-4o analysis failed")
            return False
        
        print("✅ GPT-4o analysis completed")
        
        # Step 3: Parse and save results
        analysis_data = self.extract_json_from_analysis(analysis_result.get("raw_analysis", ""))
        if not analysis_data:
            print("⚠️ Could not parse GPT-4o analysis")
            return False
        
        if progress_callback:
            progress_callback(3, 3, self.section_name, "Saving analysis results...")
        
        # Save analysis results for unified processing
        self.save_analysis_results(analysis_data)
        
        print(f"🎉 Section_3_4 Analysis Complete!")
        return True
    
    def run_test(self):
        """Run the complete Section 3_4 test (RE-ENABLED)"""
        print("Starting Section 3_4 Test (RE-ENABLED after scaling fix)")
        print("Test section: Section 3_4 - PNG image analysis only")
        print("🔍 Section: Section_3_4 (Travel → Fund through cash flow)")
        print("🔧 Expected: Fixed PDF coordinates, correct content extraction")
        print("=" * 80)
        
        # Step 1: Load PDF and cut section with FIXED scaling
        print("📊 Step 1: Loading PDF and cutting Section_3_4 (with FIXED scaling)...")
        section_image_path = self.load_extracted_image()
        if not section_image_path:
            return
        print(f"✅ Section image loaded with fixed scaling")
        
        # Step 2: Analyze with GPT-4o
        print("🧠 Step 2: Analyzing Section_3_4 with GPT-4o...")
        analysis_result = self.analyze_with_gpt4o(section_image_path)
        
        # Save analysis for inspection
        analysis_output_path = f"{self.test_dir}/section_3_4_analysis.json"
        with open(analysis_output_path, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        print(f"💾 Analysis saved: {analysis_output_path}")
        
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
            print(f"      • Items interrupted: {left_analysis.get('interrupted_items', 0)}/{left_analysis.get('total_items', 0)}")
            
            right_analysis = json_data.get("right_box_analysis", {})
            print(f"   📦 Right Box Analysis:")
            print(f"      • Has deletion marks: {right_analysis.get('has_deletion_marks', False)}")
            print(f"      • Items interrupted: {right_analysis.get('interrupted_items', 0)}/{right_analysis.get('total_items', 0)}")
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
    """Run 3 4 test"""
    import argparse

    parser = argparse.ArgumentParser(description="3 4 Tester")
    parser.add_argument("--pdf-path", help="Path to PDF file for analysis")
    parser.add_argument("--analysis-only", action="store_true",
                       help="Run only analysis (no Word processing)")
    args = parser.parse_args()

    # Create tester with dynamic PDF path
    tester = Section3_4Tester(pdf_path=args.pdf_path)

    if args.analysis_only:
        success = tester.run_analysis_only()
        print(f"Analysis {'completed successfully' if success else 'failed'}")
    else:
        tester.run_test()

if __name__ == "__main__":
    main()

