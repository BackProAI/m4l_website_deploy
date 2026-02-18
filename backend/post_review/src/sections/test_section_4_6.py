#!/usr/bin/env python3
"""
Section 4_6 Individual Testing
Tests blank box section - detects handwriting and creates bullet points with the text
"""

# This file requires pre-extracted images from pdf_section_splitter.py
# Run: splitter = PDFSectionSplitter(pdf_path); splitter.extract_all_sections()
# Then this file will work with the pre-extracted section image

import os
import json
import base64
import requests
from pathlib import Path
from PIL import Image
from docx import Document
from docx.shared import Pt
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, project_root)

from dotenv import load_dotenv

# This file is designed to work only through the Post-Review UI system
# Run: python post_review_modern_ui.py
# Do not run this file directly

class Section46Tester:
    def __init__(self, pdf_path=None):
        # This test section works with pre-extracted PNG images only
        # PDF sectioning is handled by PDFSectionSplitter
        # Word processing is handled by unified_section_implementations.py
        
        # Make test directory relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.test_dir = os.path.join(project_root, "data", "test_sections", "section_4_6_test")
        
        # Get API key
        # Load environment variables from project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_path = os.path.join(project_root, '.env')
        load_dotenv(env_path)
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY in .env file.")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def load_extracted_image(self) -> Image.Image:
        """Load pre-extracted section image (extracted by pdf_section_splitter.py)"""
        try:
            # Ensure test directory exists
            os.makedirs(self.test_dir, exist_ok=True)
            
            # Check for pre-extracted image
            image_filename = "section_4_6_extracted.png"
            image_path = os.path.join(self.test_dir, image_filename)
            
            if os.path.exists(image_path):
                print(f"✅ Found pre-extracted image: {image_path}")
                
                # Load and return the image
                section_image = Image.open(image_path)
                print(f"   📏 Image size: {section_image.size}")
                return section_image
            else:
                print(f"❌ Pre-extracted image not found: {image_path}")
                print(f"   💡 Make sure to run pdf_section_splitter.py first!")
                return None
                
        except Exception as e:
            print(f"Error loading pre-extracted image: {e}")
            return None
    
    def encode_image(self, image: Image.Image) -> str:
        """Encode PIL image to base64"""
        import io
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def get_section_4_6_analysis_prompt(self) -> str:
        """
        PROMPT for Section 4_6 - Blank box with potential handwriting
        """
        return """
        Analyze this Section 4_6 for HANDWRITTEN TEXT in a BLANK BOX:
        
        SECTION DESCRIPTION:
        - This is typically a blank rectangular box/area
        - Sometimes it contains handwritten text or bullet points
        - Sometimes it's completely empty
        
        TASK: HANDWRITING DETECTION AND EXTRACTION
        
        STEP 1: ANALYZE THE BOX CONTENT
        - Look carefully for ANY handwritten text, words, or marks
        - Check for handwritten bullet points or dot points
        - Look for any written content, even if faint or partial
        - Determine if the box is completely empty or contains content
        
        STEP 2: EXTRACT HANDWRITTEN CONTENT
        - If handwriting is found, extract each distinct piece of text
        - If there are multiple lines or bullet points, extract each one separately
        - Clean up the handwritten text to make it readable
        - Preserve the intended meaning while making it legible
        
        STEP 3: STRUCTURE THE CONTENT
        - Group related handwritten text together
        - If there are natural bullet points or list items, identify them
        - If it's continuous text, break it into logical sentences or phrases
        
        CRITICAL DETECTION RULES:
        1. Look very carefully - handwriting can be faint or small
        2. Even partial words or phrases should be captured
        3. If you see any marks that could be text, err on the side of including them
        4. Empty boxes should be clearly identified as having no content
        
        Return detailed JSON:
        {
            "blank_box_analysis": {
                "has_handwritten_content": true/false,
                "content_type": "bullet_points/continuous_text/mixed/empty",
                "handwritten_items": [
                    {
                        "item_number": 1,
                        "text": "extracted handwritten text",
                        "confidence": 0.0-1.0,
                        "item_type": "bullet_point/sentence/phrase"
                    }
                ],
                "total_items_found": 0,
                "box_appears_empty": true/false,
                "additional_notes": "any observations about the handwriting quality, style, or layout"
            },
            "processing_recommendations": {
                "should_create_bullet_points": true/false,
                "suggested_format": "bullet_list/paragraph/mixed",
                "estimated_items_to_create": 0
            },
            "visual_description": "comprehensive description of what is seen in the blank box area"
        }
        """
    
    def analyze_section_4_6(self, section_image: Image.Image) -> dict:
        """Analyze Section 4_6 with GPT-4o"""
        
        prompt = self.get_section_4_6_analysis_prompt()
        base64_image = self.encode_image(section_image)
        
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
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.1
        }
        
        try:
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
                "raw_analysis": f"Error analyzing Section 4_6: {str(e)}",
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
    
    def run_section_4_6_test(self):
        """Run complete Section 4_6 test"""
        print("🧪 Section 4_6 Individual Test - Blank Box Handwriting Detection")
        print("=" * 70)
        
        # Step 1: Extract section image
        print("📷 Step 1: Extracting Section 4_6 image...")
        section_image = self.load_extracted_image()
        if not section_image:
            print("❌ Failed to extract Section 4_6 image")
            return
        
        # Save section image for reference
        os.makedirs(self.test_dir, exist_ok=True)
        image_path = os.path.join(self.test_dir, "section_4_6_extracted.png")
        section_image.save(image_path)
        print(f"   💾 Section image saved: {image_path}")
        
        # Step 2: Analyze with GPT-4o
        print("\n🔍 Step 2: Analyzing blank box with GPT-4o...")
        analysis_result = self.analyze_section_4_6(section_image)
        
        if not analysis_result["success"]:
            print("❌ Analysis failed")
            return
        
        analysis_data = self.extract_json_from_analysis(analysis_result["raw_analysis"])
        
        # Save analysis results
        analysis_file = os.path.join(self.test_dir, "section_4_6_analysis.json")
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump({
                "raw_analysis": analysis_result["raw_analysis"],
                "parsed_data": analysis_data
            }, f, indent=2, ensure_ascii=False)
        
        # Step 3: Display analysis results
        print("\n📊 Step 3: Analysis Results:")
        
        blank_box = analysis_data.get("blank_box_analysis", {})
        recommendations = analysis_data.get("processing_recommendations", {})
        
        print(f"   📦 Blank Box Analysis:")
        print(f"      • Has handwritten content: {blank_box.get('has_handwritten_content', False)}")
        print(f"      • Content type: {blank_box.get('content_type', 'unknown')}")
        print(f"      • Total items found: {blank_box.get('total_items_found', 0)}")
        print(f"      • Box appears empty: {blank_box.get('box_appears_empty', True)}")
        
        if blank_box.get('handwritten_items'):
            print(f"   ✍️ Handwritten Items Found:")
            for i, item in enumerate(blank_box.get('handwritten_items', [])):
                print(f"      {i+1}. '{item.get('text', '')}' (confidence: {item.get('confidence', 0.0):.1f})")
        
        print(f"   💡 Processing Recommendations:")
        print(f"      • Should create bullet points: {recommendations.get('should_create_bullet_points', False)}")
        print(f"      • Suggested format: {recommendations.get('suggested_format', 'none')}")
        print(f"      • Estimated items to create: {recommendations.get('estimated_items_to_create', 0)}")
        
        print(f"   📝 Additional Notes: {blank_box.get('additional_notes', 'None')}")
        
        print("\n📝 Analysis-only mode: Word document processing handled by unified_section_implementations.py")

    def save_analysis_results(self, analysis_data: dict):
        """Save analysis results to JSON file for unified processing"""
        try:
            analysis_file = os.path.join(self.test_dir, "section_4_6_analysis.json")
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
                progress_callback("Extracting Section 4_6 image...")
            
            # Extract section image  
            section_image = self.load_extracted_image()
            if not section_image:
                print("Failed to extract Section 4_6 image")
                return False

            # Save section image
            os.makedirs(self.test_dir, exist_ok=True)
            image_path = os.path.join(self.test_dir, "section_4_6_extracted.png")
            section_image.save(image_path)
            
            if progress_callback:
                progress_callback("Analyzing Section 4_6 blank box with GPT-4o...")
            
            # Analyze with GPT-4o
            analysis_result = self.analyze_section_4_6(section_image)
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
            
            analysis_file = os.path.join(self.test_dir, "section_4_6_analysis.json")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result_full, f, indent=2, ensure_ascii=False)
            
            print("Section 4_6 analysis completed and saved successfully")
            return True
            
        except Exception as e:
            print(f"Error in run_analysis_only: {e}")
            return False

def main():
    """Run Section 4_6 test"""
    import argparse

    parser = argparse.ArgumentParser(description="Section 4_6 Tester")
    parser.add_argument("--pdf-path", help="Path to PDF file for analysis")
    parser.add_argument("--analysis-only", action="store_true",
                       help="Run only analysis (no Word processing)")
    args = parser.parse_args()

    # Create tester with dynamic PDF path
    tester = Section46Tester(pdf_path=args.pdf_path)

    if args.analysis_only:
        success = tester.run_analysis_only()
        print(f"Analysis {'completed successfully' if success else 'failed'}")
    else:
        tester.run_section_4_6_test()

if __name__ == "__main__":
    main()

