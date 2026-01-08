#!/usr/bin/env python3
"""

# This file requires pre-extracted images from pdf_section_splitter.py
# Run: splitter = PDFSectionSplitter(pdf_path); splitter.extract_all_sections()
# Then this file will work with the pre-extracted section image

Test script for Section 1_1 - Date Replacement & General Strikethrough Detection

PRIMARY FUNCTIONALITY - Date Replacement:
- Look for "Dear Michael & Karen Thank you for your time and the information you shared with me at your More4Life review on < insert date >."
- The "< insert date >" has a line through it with handwritten date nearby (with arrow or direct placement)
- Replace "< insert date >" with the handwritten date in the Word document

SECONDARY FUNCTIONALITY - General Strikethrough Detection:
- Scan for ANY words with strikethrough/line-through marks
- Check pixel proximity between strikethrough and handwritten text
- Delete strikethrough words ONLY if no handwritten text is within close proximity (~20-30 pixels)
- Preserve words if handwritten text is nearby (likely replacements)
"""

import os
import sys
import json
import base64
import requests

from datetime import datetime
from docx import Document
from PIL import Image

from dotenv import load_dotenv

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import config adapter for proper PDF scaling

# This file is designed to work only through the Post-Review UI system
# Run: python post_review_modern_ui.py
# Do not run this file directly

