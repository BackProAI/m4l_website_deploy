#!/usr/bin/env python3
"""
POST REVIEW Configuration Adapter
Automatically detects POST REVIEW documents and applies correct scaling
"""

import os
import json
import fitz
from pathlib import Path

class PostReviewConfigAdapter:
    def __init__(self):
        # POST REVIEW specific settings
        self.post_review_pdf_name = "POST REV LETTER WITH JAMES NOTES Michael Easton post review working docs incl signed MDA Feb 25.pdf"
        # Get project root (three levels up from src/core/)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.post_review_config = os.path.join(project_root, "config", "post_review_sections_part2.json")
        self.default_config = os.path.join(project_root, "config", "post_review_sections_part2.json")
        
        # Expected dimensions for POST REVIEW document (original size)
        # Based on exact measurements: 595.2 × 842.0 points (A4 Portrait)
        self.post_review_width = 595.2
        self.post_review_height = 842.0
        
        # Expected dimensions for default template (original size)  
        self.default_width = 595
        self.default_height = 421
        
    def detect_document_type(self, pdf_path):
        """Detect if this is a POST REVIEW document"""
        if not pdf_path or not os.path.exists(pdf_path):
            return "unknown"
            
        pdf_name = os.path.basename(pdf_path)
        
        # Check if it's the specific POST REVIEW document
        if "POST REV LETTER" in pdf_name and "JAMES NOTES" in pdf_name:
            return "post_review"
            
        # Check dimensions to identify document type
        try:
            pdf_doc = fitz.open(pdf_path)
            if len(pdf_doc) > 0:
                page = pdf_doc[0]
                rect = page.rect
                
                # Get original dimensions (no scaling)
                rect = page.rect
                width, height = int(rect.width), int(rect.height)
                pdf_doc.close()
                
                # Check if dimensions match POST REVIEW format (portrait, tall)
                if abs(width - self.post_review_width) < 10 and abs(height - self.post_review_height) < 50:
                    return "post_review"
                # Check if dimensions match default format (landscape-ish)
                elif abs(width - self.default_width) < 10 and abs(height - self.default_height) < 50:
                    return "default"
                    
        except Exception as e:
            print(f"⚠️ Error detecting document type: {e}")
            
        return "unknown"
    
    def get_pdf_dimensions(self, pdf_path):
        """Get the actual dimensions of a PDF"""
        if not pdf_path or not os.path.exists(pdf_path):
            return 0, 0
            
        try:
            pdf_doc = fitz.open(pdf_path)
            if len(pdf_doc) > 0:
                page = pdf_doc[0]
                rect = page.rect
                width, height = rect.width, rect.height
                pdf_doc.close()
                return width, height
        except Exception as e:
            print(f"⚠️ Error getting PDF dimensions: {e}")
            
        return 0, 0
        
    def get_appropriate_config(self, pdf_path):
        """Get the appropriate configuration file for the document"""
        doc_type = self.detect_document_type(pdf_path)
        
        if doc_type == "post_review":
            if os.path.exists(self.post_review_config):
                print(f"🎯 Using POST REVIEW config: {self.post_review_config}")
                return self.post_review_config
            else:
                print(f"⚠️ POST REVIEW document detected but config not found: {self.post_review_config}")
                print(f"   Falling back to default config: {self.default_config}")
                return self.default_config
        else:
            print(f"📄 Using default config: {self.default_config}")
            return self.default_config
            
    def get_scaling_info(self, pdf_path):
        """Get scaling information for the document"""
        doc_type = self.detect_document_type(pdf_path)
        
        # Get actual PDF dimensions
        actual_width, actual_height = self.get_pdf_dimensions(pdf_path)
        
        if doc_type == "post_review":
            # Calculate scaling needed to normalize to reference dimensions
            width_scale = self.post_review_width / actual_width if actual_width > 0 else 1.0
            height_scale = self.post_review_height / actual_height if actual_height > 0 else 1.0
            
            return {
                "type": "post_review",
                "reference_width": self.post_review_width,
                "reference_height": self.post_review_height,
                "actual_width": actual_width,
                "actual_height": actual_height,
                "width_scale": width_scale,
                "height_scale": height_scale,
                "needs_scaling": abs(width_scale - 1.0) > 0.01 or abs(height_scale - 1.0) > 0.01,
                "scale_factor": 4.0,  # Still use 4x for rendering quality
                "description": "POST REVIEW Letter format (A4 portrait)"
            }
        else:
            # Calculate scaling for default format
            width_scale = self.default_width / actual_width if actual_width > 0 else 1.0
            height_scale = self.default_height / actual_height if actual_height > 0 else 1.0
            
            return {
                "type": "default",
                "reference_width": self.default_width,
                "reference_height": self.default_height,
                "actual_width": actual_width,
                "actual_height": actual_height,
                "width_scale": width_scale,
                "height_scale": height_scale,
                "needs_scaling": abs(width_scale - 1.0) > 0.01 or abs(height_scale - 1.0) > 0.01,
                "scale_factor": 4.0,  # Still use 4x for rendering quality
                "description": "Default template format"
            }
            
    def ensure_post_review_config_exists(self):
        """Create a basic POST REVIEW config if it doesn't exist"""
        if os.path.exists(self.post_review_config):
            return True
            
        print(f"🔧 Creating basic POST REVIEW config: {self.post_review_config}")
        
        # Create a basic configuration with original coordinates (need to be redefined)
        # These coordinates are placeholders and need to be defined using the section definition tool
        basic_config = {
            "page_3": [
                {
                    "id": 1,
                    "name": "Section_3_2",
                    "page": 3,
                    "rect": [12, 37, 130, 127],  # Scaled down from 4x coordinates
                    "description": "Analysis and modifications",
                    "target_field": ""
                },
                {
                    "id": 2,
                    "name": "Section_3_3", 
                    "page": 3,
                    "rect": [13, 127, 130, 172],  # Scaled down from 4x coordinates
                    "description": "Analysis and modifications",
                    "target_field": ""
                }
            ],
            "page_4": [
                {
                    "id": 1,
                    "name": "Section_4_1",
                    "page": 4,
                    "rect": [10, 3, 136, 47],  # Scaled down from 4x coordinates
                    "description": "Two boxes with deletions and arrow replacements",
                    "target_field": ""
                },
                {
                    "id": 2,
                    "name": "Section_4_2",
                    "page": 4,
                    "rect": [11, 48, 128, 55],  # Scaled down from 4x coordinates
                    "description": "Two boxes with deletions and arrow replacements",
                    "target_field": ""
                },
                {
                    "id": 3,
                    "name": "Section_4_3",
                    "page": 4,
                    "rect": [10, 56, 127, 64],  # Scaled down from 4x coordinates
                    "description": "Two boxes with deletions and arrow replacements",
                    "target_field": ""
                },
                {
                    "id": 4,
                    "name": "Section_4_4",
                    "page": 4,
                    "rect": [10, 64, 127, 87],  # Scaled down from 4x coordinates
                    "description": "Complex dot points with sub-dot point deletion rules",
                    "target_field": ""
                },
                {
                    "id": 5,
                    "name": "Section_4_5",
                    "page": 4,
                    "rect": [10, 90, 137, 142],  # Scaled down from 4x coordinates
                    "description": "Diagonal deletions, horizontal strikethroughs, arrow replacements",
                    "target_field": ""
                }
            ],
            "_metadata": {
                "version": "1.0",
                "description": "POST REVIEW Section Configuration (Original Coordinates)",
                "source_pdf": f"post_review/{self.post_review_pdf_name}",
                "reference_scale": 1.0,
                "reference_size": f"{self.post_review_width}x{self.post_review_height}",
                "total_sections": 7,
                "note": "Coordinates are in original dimensions (595x842). Use post_review_section_definition_tool.py to define accurate coordinates."
            }
        }
        
        try:
            with open(self.post_review_config, 'w') as f:
                json.dump(basic_config, f, indent=2)
            print(f"✅ Created basic POST REVIEW config")
            return True
        except Exception as e:
            print(f"❌ Failed to create POST REVIEW config: {e}")
            return False

