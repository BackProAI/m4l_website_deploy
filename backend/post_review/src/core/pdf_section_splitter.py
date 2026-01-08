#!/usr/bin/env python3
"""
PDF Section Splitter
This file takes a complete PDF and splits it into individual section images
based on coordinates from post_review_sections_part2.json.

It extracts all section images from 5 pages in one efficient operation and saves them
to their respective section_*_*_test directories.

Usage:
    splitter = PDFSectionSplitter(pdf_path)
    splitter.extract_all_sections()
"""

import os
import sys
import json
import fitz  # PyMuPDF
from datetime import datetime
from PIL import Image
from io import BytesIO

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import config adapter for proper PDF scaling
from .post_review_config_adapter import get_scaling_for_pdf

class PDFSectionSplitter:
    def __init__(self, pdf_path: str):
        """Initialize PDF splitter with the target PDF"""
        self.pdf_path = pdf_path
        # Get project root (three levels up from src/core/)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Use absolute path to config file
        self.config_path = os.path.join(project_root, "config", "post_review_sections_part2.json")
        
        # Make base output directory relative to the project root
        self.base_output_dir = project_root
        
        # Track config file timestamp for auto-reload
        self.config_last_modified = None
        self.config = None
        
        # Load configuration fresh from disk
        self.load_config()
        
        # Track extraction results
        self.extraction_results = {}
        
    def load_config(self):
        """Load section configuration fresh from disk"""
        print(f"📖 Loading section configuration from {self.config_path}")
        
        # Check if file exists
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        # Get file modification time
        current_modified = os.path.getmtime(self.config_path)
        
        # Load configuration fresh from disk
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Update timestamp
        self.config_last_modified = current_modified
        
        # Get section count
        total_sections = 0
        for page_key in ["page_1", "page_2", "page_3", "page_4"]:
            total_sections += len(self.config.get(page_key, []))
        
        print(f"✅ Configuration loaded fresh from disk - {total_sections} total sections")
        print(f"   📅 File last modified: {datetime.fromtimestamp(current_modified).strftime('%Y-%m-%d %H:%M:%S')}")
        
    def reload_config_if_needed(self):
        """Reload configuration if the file has been modified"""
        if not os.path.exists(self.config_path):
            print(f"⚠️ Configuration file missing: {self.config_path}")
            return False
            
        current_modified = os.path.getmtime(self.config_path)
        
        if self.config_last_modified is None or current_modified > self.config_last_modified:
            print(f"🔄 Configuration file updated, reloading...")
            self.load_config()
            return True
        
        return False
        
    def force_reload_config(self):
        """Force reload configuration from disk regardless of modification time"""
        print(f"🔄 Force reloading configuration from disk...")
        self.load_config()
    
    def extract_all_sections(self) -> dict:
        """Extract all section images from the PDF in one efficient operation"""
        print("\n🔪 PDF SECTION SPLITTER - EXTRACTING ALL SECTIONS")
        print("=" * 60)
        print(f"📄 Source PDF: {self.pdf_path}")
        print(f"📂 Output base: {self.base_output_dir}")
        
        # Ensure we have the latest configuration
        self.reload_config_if_needed()
        
        # REFERENCE DIMENSIONS: All PDFs will be normalized to these dimensions
        # This ensures the hardcoded coordinates in config always work
        REFERENCE_WIDTH = 595.0   # A4 width in points
        REFERENCE_HEIGHT = 842.0  # A4 height in points
        
        # Open PDF once and get actual dimensions
        doc = fitz.open(self.pdf_path)
        print(f"📖 PDF opened - {len(doc)} pages")
        
        # Get actual PDF dimensions from first page
        if len(doc) > 0:
            first_page = doc[0]
            actual_rect = first_page.rect
            actual_width = actual_rect.width
            actual_height = actual_rect.height
            
            # Calculate scaling factors to normalize to reference dimensions
            width_scale = REFERENCE_WIDTH / actual_width
            height_scale = REFERENCE_HEIGHT / actual_height
            
            # Use uniform scaling (smaller factor) to maintain aspect ratio
            uniform_scale = min(width_scale, height_scale)
            
            print(f"📐 PDF Dimensions: {actual_width:.1f} × {actual_height:.1f}")
            print(f"🎯 Target Dimensions: {REFERENCE_WIDTH:.1f} × {REFERENCE_HEIGHT:.1f}")
            print(f"⚖️ Normalization scaling: {uniform_scale:.4f}")
            print(f"📊 Final rendered size: {actual_width * uniform_scale:.1f} × {actual_height * uniform_scale:.1f}")
            
            # Apply 4x additional scaling for high-quality OCR
            final_scale_factor = uniform_scale * 4.0
            print(f"🔍 Final scale factor (with 4x OCR boost): {final_scale_factor:.4f}")
        else:
            print("❌ No pages found in PDF")
            return {}
        
        try:
            # Extract sections from each page
            total_sections = 0
            successful_extractions = 0
            
            for page_key in ["page_1", "page_2", "page_3", "page_4", "page_5"]:
                page_num = int(page_key.split("_")[1]) - 1  # Convert to 0-based index
                page_sections = self.config.get(page_key, [])
                
                if not page_sections:
                    continue
                    
                print(f"\n📄 Processing {page_key.upper()} ({len(page_sections)} sections)")
                
                # Get page and render with normalization scaling
                if page_num < len(doc):
                    page = doc[page_num]
                    # Use calculated scaling to normalize page to reference dimensions
                    mat = fitz.Matrix(final_scale_factor, final_scale_factor)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    full_page = Image.open(BytesIO(img_data))
                    
                    # Apply coordinate scaling to match the rendered page
                    coord_scale = final_scale_factor
                    print(f"   📏 Page rendered at {full_page.size}, coordinate scale: {coord_scale:.4f}")
                    
                    # Extract all sections from this page
                    for section in page_sections:
                        section_name = section['name']
                        rect = section['rect']
                        
                        try:
                            # Scale coordinates from reference dimensions to rendered page dimensions
                            x1, y1, x2, y2 = rect
                            # Apply coordinate scaling to match the rendered page
                            scaled_x1 = int(x1 * coord_scale)
                            scaled_y1 = int(y1 * coord_scale) 
                            scaled_x2 = int(x2 * coord_scale)
                            scaled_y2 = int(y2 * coord_scale)
                            
                            # Extract section image using scaled coordinates
                            section_img = full_page.crop((scaled_x1, scaled_y1, scaled_x2, scaled_y2))
                            
                            print(f"      📐 {section_name}: coords({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}) → scaled({scaled_x1},{scaled_y1},{scaled_x2},{scaled_y2}) → {section_img.size}")
                            
                            # Create output directory
                            section_dir = os.path.join(self.base_output_dir, "data", "test_sections", f"{section_name.lower()}_test")
                            os.makedirs(section_dir, exist_ok=True)
                            
                            # Save section image
                            image_filename = f"{section_name.lower()}_extracted.png"
                            image_path = os.path.join(section_dir, image_filename)
                            section_img.save(image_path)
                            
                            # Track result with both original and scaled coordinates
                            self.extraction_results[section_name] = {
                                "status": "success",
                                "image_path": image_path,
                                "directory": section_dir,
                                "original_coordinates": rect,
                                "scaled_coordinates": [scaled_x1, scaled_y1, scaled_x2, scaled_y2],
                                "coordinate_scale": coord_scale,
                                "page": page_num + 1
                            }
                            
                            successful_extractions += 1
                            total_sections += 1
                            
                        except Exception as e:
                            # Track failure
                            self.extraction_results[section_name] = {
                                "status": "error",
                                "error": str(e),
                                "page": page_num + 1
                            }
                            total_sections += 1
                            print(f"   ❌ {section_name}: ERROR - {e}")
                            
                else:
                    print(f"   ❌ Page {page_num + 1} not found in PDF")
            
            print(f"\n📊 EXTRACTION SUMMARY")
            print(f"   🎯 Total sections processed: {total_sections}")
            print(f"   ✅ Successful extractions: {successful_extractions}")
            print(f"   ❌ Failed extractions: {total_sections - successful_extractions}")
            print(f"   📈 Success rate: {(successful_extractions/total_sections)*100:.1f}%")
            print(f"\n🔧 PDF NORMALIZATION APPLIED:")
            print(f"   📐 Original PDF: {actual_width:.1f} × {actual_height:.1f}")
            print(f"   🎯 Normalized to: {REFERENCE_WIDTH:.1f} × {REFERENCE_HEIGHT:.1f} (reference)")
            print(f"   ⚖️ Scale factor: {uniform_scale:.4f} (+ 4x OCR boost = {final_scale_factor:.4f})")
            print(f"   📏 All coordinates automatically scaled for consistent extraction")
            
        finally:
            doc.close()
            print(f"📖 PDF closed")
        
        return self.extraction_results
    
    def get_extraction_summary(self) -> dict:
        """Get a summary of extraction results including normalization info"""
        successful = [name for name, result in self.extraction_results.items() if result["status"] == "success"]
        failed = [name for name, result in self.extraction_results.items() if result["status"] == "error"]
        
        # Get normalization info from first successful result
        normalization_info = {}
        for result in self.extraction_results.values():
            if result.get("status") == "success" and "coordinate_scale" in result:
                normalization_info = {
                    "coordinate_scale": result.get("coordinate_scale"),
                    "normalization_applied": True,
                    "target_dimensions": "595×842 (A4 reference)"
                }
                break
        
        return {
            "total_sections": len(self.extraction_results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": (len(successful) / len(self.extraction_results)) * 100 if self.extraction_results else 0,
            "successful_sections": successful,
            "failed_sections": failed,
            "normalization_info": normalization_info,
            "details": self.extraction_results
        }
    
    def verify_extractions(self) -> dict:
        """Verify that all extracted images exist and are valid"""
        print("\n🔍 VERIFYING EXTRACTED IMAGES")
        print("=" * 40)
        
        verification_results = {}
        
        for section_name, result in self.extraction_results.items():
            if result["status"] == "success":
                image_path = result["image_path"]
                
                try:
                    # Check if file exists
                    if os.path.exists(image_path):
                        # Check if it's a valid image
                        with Image.open(image_path) as img:
                            verification_results[section_name] = {
                                "exists": True,
                                "valid": True,
                                "size": img.size,
                                "mode": img.mode,
                                "file_size": os.path.getsize(image_path)
                            }
                        print(f"   ✅ {section_name}: {img.size}, {os.path.getsize(image_path)} bytes")
                    else:
                        verification_results[section_name] = {
                            "exists": False,
                            "valid": False,
                            "error": "File not found"
                        }
                        print(f"   ❌ {section_name}: File not found")
                        
                except Exception as e:
                    verification_results[section_name] = {
                        "exists": True,
                        "valid": False,
                        "error": str(e)
                    }
                    print(f"   ❌ {section_name}: Invalid image - {e}")
            else:
                verification_results[section_name] = {
                    "exists": False,
                    "valid": False,
                    "error": "Extraction failed"
                }
                print(f"   ❌ {section_name}: Extraction failed")
        
        # Summary
        valid_count = sum(1 for result in verification_results.values() if result.get("valid", False))
        total_count = len(verification_results)
        
        print(f"\n📊 VERIFICATION SUMMARY")
        print(f"   ✅ Valid images: {valid_count}/{total_count}")
        print(f"   📈 Verification rate: {(valid_count/total_count)*100:.1f}%")
        
        return verification_results


def main():
    """Example usage of the PDF section splitter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract all PDF sections into individual images")
    parser.add_argument("--pdf-path", required=True, help="Path to PDF file")
    parser.add_argument("--verify", action="store_true", help="Verify extracted images after extraction")
    
    args = parser.parse_args()
    
    try:
        # Create splitter and extract all sections
        splitter = PDFSectionSplitter(args.pdf_path)
        results = splitter.extract_all_sections()
        
        # Show summary
        summary = splitter.get_extraction_summary()
        print(f"\n🎯 FINAL RESULTS")
        print(f"   📊 {summary['successful']}/{summary['total_sections']} sections extracted successfully")
        print(f"   📈 Success rate: {summary['success_rate']:.1f}%")
        
        if summary['failed_sections']:
            print(f"   ❌ Failed sections: {', '.join(summary['failed_sections'])}")
        
        # Verify if requested
        if args.verify:
            verification = splitter.verify_extractions()
        
        print(f"\n✅ PDF section extraction complete!")
        
    except Exception as e:
        print(f"❌ Error during PDF section extraction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
