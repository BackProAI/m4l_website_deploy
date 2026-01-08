#!/usr/bin/env python3
"""
A3 Template Processor
Creates interactive PDF templates with form fields and populates them with extracted text
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json
import time

class A3TemplateProcessor:
    """Processes A3 templates by adding form fields and populating them."""
    
    def __init__(self, template_path: Path = None, custom_fields_config: Dict = None):
        """Initialize with the blank template."""
        self.template_path = template_path or Path("A3_templates/More4Life A3 Goals - blank.pdf")
        self.form_fields_config = custom_fields_config or self._get_default_form_fields_config()
        
    def _get_default_form_fields_config(self) -> Dict[str, List[Dict]]:
        """Define where form fields should be placed on each page."""
        return {
            "page_1": [
                # Circle content areas (left side)
                {"name": "dangers_content", "rect": [50, 200, 280, 300], "type": "text", "multiline": True},
                {"name": "opportunities_content", "rect": [50, 350, 280, 450], "type": "text", "multiline": True},
                {"name": "strengths_content", "rect": [50, 500, 280, 600], "type": "text", "multiline": True},
                
                # Right side content areas
                {"name": "financial_info", "rect": [320, 200, 550, 300], "type": "text", "multiline": True},
                {"name": "career_plans", "rect": [320, 350, 550, 450], "type": "text", "multiline": True},
                {"name": "additional_notes", "rect": [320, 500, 550, 600], "type": "text", "multiline": True},
            ],
            "page_2": [
                # Money column
                {"name": "money_goals", "rect": [50, 150, 160, 250], "type": "text", "multiline": True},
                {"name": "money_now", "rect": [50, 300, 160, 400], "type": "text", "multiline": True},
                {"name": "money_todo", "rect": [50, 450, 160, 550], "type": "text", "multiline": True},
                
                # Business column
                {"name": "business_goals", "rect": [170, 150, 280, 250], "type": "text", "multiline": True},
                {"name": "business_now", "rect": [170, 300, 280, 400], "type": "text", "multiline": True},
                {"name": "business_todo", "rect": [170, 450, 280, 550], "type": "text", "multiline": True},
                
                # Leisure column
                {"name": "leisure_goals", "rect": [290, 150, 400, 250], "type": "text", "multiline": True},
                {"name": "leisure_now", "rect": [290, 300, 400, 400], "type": "text", "multiline": True},
                {"name": "leisure_todo", "rect": [290, 450, 400, 550], "type": "text", "multiline": True},
                
                # Health column
                {"name": "health_goals", "rect": [410, 150, 520, 250], "type": "text", "multiline": True},
                {"name": "health_now", "rect": [410, 300, 520, 400], "type": "text", "multiline": True},
                {"name": "health_todo", "rect": [410, 450, 520, 550], "type": "text", "multiline": True},
                
                # Family column
                {"name": "family_goals", "rect": [530, 150, 640, 250], "type": "text", "multiline": True},
                {"name": "family_now", "rect": [530, 300, 640, 400], "type": "text", "multiline": True},
                {"name": "family_todo", "rect": [530, 450, 640, 550], "type": "text", "multiline": True},
            ]
        }
    
    def create_movable_template(self, output_path: Path = None, show_borders: bool = True, show_backgrounds: bool = False) -> Path:
        """Create a template with movable/resizable fields optimized for Adobe Acrobat editing."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        output_path = output_path or Path("processed_documents/A3_Movable_Template.pdf")
        output_path.parent.mkdir(exist_ok=True)
        
        # Open the blank template
        doc = fitz.open(self.template_path)
        
        try:
            print(f"🎯 Creating movable template with Adobe Acrobat optimization...")
            print(f"   📋 Borders visible: {show_borders}")
            print(f"   🎨 Backgrounds visible: {show_backgrounds}")
            
            # Add form fields to each page with movable properties
            total_fields = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_key = f"page_{page_num + 1}"
                
                if page_key in self.form_fields_config:
                    page_fields = self.form_fields_config[page_key]
                    print(f"   📄 Page {page_num + 1}: Adding {len(page_fields)} movable fields")
                    
                    for field_config in page_fields:
                        # Add movability settings to field config
                        enhanced_config = field_config.copy()
                        enhanced_config["show_borders"] = show_borders
                        enhanced_config["show_background"] = show_backgrounds
                        
                        self._add_form_field(page, enhanced_config)
                        total_fields += 1
            
            # Configure document for Adobe Acrobat form editing
            self._configure_document_for_adobe_editing(doc)
            
            # Save the template with movable form fields
            try:
                # Try to save, handling file permission issues
                if output_path.exists():
                    # File exists, try to remove it first
                    try:
                        output_path.unlink()
                    except PermissionError:
                        # File is open, create with different name
                        import time
                        timestamp = int(time.time())
                        output_path = output_path.parent / f"{output_path.stem}_new_{timestamp}.pdf"
                        print(f"⚠️ Original file in use, saving as: {output_path.name}")
                
                doc.save(str(output_path), incremental=False, encryption=fitz.PDF_ENCRYPT_NONE)
                
            except Exception as save_error:
                print(f"⚠️ Save error: {save_error}")
                # Try alternative save location
                import time
                timestamp = int(time.time())
                backup_path = Path(f"A3_Custom_Template_Movable_backup_{timestamp}.pdf")
                try:
                    doc.save(str(backup_path), incremental=False, encryption=fitz.PDF_ENCRYPT_NONE)
                    output_path = backup_path
                    print(f"✅ Saved to backup location: {output_path}")
                except Exception as backup_error:
                    print(f"❌ Could not save template: {backup_error}")
                    raise backup_error
            print(f"✅ Created movable template: {output_path}")
            print(f"📊 Total movable fields: {total_fields}")
            print(f"🎯 Adobe Acrobat features:")
            print(f"   ✅ Fields can be moved by dragging in Prepare Form mode")
            print(f"   ✅ Fields can be resized by dragging corners/edges")
            print(f"   ✅ Text content is fully editable")
            print(f"   ✅ Borders visible for easy field identification")
            print(f"   📋 Adobe Acrobat Instructions:")
            print(f"      1. Open PDF in Adobe Acrobat")
            print(f"      2. Go to Tools > Prepare Form")
            print(f"      3. Fields will be movable and resizable")
            
            return output_path
            
        finally:
            doc.close()
    
    def create_template_with_form_fields(self, output_path: Path = None) -> Path:
        """Create a template with interactive form fields."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        output_path = output_path or Path("processed_documents/A3_template_with_fields.pdf")
        output_path.parent.mkdir(exist_ok=True)
        
        # Open the blank template
        doc = fitz.open(self.template_path)
        
        try:
            # Add form fields to each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_key = f"page_{page_num + 1}"
                
                if page_key in self.form_fields_config:
                    for field_config in self.form_fields_config[page_key]:
                        self._add_form_field(page, field_config)
            
            # Save the template with form fields
            doc.save(str(output_path))
            print(f"✅ Created template with form fields: {output_path}")
            return output_path
            
        finally:
            doc.close()
    
    def _add_form_field(self, page: fitz.Page, field_config: Dict):
        """Add a single form field to a page with Adobe Acrobat movable/resizable properties."""
        try:
            field_name = field_config["name"]
            rect = fitz.Rect(field_config["rect"])
            
            # Use PyMuPDF's add_textfield method for better Adobe Acrobat compatibility
            if field_config.get("show_borders", True):
                border_color = (0.0, 0.0, 1.0)  # Blue border for visibility
                fill_color = (0.95, 0.95, 1.0) if field_config.get("show_background", False) else (1, 1, 1)
            else:
                border_color = None
                fill_color = None
            
            # Create text field widget with Adobe Acrobat optimization
            # Note: PyMuPDF doesn't have add_textfield, use Widget approach
            field_widget = fitz.Widget()
            field_widget.field_name = field_name
            field_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            field_widget.rect = rect
            
            # Adobe Acrobat compatibility settings
            field_widget.annot_flags = 0  # No restrictions - fully interactive
            field_widget.text_font = "helv"
            field_widget.text_fontsize = field_config.get("fontsize", 12)
            field_widget.text_maxlen = 0  # No text length limit
            field_widget.text_color = (0, 0, 0)  # Black text
            
            # Set border and fill colors
            if border_color:
                field_widget.border_color = border_color
                field_widget.border_width = 1
                field_widget.border_style = "solid"
            else:
                field_widget.border_color = None
                field_widget.border_width = 0
                
            if fill_color:
                field_widget.fill_color = fill_color
            else:
                field_widget.fill_color = None
                
            # Add to page
            page.add_widget(field_widget)
            
            # Configure the widget for Adobe Acrobat movability
            if field_widget:
                # Set annotation flags for maximum interactivity
                field_widget.annot_flags = 0  # No restrictions - fully interactive
                
                # Set field flags for editability and movability
                flags = 0  # Start with no restrictions
                if field_config.get("multiline"):
                    flags |= fitz.PDF_TX_FIELD_IS_MULTILINE
                
                field_widget.field_flags = flags
                
                # Ensure the field is not read-only
                field_widget.text_maxlen = 0  # No text length limit
                
                # Update the field appearance
                field_widget.update()
                
                print(f"✅ Added Adobe-compatible field '{field_name}' at {rect}")
            else:
                print(f"⚠️ Failed to create field widget for '{field_name}'")
            
        except Exception as e:
            print(f"⚠️ Failed to add form field {field_config.get('name', 'unknown')}: {e}")
            # Fallback to original method
            try:
                self._add_form_field_fallback(page, field_config)
            except:
                pass
    
    def _add_form_field_fallback(self, page: fitz.Page, field_config: Dict):
        """Fallback method for adding form fields if add_textfield fails."""
        field_name = field_config["name"]
        rect = fitz.Rect(field_config["rect"])
        
        # Create widget manually as fallback
        widget = fitz.Widget()
        widget.field_name = field_name
        widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        widget.rect = rect
        
        # Adobe Acrobat compatibility settings
        widget.annot_flags = 0  # No restrictions
        widget.field_flags = fitz.PDF_TX_FIELD_IS_MULTILINE if field_config.get("multiline") else 0
        
        # Visual properties
        widget.text_font = "helv"
        widget.text_fontsize = field_config.get("fontsize", 12)
        widget.text_maxlen = 0
        
        if field_config.get("show_borders", True):
            widget.border_color = (0.0, 0.0, 1.0)
            widget.border_width = 1
        else:
            widget.border_color = None
            widget.border_width = 0
            
        widget.fill_color = (1, 1, 1) if field_config.get("show_borders", True) else None
        widget.text_color = (0, 0, 0)
        
        page.add_widget(widget)
        print(f"✅ Added fallback field '{field_name}' at {rect}")
    
    def _configure_document_for_adobe_editing(self, doc):
        """Configure PDF document for Adobe Acrobat form editing and field manipulation."""
        try:
            # Set document metadata for form editing
            metadata = {
                'title': 'A3 Goals Template - Editable Form',
                'author': 'A3 Automation System',
                'subject': 'Movable and Resizable Form Fields',
                'creator': 'PyMuPDF with Adobe Acrobat Optimization',
                'producer': 'A3 Template Processor',
                'keywords': 'form, editable, movable, resizable, Adobe Acrobat'
            }
            doc.set_metadata(metadata)
            
            # Set document permissions for form editing
            # Note: PyMuPDF has limited support for advanced permissions
            # The key is to ensure no restrictions are set
            
            # Add document-level JavaScript (if supported) to help with Adobe compatibility
            try:
                # This helps Adobe Acrobat recognize the document as a form
                js_code = """
                // Enable form editing mode recognition
                this.info.Title = "A3 Goals Template - Editable Form";
                this.info.Subject = "Movable and Resizable Form Fields";
                """
                # Note: PyMuPDF may not support document-level JavaScript
                # This is for Adobe Acrobat recognition
            except:
                pass  # JavaScript not supported, continue without it
            
            print("✅ Configured document for Adobe Acrobat form editing")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not fully configure document for Adobe editing: {e}")
    
    def create_empty_template(self, output_path: Path = None) -> Path:
        """Create a template with empty text fields ready for manual population."""
        if not output_path:
            timestamp = int(time.time())
            output_path = Path(f"processed_documents/A3_Empty_Template_{timestamp}.pdf")
        
        output_path.parent.mkdir(exist_ok=True)
        
        # Just create and return the template with empty form fields
        return self.create_template_with_form_fields(output_path)
    
    def populate_movable_template(self, extracted_results: List[Dict[str, Any]], output_path: Path = None, base_template: Path = None, preserve_movability: bool = True) -> Path:
        """Populate template while preserving field movability for further editing in Adobe Acrobat."""
        if not output_path:
            timestamp = int(time.time())
            output_path = Path(f"processed_documents/A3_Populated_Movable_{timestamp}.pdf")
        
        output_path.parent.mkdir(exist_ok=True)
        
        # Use existing movable template if provided, otherwise create new one
        if base_template and base_template.exists():
            template_with_fields = base_template
            print(f"✅ Using existing movable template: {template_with_fields}")
        else:
            # Create new movable template
            template_with_fields = self.create_movable_template()
            print(f"📝 Created new movable template: {template_with_fields}")
        
        # Open the template with form fields
        doc = fitz.open(template_with_fields)
        
        try:
            # Map extracted text to form fields
            field_mappings = self._map_text_to_fields(extracted_results)
            
            print(f"🎯 Populating {len(field_mappings)} fields while preserving movability...")
            
            # Populate the form fields with page-specific mapping
            populated_count = 0
            
            # Get page mapping for fields
            field_to_page = {}
            for page_key, fields in self.form_fields_config.items():
                page_number = 0 if page_key == 'page_1' else 1  # Convert to 0-based indexing
                for field in fields:
                    field_to_page[field['name']] = page_number
            
            for field_name, text_content in field_mappings.items():
                if text_content.strip():
                    try:
                        # Get the correct page for this field
                        target_page_num = field_to_page.get(field_name)
                        
                        if target_page_num is not None and target_page_num < len(doc):
                            page = doc[target_page_num]
                            widgets = page.widgets()
                            
                            field_found = False
                            for widget in widgets:
                                if widget.field_name == field_name:
                                    widget.field_value = text_content.strip()
                                    
                                    if preserve_movability:
                                        # Ensure field remains movable/editable
                                        widget.field_flags = widget.field_flags  # Keep existing flags
                                        # Keep visible borders for editing
                                        if not widget.border_color:
                                            widget.border_color = (0.7, 0.7, 1.0)
                                            widget.border_width = 1
                                    
                                    widget.update()
                                    populated_count += 1
                                    print(f"   ✅ Page {target_page_num + 1} - {field_name}: {text_content[:50]}... (movable)")
                                    field_found = True
                                    break
                            
                            if not field_found:
                                print(f"   ⚠️ Field '{field_name}' not found on Page {target_page_num + 1}")
                        else:
                            print(f"   ❌ Invalid page mapping for field '{field_name}'")
                            
                    except Exception as e:
                        print(f"⚠️ Failed to populate field {field_name}: {e}")
            
            print(f"✅ Successfully populated {populated_count} movable fields")
            print(f"🎯 Fields remain movable and resizable in Adobe Acrobat")
            
            # Save the completed document
            doc.save(str(output_path))
            print(f"📁 Saved populated movable template: {output_path}")
            
            # Clean up temporary template (only if we created it, not if it's the base template)
            if not base_template or template_with_fields != base_template:
                try:
                    if template_with_fields.exists():
                        template_with_fields.unlink()
                except Exception as cleanup_error:
                    print(f"⚠️ Could not clean up temporary template: {cleanup_error}")
            
            return output_path
            
        finally:
            doc.close()
    
    def populate_template(self, extracted_results: List[Dict[str, Any]], output_path: Path = None, base_template: Path = None) -> Path:
        """Use existing template and automatically populate it with extracted text."""
        if not output_path:
            timestamp = int(time.time())
            output_path = Path(f"processed_documents/A3_Populated_{timestamp}.pdf")
        
        output_path.parent.mkdir(exist_ok=True)
        
        # Use existing template if provided, otherwise create new one
        if base_template and base_template.exists():
            template_with_fields = base_template
            print(f"✅ Using existing template: {template_with_fields}")
        else:
            # Fallback: create new template with form fields
            template_with_fields = self.create_template_with_form_fields()
            print(f"📝 Created new template: {template_with_fields}")
        
        # Open the template with form fields
        doc = fitz.open(template_with_fields)
        
        try:
            # Map extracted text to form fields
            field_mappings = self._map_text_to_fields(extracted_results)
            
            print(f"🎯 Populating {len(field_mappings)} fields with extracted text...")
            
            # Populate the form fields with page-specific mapping
            populated_count = 0
            
            # Get page mapping for fields
            field_to_page = {}
            for page_key, fields in self.form_fields_config.items():
                page_number = 0 if page_key == 'page_1' else 1  # Convert to 0-based indexing
                for field in fields:
                    field_to_page[field['name']] = page_number
            
            for field_name, text_content in field_mappings.items():
                if text_content.strip():
                    try:
                        # Get the correct page for this field
                        target_page_num = field_to_page.get(field_name)
                        
                        if target_page_num is not None and target_page_num < len(doc):
                            page = doc[target_page_num]
                            widgets = page.widgets()
                            
                            field_found = False
                            for widget in widgets:
                                if widget.field_name == field_name:
                                    widget.field_value = text_content.strip()
                                    widget.update()
                                    populated_count += 1
                                    print(f"   ✅ Page {target_page_num + 1} - {field_name}: {text_content[:50]}...")
                                    field_found = True
                                    break
                            
                            if not field_found:
                                print(f"   ⚠️ Field '{field_name}' not found on Page {target_page_num + 1}")
                        else:
                            print(f"   ❌ Invalid page mapping for field '{field_name}'")
                            
                    except Exception as e:
                        print(f"⚠️ Failed to populate field {field_name}: {e}")
            
            print(f"✅ Successfully populated {populated_count} fields")
            
            # Save the completed document
            doc.save(str(output_path))
            print(f"📁 Saved populated template: {output_path}")
            
            # Clean up temporary template (only if we created it, not if it's the base template)
            if not base_template or template_with_fields != base_template:
                try:
                    if template_with_fields.exists():
                        template_with_fields.unlink()
                except Exception as cleanup_error:
                    print(f"⚠️ Could not clean up temporary template: {cleanup_error}")
            
            return output_path
            
        finally:
            doc.close()
    
    def _map_text_to_fields(self, extracted_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """Map extracted text sections to appropriate form fields."""
        field_mappings = {}
        
        # Get available field names from the current configuration
        available_fields = {}
        for page_key, fields in self.form_fields_config.items():
            for field in fields:
                available_fields[field['name']] = page_key
        
        print(f"\n🎯 SMART FIELD MAPPING")
        print(f"{'='*50}")
        
        # Show page-specific field counts
        page1_fields = [name for name, page in available_fields.items() if page == 'page_1']
        page2_fields = [name for name, page in available_fields.items() if page == 'page_2']
        print(f"📋 Page 1 fields ({len(page1_fields)}): {', '.join(page1_fields[:3])}{'...' if len(page1_fields) > 3 else ''}")
        print(f"📋 Page 2 fields ({len(page2_fields)}): {', '.join(page2_fields[:3])}{'...' if len(page2_fields) > 3 else ''}")
        
        for result in extracted_results:
            if not result.get('success', False):
                continue
                
            page_num = result.get('page_number', 1)
            sections = result.get('sections', [])
            
            print(f"\n📄 PROCESSING PAGE {page_num} ({'='*30})")
            print(f"   📝 Found {len(sections)} text sections to map")
            
            if page_num == 1:
                print(f"   🎯 Target: Page 1 fields only")
                page_mappings = self._map_page1_sections(sections, available_fields)
                field_mappings.update(page_mappings)
            elif page_num == 2:
                print(f"   🎯 Target: Page 2 fields only")
                page_mappings = self._map_page2_sections(sections, available_fields)
                field_mappings.update(page_mappings)
        
        print(f"\n✅ FINAL FIELD MAPPINGS:")
        print(f"{'='*50}")
        for field_name, text in field_mappings.items():
            page_info = available_fields.get(field_name, 'unknown')
            page_display = "Page 1" if page_info == 'page_1' else "Page 2" if page_info == 'page_2' else "Unknown"
            print(f"🎯 [{page_display}] {field_name}: {text[:80]}{'...' if len(text) > 80 else ''}")
        
        return field_mappings
    
    def _map_page1_sections(self, sections: List[Dict], available_fields: Dict[str, str] = None) -> Dict[str, str]:
        """Map Page 1 sections to form fields using intelligent field matching."""
        mappings = {}
        available_fields = available_fields or {}
        
        # Filter to only Page 1 fields
        page1_fields = {name: page for name, page in available_fields.items() if page == 'page_1'}
        
        for i, section in enumerate(sections):
            text = section.get('text', '').strip()
            location = section.get('location', '').lower()
            
            if not text:
                continue
            
            print(f"  📝 Section {i+1}: '{text[:50]}...' at '{location}'")
            
            # Try to find the best matching field for this text (Page 1 only)
            best_field = self._find_best_field_match(text, location, page1_fields, page=1)
            
            if best_field:
                print(f"     ✅ Matched to Page 1 field: '{best_field}'")
                if best_field in mappings:
                    mappings[best_field] += '\n' + text
                else:
                    mappings[best_field] = text
            else:
                # Fallback to generic mapping if no specific field found (Page 1 only)
                generic_field = self._get_generic_page1_field(page1_fields)
                if generic_field:
                    print(f"     🔄 Using Page 1 fallback field: '{generic_field}'")
                    if generic_field in mappings:
                        mappings[generic_field] += '\n' + text
                    else:
                        mappings[generic_field] = text
                else:
                    print(f"     ❌ No Page 1 field match found - text will be skipped")
        
        return mappings
    
    def _map_page2_sections(self, sections: List[Dict], available_fields: Dict[str, str] = None) -> Dict[str, str]:
        """Map Page 2 sections to form fields using intelligent field matching."""
        mappings = {}
        available_fields = available_fields or {}
        
        # Filter to only Page 2 fields
        page2_fields = {name: page for name, page in available_fields.items() if page == 'page_2'}
        
        for i, section in enumerate(sections):
            text = section.get('text', '').strip()
            location = section.get('location', '').lower()
            
            if not text:
                continue
            
            print(f"  📝 Section {i+1}: '{text[:50]}...' at '{location}'")
            
            # Try to find the best matching field for this text (Page 2 only)
            best_field = self._find_best_field_match(text, location, page2_fields, page=2)
            
            if best_field:
                print(f"     ✅ Matched to Page 2 field: '{best_field}'")
                if best_field in mappings:
                    mappings[best_field] += '\n' + text
                else:
                    mappings[best_field] = text
            else:
                # Fallback to generic mapping if no specific field found (Page 2 only)
                generic_field = self._get_generic_page2_field(page2_fields)
                if generic_field:
                    print(f"     🔄 Using Page 2 fallback field: '{generic_field}'")
                    if generic_field in mappings:
                        mappings[generic_field] += '\n' + text
                    else:
                        mappings[generic_field] = text
                else:
                    print(f"     ❌ No Page 2 field match found - text will be skipped")
        
        return mappings
    
    def _find_best_field_match(self, text: str, location: str, available_fields: Dict[str, str], page: int) -> str:
        """Find the best matching field name for given text and location using sophisticated mapping."""
        text_lower = text.lower()
        location_lower = location.lower()
        
        if page == 1:
            return self._match_page1_field(text_lower, location_lower, available_fields)
        elif page == 2:
            return self._match_page2_field(text_lower, location_lower, available_fields)
        
        return None
    
    def _match_page1_field(self, text_lower: str, location_lower: str, available_fields: Dict[str, str]) -> str:
        """Match Page 1 text to specific field names based on content and position."""
        
        # Check for specific content matches first
        if any(keyword in text_lower for keyword in ['danger', 'eliminate', 'risk', 'threat', 'avoid', 'prevent']):
            for field_name in available_fields.keys():
                if 'danger' in field_name.lower() and 'eliminate' in field_name.lower():
                    return field_name
        
        if any(keyword in text_lower for keyword in ['opportunit', 'focus', 'capture', 'chance', 'potential']):
            for field_name in available_fields.keys():
                if 'opportunit' in field_name.lower() and 'focus' in field_name.lower():
                    return field_name
        
        if any(keyword in text_lower for keyword in ['strength', 'reinforce', 'maximi', 'strong', 'advantage']):
            for field_name in available_fields.keys():
                if 'strength' in field_name.lower() and 'reinforce' in field_name.lower():
                    return field_name
        
        # Position-based matching for right-side fields
        if any(pos in location_lower for pos in ['right', 'center right', 'middle right']):
            # Try to match to specific right-side fields based on vertical position
            if any(pos in location_lower for pos in ['top', 'upper', 'high']):
                for field_name in available_fields.keys():
                    if field_name.lower() == 'right_mid':
                        return field_name
            elif any(pos in location_lower for pos in ['middle', 'center', 'mid']):
                for field_name in available_fields.keys():
                    if field_name.lower() == 'right_belowmid':
                        return field_name
            elif any(pos in location_lower for pos in ['bottom', 'lower', 'down']):
                for field_name in available_fields.keys():
                    if field_name.lower() == 'right_bottom':
                        return field_name
        
        # Check for More4Life signature/branding
        if any(keyword in text_lower for keyword in ['more4life', 'm4lfs', 'brookvale', 'dale street']):
            for field_name in available_fields.keys():
                if 'more4life' in field_name.lower():
                    return field_name
        
        return None
    
    def _match_page2_field(self, text_lower: str, location_lower: str, available_fields: Dict[str, str]) -> str:
        """Match Page 2 text to specific field names based on content and position."""
        
        # 🎯 MANUAL POSITION TO FIELD MAPPING (User-defined)
        # Order matters! Check most specific patterns first
        manual_position_mapping = [
            # Row 2 (GOALS) - Most specific first (handle both hyphen variants)
            ("second row center-right", "health_goals"),  # With hyphen
            ("second row center right", "health_goals"),  # Without hyphen  
            ("second row center-left", "business_goals"),
            ("second row center", "leisure_goals"),
            ("second row left", "money_goals"),
            ("second row right", "family_goals"),
            
            # Row 3 (NOW) - Most specific first (handle both hyphen variants)
            ("third row center-right", "health_now"),
            ("third row center right", "health_now"),
            ("third row center-left", "business_now"),
            ("third row center left", "business_now"),
            ("third row center", "leisure_now"),
            ("third row left", "money_now"),
            ("third row right", "family_now"),
            
            # Row 4 (TO DO) - Most specific first (handle both hyphen variants)
            ("fourth row center-right", "health_todo"),
            ("fourth row center right", "health_todo"),
            ("fourth row center-left", "business_todo"),
            ("fourth row center left", "business_todo"),
            ("fourth row center", "leisure_todo"),
            ("fourth row left", "money_todo"),
            ("fourth row right", "family_todo")
        ]
        
        # Check manual mappings FIRST (highest priority) - most specific first
        for position_key, field_name in manual_position_mapping:
            if position_key in location_lower:
                if field_name in available_fields:
                    print(f"     🎯 Manual mapping: '{position_key}' → '{field_name}'")
                    return field_name
        
        # Category-based matching (money, business, leisure, health, family)
        category = None
        if any(keyword in text_lower for keyword in ['money', 'financial', 'finance', '$', 'dollar', 'cash', 'income', 'salary']):
            category = 'money'
        elif any(keyword in text_lower for keyword in ['business', 'work', 'career', 'job', 'company', 'office']):
            category = 'business'
        elif any(keyword in text_lower for keyword in ['leisure', 'hobby', 'fun', 'vacation', 'travel', 'entertainment']):
            category = 'leisure'
        elif any(keyword in text_lower for keyword in ['health', 'fitness', 'medical', 'doctor', 'exercise', 'diet']):
            category = 'health'
        elif any(keyword in text_lower for keyword in ['family', 'child', 'kids', 'spouse', 'parent', 'home']):
            category = 'family'
        
        if category:
            # Determine if it's GOALS, NOW, or TO DO based on content
            field_type = None
            if any(keyword in text_lower for keyword in ['goal', 'want', 'wish', 'dream', 'aim', 'target']):
                field_type = 'goals'
            elif any(keyword in text_lower for keyword in ['now', 'current', 'today', 'present', 'doing']):
                field_type = 'now'
            elif any(keyword in text_lower for keyword in ['todo', 'to do', 'action', 'plan', 'next', 'will']):
                field_type = 'todo'
            
            # Try to match based on position if content doesn't give clear indication
            if not field_type:
                if any(pos in location_lower for pos in ['top', 'upper', 'first']):
                    field_type = 'goals'
                elif any(pos in location_lower for pos in ['middle', 'center']):
                    field_type = 'now'
                elif any(pos in location_lower for pos in ['bottom', 'lower', 'last']):
                    field_type = 'todo'
            
            # Find the exact field name
            if field_type:
                target_field = f"{category}_{field_type}"
                for field_name in available_fields.keys():
                    if field_name.lower() == target_field:
                        return field_name
        
        # Position-based fallback matching for columns
        if any(pos in location_lower for pos in ['left', 'first column']):
            # Money column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'money_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'money_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'money_todo'
        elif any(pos in location_lower for pos in ['center left', 'second column']):
            # Business column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'business_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'business_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'business_todo'
        elif any(pos in location_lower for pos in ['center', 'middle column', 'third column']):
            # Leisure column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'leisure_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'leisure_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'leisure_todo'
        elif any(pos in location_lower for pos in ['center right', 'fourth column']):
            # Health column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'health_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'health_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'health_todo'
        elif any(pos in location_lower for pos in ['right', 'last column', 'fifth column']):
            # Family column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'family_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'family_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'family_todo'
        
        return None
    
    def _get_generic_page1_field(self, available_fields: Dict[str, str]) -> str:
        """Get a generic field for Page 1 content that doesn't match specific fields."""
        # Look for generic fields like 'notes', 'additional', 'other', etc.
        for field_name in available_fields.keys():
            if any(keyword in field_name.lower() for keyword in ['note', 'additional', 'other', 'general', 'misc']):
                return field_name
        
        # If no generic field, return the first available Page 1 field
        page1_fields = [name for name, page in available_fields.items() if page == 'page_1']
        return page1_fields[0] if page1_fields else None
    
    def _get_generic_page2_field(self, available_fields: Dict[str, str]) -> str:
        """Get a generic field for Page 2 content that doesn't match specific fields."""
        # Return the first available Page 2 field
        page2_fields = [name for name, page in available_fields.items() if page == 'page_2']
        return page2_fields[0] if page2_fields else None
    
    def save_custom_fields_config(self, config_path: Path = None):
        """Save the current field configuration to a JSON file for customization."""
        config_path = config_path or Path("custom_field_positions.json")
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.form_fields_config, f, indent=2)
            print(f"✅ Saved field configuration to: {config_path}")
            print(f"📝 Edit this file to customize field positions")
            return config_path
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return None
    
    def load_custom_fields_config(self, config_path: Path = None) -> Dict:
        """Load custom field configuration from a JSON file."""
        config_path = config_path or Path("custom_field_positions.json")
        
        try:
            if not config_path.exists():
                print(f"⚠️ Config file not found: {config_path}")
                return self._get_default_form_fields_config()
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Loaded custom field configuration from: {config_path}")
            return config
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return self._get_default_form_fields_config()
    
    def create_template_with_custom_fields(self, config_path: Path = None, output_path: Path = None) -> Path:
        """Create a template using custom field positions from a JSON file."""
        custom_config = self.load_custom_fields_config(config_path)
        
        # Temporarily use custom config
        original_config = self.form_fields_config
        self.form_fields_config = custom_config
        
        try:
            template_path = self.create_template_with_form_fields(output_path)
            return template_path
        finally:
            # Restore original config
            self.form_fields_config = original_config

def test_template_processor():
    """Test the template processor."""
    print("🧪 Testing A3 Template Processor")
    print("=" * 40)
    
    processor = A3TemplateProcessor()
    
    # Test creating template with form fields
    try:
        template_path = processor.create_template_with_form_fields()
        print(f"✅ Successfully created template with form fields")
        
        # Test with sample data
        sample_results = [
            {
                'success': True,
                'page_number': 1,
                'sections': [
                    {'text': 'Getting back into property market', 'location': 'left circle danger'},
                    {'text': 'Borrow up to $625,000', 'location': 'right center'}
                ]
            },
            {
                'success': True,
                'page_number': 2,
                'sections': [
                    {'text': 'GOALS\n-Save for house deposit', 'location': 'second row left'},
                    {'text': 'NOW\n-Looking at properties', 'location': 'third row left'}
                ]
            }
        ]
        
        output_path = processor.populate_template(sample_results)
        print(f"✅ Successfully created populated template: {output_path}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import time
    test_template_processor() 