# Convenience functions for integration
def get_config_for_pdf(pdf_path):
    """Get the appropriate config file for a PDF"""
    adapter = PostReviewConfigAdapter()
    return adapter.get_appropriate_config(pdf_path)

def get_scaling_for_pdf(pdf_path):
    """Get scaling information for a PDF"""
    adapter = PostReviewConfigAdapter()
    return adapter.get_scaling_info(pdf_path)

def ensure_post_review_ready():
    """Ensure POST REVIEW configuration is ready"""
    adapter = PostReviewConfigAdapter()
    return adapter.ensure_post_review_config_exists()

if __name__ == "__main__":
    # Test the adapter
    adapter = PostReviewConfigAdapter()
    
    # Test with POST REVIEW document
    post_review_path = "post_review/POST REV LETTER WITH JAMES NOTES Michael Easton post review working docs incl signed MDA Feb 25.pdf"
    
    print("🔍 Testing POST REVIEW Config Adapter")
    print("="*50)
    
    doc_type = adapter.detect_document_type(post_review_path)
    print(f"📄 Document type: {doc_type}")
    
    config_file = adapter.get_appropriate_config(post_review_path)
    print(f"⚙️ Config file: {config_file}")
    
    scaling_info = adapter.get_scaling_info(post_review_path)
    print(f"📐 Scaling info: {scaling_info}")
    
    # Ensure config exists
    adapter.ensure_post_review_config_exists()
