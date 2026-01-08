#!/usr/bin/env python3
"""

# This file requires pre-extracted images from pdf_section_splitter.py
# Run: splitter = PDFSectionSplitter(pdf_path); splitter.extract_all_sections()
# Then this file will work with the pre-extracted section image

Test script for Section 1_2 - Goals/Achieved Table
- Look for "GOALS" and "ACHIEVED" table headers
- Left side: Extract handwritten words next to dot points and place them in the dot points
- Right side: Leave the ticks/checkmarks unchanged (don't touch them)
- Preserve the dot point structure while adding the handwritten text
"""

import os
import sys
import json
import base64
import requests

from datetime import datetime
from docx import Document
from PIL import Image

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from dotenv import load_dotenv

# This file is designed to work only through the Post-Review UI system
# Run: python post_review_modern_ui.py
# Do not run this file directly

class Section1_2Tester:
    def __init__(self, pdf_path=None):
        self.section_name = "Section_1_2"
        
        # Make test directory relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.test_dir = os.path.join(project_root, "data", "test_sections", "section_1_2_test")
        
        # This test section works with pre-extracted PNG images only
        # PDF sectioning is handled by PDFSectionSplitter
        # Word processing is handled by unified_section_implementations.py
        
        # Load environment variables
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

    def load_extracted_image(self) -> str:
        """Load pre-extracted section image (extracted by pdf_section_splitter.py)"""
        try:
            # Ensure test directory exists
            os.makedirs(self.test_dir, exist_ok=True)
            
            # Check for pre-extracted image
            image_filename = f"section_1_2_extracted.png"
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
        """Analyze Section 1_2 with GPT-4o for Goals/Achieved table"""
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Section 1_2 specific prompt for Goals/Achieved table
            prompt = """
You are analyzing Section 1_2 of a document that contains a Goals/Achieved table.

SECTION 1_2 ANALYSIS RULES:
1. Look for table with "GOALS" and "ACHIEVED" headers
2. LEFT SIDE (Goals column): Look for handwritten text next to dot points (•)
3. RIGHT SIDE (Achieved column): Look for ticks/checkmarks - LEAVE THESE UNCHANGED
4. Extract the handwritten text and associate it with the corresponding dot point position

CRITICAL DETECTION REQUIREMENTS:
- COMPLETE HANDWRITTEN TEXT: Extract ALL handwritten words next to each dot point, including names like "Karen"
- DOT POINT POSITION: Note which dot point (1st, 2nd, 3rd, 4th) the handwritten text belongs to
- FULL TEXT EXTRACTION: Don't miss any handwritten words - capture the complete phrase
- PRESERVE STRUCTURE: Keep the dot points, only add the handwritten text
- IGNORE ACHIEVED COLUMN: Don't extract or modify anything from the right side

EXTRACTION PRECISION:
- Look carefully for ALL handwritten text near each dot point
- Include names, articles, and complete phrases
- Don't truncate or miss parts of handwritten text
- Capture the full context of what was written

Analyze this image and provide a JSON response:

```json
{
    "has_goals_table": boolean,
    "goals_column_found": boolean,
    "achieved_column_found": boolean,
    "handwritten_goals": [
        {
            "dot_point_number": 1,
            "handwritten_text": "COMPLETE handwritten text including all words",
            "has_handwriting": boolean
        },
        {
            "dot_point_number": 2,
            "handwritten_text": "COMPLETE handwritten text including all words", 
            "has_handwriting": boolean
        },
        {
            "dot_point_number": 3,
            "handwritten_text": "COMPLETE handwritten text including all words",
            "has_handwriting": boolean
        },
        {
            "dot_point_number": 4,
            "handwritten_text": "COMPLETE handwritten text including all words",
            "has_handwriting": boolean
        }
    ],
    "achieved_column_instructions": "Leave ticks/checkmarks unchanged",
    "should_update_goals": boolean,
    "explanation": "detailed explanation of what was found including all handwritten text"
}
```

BE COMPLETE: Extract ALL handwritten text, don't miss any words.
BE PRECISE: Include names, complete phrases, and all visible handwritten content.
PRESERVE STRUCTURE: The goal is to add complete text to existing dot points.
IGNORE ACHIEVED: Don't analyze or extract anything from the Achieved column.
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
            
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                
                # Save analysis for inspection
                analysis_output_path = f"{self.test_dir}/section_1_2_analysis.json"
                with open(analysis_output_path, 'w') as f:
                    json.dump({"raw_analysis": analysis_text}, f, indent=2)
                print(f"Analysis saved: {analysis_output_path}")
                
                return {
                    "success": True,
                    "raw_analysis": analysis_text
                }
            else:
                print(f"GPT-4o API error: {response.status_code}")
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
    
    def find_goals_table(self, doc: Document) -> tuple:
        """Find the Goals/Achieved table in the document"""
        for table_idx, table in enumerate(doc.tables):
            # Look for table with Goals/Achieved headers
            if len(table.rows) > 0 and len(table.columns) >= 2:
                first_row = table.rows[0]
                if len(first_row.cells) >= 2:
                    cell1_text = first_row.cells[0].text.strip().upper()
                    cell2_text = first_row.cells[1].text.strip().upper()
                    
                    if "GOALS" in cell1_text and "ACHIEVED" in cell2_text:
                        return table_idx, table
        
        return None, None
    
    def apply_goals_updates(self, doc: Document, analysis_data: dict) -> list:
        """Apply Section 1_2 goals updates to the Word document"""
        changes_applied = []
        
        try:
            if not analysis_data.get("should_update_goals", False):
                print("   ℹ️ No goals updates needed")
                return changes_applied
            
            # Find the Goals/Achieved table
            table_idx, goals_table = self.find_goals_table(doc)
            
            if not goals_table:
                print("   ❌ Goals/Achieved table not found in document")
                return changes_applied
            
            print(f"   ✅ Found Goals/Achieved table (Table {table_idx + 1})")
            print(f"   📊 Table has {len(goals_table.rows)} rows and {len(goals_table.columns)} columns")
            
            handwritten_goals = analysis_data.get("handwritten_goals", [])
            
            # The Goals table structure: Header row + 1 data row with existing bullet points
            if len(goals_table.rows) >= 2:
                data_row = goals_table.rows[1]  # Second row (after header)
                goals_cell = data_row.cells[0]  # Goals column (left side)
                
                print(f"   📋 Current Goals cell content: '{goals_cell.text.strip()}'")
                
                # Get existing paragraphs in the Goals cell
                existing_paragraphs = goals_cell.paragraphs
                print(f"   📊 Found {len(existing_paragraphs)} existing paragraphs in Goals cell")
                
                for i, para in enumerate(existing_paragraphs):
                    print(f"   📋 Paragraph {i+1}: '{para.text.strip()}'")
                
                updates_made = 0
                
                # Update existing bullet points with handwritten text
                for goal_data in handwritten_goals:
                    if goal_data.get("has_handwriting", False):
                        dot_point_num = goal_data.get("dot_point_number", 0)
                        handwritten_text = goal_data.get("handwritten_text", "").strip()
                        
                        if handwritten_text and 1 <= dot_point_num <= len(existing_paragraphs):
                            # Get the corresponding paragraph (dot_point_number 1 = index 0)
                            target_paragraph = existing_paragraphs[dot_point_num - 1]
                            current_text = target_paragraph.text.strip()
                            
                            # Just add the handwritten text to the existing bullet point (don't add • symbol)
                            if current_text == "•" or current_text == "" or current_text == " ":
                                # Existing bullet point is empty, just add the text
                                new_text = handwritten_text
                            elif current_text.startswith("•"):
                                # Already has bullet, add text after the bullet
                                new_text = f"• {handwritten_text}"
                            else:
                                # No bullet yet, add the text only
                                new_text = handwritten_text
                            
                            target_paragraph.text = new_text
                            print(f"   ✅ Updated bullet point {dot_point_num}: '{new_text}'")
                            updates_made += 1
                        else:
                            if handwritten_text:
                                print(f"   ⚠️ Dot point {dot_point_num} out of range (have {len(existing_paragraphs)} paragraphs)")
                
                if updates_made > 0:
                    changes_applied.append({
                        "type": "goals_table_updates",
                        "table_index": table_idx,
                        "updates_count": updates_made,
                        "existing_paragraphs": len(existing_paragraphs),
                        "goals_updated": [goal for goal in handwritten_goals if goal.get("has_handwriting")]
                    })
                    print(f"   ✅ Successfully updated {updates_made} existing bullet point(s)")
                else:
                    print("   ℹ️ No existing bullet points needed updating")
            else:
                print(f"   ❌ Table doesn't have enough rows (found {len(goals_table.rows)}, need at least 2)")
            
        except Exception as e:
            print(f"   ❌ Error applying goals updates: {e}")
            import traceback
            traceback.print_exc()
        
        return changes_applied
    
        # Word processing methods removed - now handled by unified_section_implementations.py

    def save_analysis_results(self, analysis_data: dict):
        """Save analysis results to JSON file for unified processing"""
        try:
            analysis_file = os.path.join(self.test_dir, "section_1_2_analysis.json")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved: {analysis_file}")
        except Exception as e:
            print(f"Error saving analysis: {e}")
    
    def run_analysis_only(self, progress_callback=None):
        """Run only image extraction and analysis (no Word processing)"""
        print(f"Starting Section_1_2 Analysis")
        print("Analysis only - Word processing handled by unified processor")
        print("=" * 80)
        
        if progress_callback:
            progress_callback(1, 3, self.section_name, "Extracting section image...")
        
        # Step 1: Load PDF and cut section
        print(f"Step 1: Loading PDF and cutting Section_1_2...")
        section_image_path = self.load_extracted_image()
        if not section_image_path:
            print(f"Section_1_2 Analysis Failed!")
            return False
        print(f"Section image loaded: {section_image_path}")
        
        if progress_callback:
            progress_callback(2, 3, self.section_name, "Analyzing with GPT-4o...")
        
        # Step 2: Analyze with GPT-4o
        print(f"Step 2: Analyzing Section_1_2 with GPT-4o...")
        analysis_result = self.analyze_with_gpt4o(section_image_path)
        
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
        
        # Save analysis results for unified processing
        self.save_analysis_results(analysis_data)
        
        print(f"Section_1_2 Analysis Complete!")
        return True
    
    def run_test(self):
        """Run complete Section 1_2 test"""
        print("🚀 Starting Section 1_2 Test (Goals/Achieved Table)")
        print("📄 Test section: Section 1_2 - PNG image analysis only")
        print("🔍 Section: Section_1_2")
        print("🎯 Looking for: Handwritten text next to dot points in Goals column")
        print("=" * 80)
        
        # Step 1: Load PDF and cut section
        print("📊 Step 1: Loading PDF and cutting Section_1_2...")
        section_image_path = self.load_extracted_image()
        if not section_image_path:
            print("❌ Section 1_2 Test Failed!")
            return
        print(f"✅ Section image loaded: {section_image_path}")
        
        # Step 2: Analyze with GPT-4o
        print("🧠 Step 2: Analyzing Section_1_2 with GPT-4o...")
        analysis_result = self.analyze_with_gpt4o(section_image_path)
        
        if not analysis_result.get("success"):
            print("❌ GPT-4o analysis failed")
            print("❌ Section 1_2 Test Failed!")
            return
        
        print("✅ GPT-4o analysis completed")
        
        # Step 3: Parse and display results
        analysis_data = self.extract_json_from_analysis(analysis_result.get("raw_analysis", ""))
        if analysis_data:
            print("📊 Step 3: Analysis Results:")
            print(f"   📋 Goals table found: {analysis_data.get('has_goals_table', False)}")
            print(f"   📝 Goals column found: {analysis_data.get('goals_column_found', False)}")
            print(f"   ✅ Achieved column found: {analysis_data.get('achieved_column_found', False)}")
            print(f"   🔄 Should update goals: {analysis_data.get('should_update_goals', False)}")
            
            handwritten_goals = analysis_data.get('handwritten_goals', [])
            print(f"   📋 Handwritten Goals Analysis:")
            for i, goal in enumerate(handwritten_goals, 1):
                has_writing = goal.get('has_handwriting', False)
                text = goal.get('handwritten_text', '')
                print(f"      • Dot Point {i}: {'✏️' if has_writing else '⭕'} {text if text else 'No handwriting'}")
            
        else:
            print("⚠️ Could not parse GPT-4o analysis")
            print("❌ Section 1_2 Test Failed!")
            return
        
        # Step 4: Save analysis results for unified processing
        print("💾 Step 4: Saving analysis results...")
        self.save_analysis_results(analysis_data)
        
        print("📝 Analysis-only mode: Word document processing handled by unified_section_implementations.py")
        print(f"\n🎉 Section 1_2 Test Complete!")
        print(f"📁 Check the {self.test_dir}/ folder for results")

def main():
    """Run Section 1_2 test"""
    import argparse

    parser = argparse.ArgumentParser(description="Section 1_2 Tester")
    parser.add_argument("--pdf-path", help="Path to PDF file for analysis")
    parser.add_argument("--analysis-only", action="store_true",
                       help="Run only analysis (no Word processing)")
    args = parser.parse_args()

    # Create tester with dynamic PDF path
    tester = Section1_2Tester(pdf_path=args.pdf_path)

    if args.analysis_only:
        success = tester.run_analysis_only()
        print(f"Analysis {'completed successfully' if success else 'failed'}")
    else:
        tester.run_test()

if __name__ == "__main__":
    main()