class Section1_1Tester:
    def __init__(self, pdf_path=None):
        self.section_name = "Section_1_1"
        
        # Make test directory relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.test_dir = os.path.join(project_root, "data", "test_sections", "section_1_1_test")
        
        # This test section works with pre-extracted PNG images only
        # PDF sectioning is handled by PDFSectionSplitter
        # Word processing is handled by unified_section_implementations.py

        # Load environment variables from project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_path = os.path.join(project_root, '.env')
        print(f"🔍 Debug - Project root: {project_root}")
        print(f"🔍 Debug - Looking for .env at: {env_path}")
        print(f"🔍 Debug - .env file exists: {os.path.exists(env_path)}")
        
        load_dotenv(env_path)
        self.api_key = os.getenv('OPENAI_API_KEY')
        print(f"🔍 Debug - API key loaded: {'Yes' if self.api_key else 'No'}")
        if self.api_key:
            print(f"🔍 Debug - API key length: {len(self.api_key)} characters")
            print(f"🔍 Debug - API key starts with: {self.api_key[:10]}...")
        
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY in .env file.")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def load_extracted_image(self) -> str:
        """Load pre-extracted section image (extracted by pdf_section_splitter.py)"""
        try:
            # Ensure test directory exists
            print(f"🔍 Debug - Test directory: {self.test_dir}")
            os.makedirs(self.test_dir, exist_ok=True)
            print(f"🔍 Debug - Test directory exists after makedirs: {os.path.exists(self.test_dir)}")
            
            # Check for pre-extracted image
            image_filename = f"section_1_1_extracted.png"
            image_path = os.path.join(self.test_dir, image_filename)
            print(f"🔍 Debug - Looking for image at: {image_path}")
            print(f"🔍 Debug - Image file exists: {os.path.exists(image_path)}")
            
            # List all files in test directory
            if os.path.exists(self.test_dir):
                all_files = os.listdir(self.test_dir)
                print(f"🔍 Debug - All files in test dir: {all_files}")
            
            if os.path.exists(image_path):
                print(f"✅ Found pre-extracted image: {image_path}")
                
                # Verify it's a valid image
                try:
                    with Image.open(image_path) as img:
                        print(f"   📏 Image size: {img.size}")
                        print(f"   📏 Image mode: {img.mode}")
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
        """Analyze Section 1_1 with GPT-4o for date replacement"""
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Section 1_1 specific prompt for date replacement AND general strikethrough detection
            prompt = """
You are analyzing Section 1_1 of a document that contains date replacement instructions and general strikethrough deletions.

SECTION 1_1 ANALYSIS RULES:

PRIMARY TASK - DATE REPLACEMENT:
1. Look for the text "Dear Michael & Karen Thank you for your time and the information you shared with me at your More4Life review on < insert date >."
2. The "< insert date >" should have a line through it (strikethrough/deletion mark)
3. Look for handwritten date text nearby - either:
   - With an arrow pointing to where the date should go
   - Written directly near the "< insert date >" area
4. The handwritten date should replace "< insert date >" in the Word document

SECONDARY TASK - GENERAL STRIKETHROUGH DETECTION:
5. Scan the entire section for ANY words that have strikethrough/line-through marks
6. For each strikethrough word, check if there is handwritten text within close pixel proximity (within ~20-30 pixels)
7. DELETION RULE: Only mark a word for deletion if:
   - It has a clear strikethrough/line-through mark AND
   - There is NO handwritten text within close pixel distance from the strikethrough
8. PRESERVATION RULE: If handwritten text is near a strikethrough, do NOT delete the original word (the handwritten text is likely a replacement)

CRITICAL DETECTION REQUIREMENTS:
- STRIKETHROUGH: Must see a line through text
- PROXIMITY CHECK: Measure pixel distance between strikethrough and any handwritten text
- HANDWRITTEN TEXT: Must identify any handwritten additions/modifications
- DELETION SAFETY: Only delete if no handwritten text is nearby

Analyze this image and provide a JSON response:

```json
{
    "has_date_replacement": boolean,
    "strikethrough_detected": boolean,
    "handwritten_date_found": boolean,
    "handwritten_date_text": "extracted date text or empty string",
    "arrow_present": boolean,
    "replacement_instruction": {
        "find_text": "< insert date >",
        "replace_with": "handwritten date text",
        "should_replace": boolean
    },
    "general_strikethrough_analysis": {
        "strikethrough_words_found": boolean,
        "strikethrough_details": [
            {
                "word_text": "text with strikethrough",
                "has_nearby_handwriting": boolean,
                "pixel_distance_to_handwriting": number or null,
                "should_delete": boolean,
                "handwritten_replacement_text": "text or empty string",
                "explanation": "why this word should/shouldn't be deleted"
            }
        ]
    },
    "explanation": "detailed explanation of what was found including all strikethrough analysis"
}
```

BE PRECISE: Only return true for handwritten_date_found if you can clearly see handwritten date text.
EXTRACT EXACTLY: Provide the exact handwritten date text as it appears.
PROXIMITY CHECKING: Carefully measure pixel distances between strikethrough marks and handwritten text.
DELETION SAFETY: Always err on the side of caution - if unsure about handwriting proximity, set should_delete to false.
"""

            # Make API call to GPT-4o
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            print(f"🔍 Debug - Making GPT-4o API request to: {self.api_url}")
            print(f"🔍 Debug - Image base64 length: {len(base64_image)} characters")
            print(f"🔍 Debug - Headers: {dict(self.headers)}")
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=90)
            
            print(f"🔍 Debug - Response status code: {response.status_code}")
            print(f"🔍 Debug - Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"🔍 Debug - GPT-4o response received successfully")
                print(f"🔍 Debug - Response keys: {list(result.keys())}")
                
                analysis_text = result['choices'][0]['message']['content']
                print(f"🔍 Debug - Analysis text length: {len(analysis_text)} characters")
                print(f"🔍 Debug - Analysis text preview: {analysis_text[:200]}...")
                
                # Save analysis for inspection
                analysis_output_path = f"{self.test_dir}/section_1_1_analysis.json"
                print(f"🔍 Debug - Saving analysis to: {analysis_output_path}")
                print(f"🔍 Debug - Test directory exists: {os.path.exists(self.test_dir)}")
                
                try:
                    with open(analysis_output_path, 'w') as f:
                        json.dump({"raw_analysis": analysis_text}, f, indent=2)
                    print(f"✅ Analysis saved successfully: {analysis_output_path}")
                    print(f"🔍 Debug - File was created: {os.path.exists(analysis_output_path)}")
                    if os.path.exists(analysis_output_path):
                        print(f"🔍 Debug - File size: {os.path.getsize(analysis_output_path)} bytes")
                except Exception as e:
                    print(f"❌ Error saving analysis: {e}")
                
                return {
                    "success": True,
                    "raw_analysis": analysis_text
                }
            else:
                print(f"❌ GPT-4o API error: {response.status_code}")
                print(f"❌ Error response: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"Error analyzing with GPT-4o: {e}")
            return {"success": False, "error": str(e)}
    
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
    
    # Word processing methods removed - now handled by unified_section_implementations.py
    
    def save_analysis_results(self, analysis_data: dict):
        """Save analysis results to JSON file for unified processing"""
        try:
            analysis_file = f"{self.test_dir}/section_1_1_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved: {analysis_file}")
        except Exception as e:
            print(f"Error saving analysis: {e}")
    
    def run_analysis_only(self, progress_callback=None):
        """Run only image extraction and analysis (no Word processing)"""
        print("Starting Section 1_1 Analysis (Date Replacement)")
        print("Analysis only - Word processing handled by unified processor")
        print("=" * 80)
        print(f"🔍 Debug - Current working directory: {os.getcwd()}")
        print(f"🔍 Debug - Section name: {self.section_name}")
        print(f"🔍 Debug - Test directory: {self.test_dir}")
        
        if progress_callback:
            progress_callback(1, 3, self.section_name, "Extracting section image...")
        
        # Step 1: Load PDF and cut section
        print("Step 1: Loading PDF and cutting Section_1_1...")
        section_image_path = self.load_extracted_image()
        if not section_image_path:
            print("❌ Section 1_1 Analysis Failed - No image found!")
            return False
        print(f"✅ Section image loaded: {section_image_path}")
        
        if progress_callback:
            progress_callback(2, 3, self.section_name, "Analyzing with GPT-4o...")
        
        # Step 2: Analyze with GPT-4o
        print("Step 2: Analyzing Section_1_1 with GPT-4o...")
        print(f"🔍 Debug - About to call analyze_with_gpt4o with: {section_image_path}")
        analysis_result = self.analyze_with_gpt4o(section_image_path)
        print(f"🔍 Debug - Analysis result: {analysis_result}")
        
        if not analysis_result.get("success"):
            print("GPT-4o analysis failed")
            return False
        
        print("GPT-4o analysis completed")
        
        # Step 3: Parse and save results
        analysis_data = self.extract_json_from_analysis(analysis_result.get("raw_analysis", ""))
        if not analysis_data:
            print("Could not parse GPT-4o analysis")
            return False
        
        if progress_callback:
            progress_callback(3, 3, self.section_name, "Saving analysis results...")
        
        # Save analysis results for unified processing (save the full result, not just parsed data)
        self.save_analysis_results(analysis_result)
        
        print(f"Section 1_1 Analysis Complete!")
        return True
    
    def run_test(self):
        """Run complete Section 1_1 test"""
        print("Starting Section 1_1 Test (Date Replacement)")
        print("Test section: Section 1_1 - PNG image analysis only")
        print("Section: Section_1_1")
        print("Looking for: '< insert date >' replacement with handwritten date")
        print("=" * 80)
        
        # Step 1: Load PDF and cut section
        print("Step 1: Loading PDF and cutting Section_1_1...")
        section_image_path = self.load_extracted_image()
        if not section_image_path:
            print("Section 1_1 Test Failed!")
            return
        print(f"Section image loaded: {section_image_path}")
        
        # Step 2: Analyze with GPT-4o
        print("Step 2: Analyzing Section_1_1 with GPT-4o...")
        analysis_result = self.analyze_with_gpt4o(section_image_path)
        
        if not analysis_result.get("success"):
            print("GPT-4o analysis failed")
            print("Section 1_1 Test Failed!")
            return
        
        print("GPT-4o analysis completed")
        
        # Step 3: Parse and display results
        analysis_data = self.extract_json_from_analysis(analysis_result.get("raw_analysis", ""))
        if analysis_data:
            print("Step 3: Analysis Results:")
            print(f"   Date replacement needed: {analysis_data.get('has_date_replacement', False)}")
            print(f"   Strikethrough detected: {analysis_data.get('strikethrough_detected', False)}")
            print(f"   Handwritten date found: {analysis_data.get('handwritten_date_found', False)}")
            print(f"   Handwritten date text: '{analysis_data.get('handwritten_date_text', '')}'")
            print(f"   Arrow present: {analysis_data.get('arrow_present', False)}")
            
            replacement = analysis_data.get('replacement_instruction', {})
            print(f"   Should replace: {replacement.get('should_replace', False)}")
            if replacement.get('should_replace'):
                print(f"   Find: '{replacement.get('find_text', '')}'")
                print(f"   Replace with: '{replacement.get('replace_with', '')}'")
            
            # Display general strikethrough analysis results
            strikethrough_analysis = analysis_data.get('general_strikethrough_analysis', {})
            if strikethrough_analysis.get('strikethrough_words_found', False):
                print(f"\n   📝 GENERAL STRIKETHROUGH ANALYSIS:")
                print(f"   Strikethrough words found: {strikethrough_analysis.get('strikethrough_words_found', False)}")
                
                strikethrough_details = strikethrough_analysis.get('strikethrough_details', [])
                if strikethrough_details:
                    print(f"   Found {len(strikethrough_details)} strikethrough word(s):")
                    for i, detail in enumerate(strikethrough_details, 1):
                        print(f"      {i}. Word: '{detail.get('word_text', 'Unknown')}'")
                        print(f"         Has nearby handwriting: {detail.get('has_nearby_handwriting', False)}")
                        pixel_dist = detail.get('pixel_distance_to_handwriting')
                        if pixel_dist is not None:
                            print(f"         Pixel distance to handwriting: {pixel_dist}")
                        else:
                            print(f"         Pixel distance to handwriting: N/A")
                        print(f"         Should delete: {detail.get('should_delete', False)}")
                        replacement_text = detail.get('handwritten_replacement_text', '')
                        if replacement_text:
                            print(f"         Handwritten replacement: '{replacement_text}'")
                        explanation = detail.get('explanation', '')
                        if explanation:
                            print(f"         Explanation: {explanation}")
            else:
                print(f"\n   📝 GENERAL STRIKETHROUGH ANALYSIS: No additional strikethrough words found")
        else:
            print("Could not parse GPT-4o analysis")
            print("Section 1_1 Test Failed!")
            return
        
        # Step 4: Save analysis results for unified processing
        print("Step 4: Saving analysis results...")
        self.save_analysis_results(analysis_result)
        
        print("Analysis-only mode: Word document processing handled by unified_section_implementations.py")
        
        print(f"\nSection 1_1 Test Complete!")
        print(f"Check the {self.test_dir}/ folder for results")

def main():
    """Run Section 1_1 test"""
    import argparse

    parser = argparse.ArgumentParser(description="Section 1_1 Tester")
    parser.add_argument("--pdf-path", help="Path to PDF file for analysis")
    parser.add_argument("--analysis-only", action="store_true",
                       help="Run only analysis (no Word processing)")
    args = parser.parse_args()

    # Create tester with dynamic PDF path
    tester = Section1_1Tester(pdf_path=args.pdf_path)

    if args.analysis_only:
        success = tester.run_analysis_only()
        print(f"Analysis {'completed successfully' if success else 'failed'}")
    else:
        tester.run_test()

if __name__ == "__main__":
    main()

