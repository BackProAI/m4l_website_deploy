#!/usr/bin/env python3
"""
Test Section 3_2 Implementation
Uses the same logic as Section 2_5 with content-based matching and enhanced row deletion rule
"""

# This file requires pre-extracted images from pdf_section_splitter.py
# Run: splitter = PDFSectionSplitter(pdf_path); splitter.extract_all_sections()
# Then this file will work with the pre-extracted section image

import os
import sys
import json
import base64
import requests
from pathlib import Path
from PIL import Image
from docx import Document
from datetime import datetime

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)



# This file is designed to work only through the Post-Review UI system
# Run: python post_review_modern_ui.py
# Do not run this file directly

class Section3_3Tester:
    def __init__(self, pdf_path=None):
        self.section_name = "Section_3_2"
        
        # Make test directory relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.test_dir = os.path.join(project_root, "data", "test_sections", "Section_3_2_test")
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
            image_filename = "Section_3_2_extracted.png"
            image_path = os.path.join(self.test_dir, image_filename)
            
            if os.path.exists(image_path):
                print(f"✅ Found pre-extracted image: {image_path}")
                return image_path
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
            from src.utils.section_implementations_reference import SectionImplementationsReference
            ref_impl = SectionImplementationsReference()
            prompt = ref_impl.get_section_3_2_analysis_prompt()
            
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
                "max_tokens": 2000,
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
                "raw_analysis": f"Error analyzing section: {str(e)}",
                "success": False
            }
    
    def apply_changes_to_document(self, analysis_result: dict) -> bool:
        """Apply changes to the test document"""
        try:
            if not os.path.exists(self.test_document):
                print(f"❌ Test document not found: {self.test_document}")
                return False
            
            # Load document
            doc = Document(self.test_document)
            
            # Apply Section 3_2 changes using the reference implementation
            from src.utils.section_implementations_reference import SectionImplementationsReference
            ref_impl = SectionImplementationsReference()
            changes_applied = ref_impl.apply_Section_3_2_changes(doc, analysis_result)
            
            # Save processed document
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{self.test_dir}/Section_3_2_processed_{timestamp}.docx"
            doc.save(output_path)
            
            print(f"💾 Processed document saved: {output_path}")
            print(f"🔧 Changes applied: {len(changes_applied)}")
            
            if changes_applied:
                print(f"\n📋 Changes Summary:")
                for i, change in enumerate(changes_applied, 1):
                    print(f"   {i}. {change['type']} in {change['section']}")
                    if change['type'] == 'row_deletion':
                        print(f"      🚨 Complete row deleted: {change['explanation']}")
                    elif 'deleted_count' in change:
                        print(f"      🗑️ Deleted {change['deleted_count']}/{change.get('total_requested', '?')} items")
                        if change.get('type') == 'right_box_deletions' and 'continuous_line_detected' in str(analysis_result):
                            print(f"      🔄 Continuous line detected")
            else:
                print(f"\n📋 No changes were applied")
            
            return True
            
        except Exception as e:
            print(f"❌ Error applying changes: {e}")
            return False
    
    def extract_json_from_analysis(self, analysis_text: str) -> dict:
        """Extract JSON from GPT-4o analysis"""
        try:
            # Find JSON in the response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = analysis_text[start_idx:end_idx]
                return json.loads(json_str)
            return {}
        except Exception as e:
            print(f"⚠️ Could not extract JSON: {e}")
            return {}
    
    def run_test(self) -> bool:
        """Run the complete Section 3_5 test"""
        print(f"🚀 Starting Section 3_2 Test (Same logic as Section 2_5)")
        print(f"📄 Test document: {self.test_document}")
        print(f"🔍 Section: {self.section_name}")
        print("=" * 80)
        
        # Step 1: Load PDF and cut section
        print(f"📊 Step 1: Loading PDF and cutting {self.section_name}...")
        section_image_path = self.load_extracted_image()
        
        if not section_image_path:
            print(f"❌ Failed to extract section")
            return False
        
        print(f"✅ Section image loaded: {section_image_path}")
        
        # Step 2: Analyze with GPT-4o
        print(f"🧠 Step 2: Analyzing {self.section_name} with GPT-4o...")
        analysis_result = self.analyze_with_gpt4o(section_image_path)
        
        if not analysis_result.get("success", False):
            print(f"❌ GPT-4o analysis failed")
            return False
        
        # Save analysis results for inspection
        analysis_path = f"{self.test_dir}/Section_3_2_analysis.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        print(f"💾 Analysis saved: {analysis_path}")
        
        print(f"✅ GPT-4o analysis completed")
        
        # Step 3: Display analysis results
        print(f"📊 Step 3: Analysis Results:")
        json_data = self.extract_json_from_analysis(analysis_result.get("raw_analysis", ""))
        
        if json_data:
            left_analysis = json_data.get("left_box_analysis", {})
            right_analysis = json_data.get("right_box_analysis", {})
            row_rule = json_data.get("row_deletion_rule", {})
            
            print(f"   📦 Left Box Analysis:")
            print(f"      • Has deletion marks: {left_analysis.get('has_deletion_marks', False)}")
            print(f"      • Items interrupted: {left_analysis.get('interrupted_items', 0)}/{left_analysis.get('total_items', 0)}")
            print(f"      • All items interrupted: {left_analysis.get('all_items_interrupted', False)}")
            
            print(f"   📦 Right Box Analysis:")
            print(f"      • Has deletion marks: {right_analysis.get('has_deletion_marks', False)}")
            print(f"      • Items interrupted: {right_analysis.get('interrupted_items', 0)}/{right_analysis.get('total_items', 0)}")
            print(f"      • All items interrupted: {right_analysis.get('all_items_interrupted', False)}")
            print(f"      • Continuous line detected: {right_analysis.get('continuous_line_detected', False)}")
            
            print(f"   🚨 Row Deletion Rule:")
            print(f"      • Should delete entire row: {row_rule.get('should_delete_entire_row', False)}")
            print(f"      • Explanation: {row_rule.get('explanation', 'N/A')}")
        
        # Step 4: Save analysis results for unified processing
        print("💾 Step 4: Saving analysis results...")
        self.save_analysis_results(json_data)
        
        print("📝 Analysis-only mode: Word document processing handled by unified_section_implementations.py")

    def save_analysis_results(self, analysis_data: dict):
        """Save analysis results to JSON file for unified processing"""
        try:
            analysis_file = os.path.join(self.test_dir, "Section_3_2_analysis.json")
            analysis_result = {
                "raw_analysis": json.dumps(analysis_data),
                "parsed_data": analysis_data
            }
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved: {analysis_file}")
        except Exception as e:
            print(f"Error saving analysis: {e}")

    def run_analysis_only(self, progress_callback=None):
        """Run analysis only - called by master processor"""
        try:
            if progress_callback:
                progress_callback("Extracting Section 3_2 image...")
            
            # Load pre-extracted section image  
            section_image_path = self.load_extracted_image()
            if not section_image_path:
                print("Failed to load Section 3_2 pre-extracted image")
                return False
            print(f"Section image loaded: {section_image_path}")
            
            if progress_callback:
                progress_callback("Analyzing Section 3_2 with GPT-4o...")
            
            # Analyze with GPT-4o
            analysis_result = self.analyze_with_gpt4o(section_image_path)
            if not analysis_result or "raw_analysis" not in analysis_result:
                print("Failed to get analysis from GPT-4o")
                return False
            
            # Parse analysis
            analysis_data = self.extract_json_from_analysis(analysis_result["raw_analysis"])
            
            # Save analysis results
            analysis_result_full = {
                "raw_analysis": analysis_result["raw_analysis"],
                "parsed_data": analysis_data
            }
            
            analysis_file = os.path.join(self.test_dir, "Section_3_2_analysis.json")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result_full, f, indent=2, ensure_ascii=False)
            
            print("Analysis completed and saved successfully")
            return True
            
        except Exception as e:
            print(f"Error in run_analysis_only: {e}")
            return False

def main():
    """Run 3 3 test"""
    import argparse

    parser = argparse.ArgumentParser(description="3 3 Tester")
    parser.add_argument("--pdf-path", help="Path to PDF file for analysis")
    parser.add_argument("--analysis-only", action="store_true",
                       help="Run only analysis (no Word processing)")
    args = parser.parse_args()

    # Create tester with dynamic PDF path
    tester = Section3_3Tester(pdf_path=args.pdf_path)

    if args.analysis_only:
        success = tester.run_analysis_only()
        print(f"Analysis {'completed successfully' if success else 'failed'}")
    else:
        tester.run_test()

if __name__ == "__main__":
    main()

