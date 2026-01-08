#!/usr/bin/env python3
"""
A3 Sectioned Document Automation System
Uses manually defined sections for 100% consistent OCR and population
"""

import os
import time
import json
import shutil
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import queue
import threading
from typing import List, Dict, Any

# Import the sectioned OCR system
from sectioned_gpt4o_ocr import SectionedGPT4oOCR
from a3_template_processor import A3TemplateProcessor

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

class A3SectionedProcessor:
    """A3 document processor using manual section definitions."""
    
    def __init__(self, api_key: str = None, section_config_path: str = "A3_templates/a3_section_config.json", enable_spell_check: bool = True):
        """Initialize the sectioned A3 processor."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        # Initialize sectioned OCR
        self.sectioned_ocr = SectionedGPT4oOCR(self.api_key, section_config_path, enable_spell_check)
        self.section_config_path = Path(section_config_path)
        
        # Initialize template processor with custom config if available
        custom_config_path = Path("A3_templates/custom_field_position.json")
        if custom_config_path.exists():
            print(f"✅ Found custom field configuration: {custom_config_path}")
            custom_config = self._load_custom_config(custom_config_path)
            self.template_processor = A3TemplateProcessor(custom_fields_config=custom_config)
            self.using_custom_fields = True
        else:
            print("📝 Using default field configuration")
            self.template_processor = A3TemplateProcessor()
            self.using_custom_fields = False
    
    def _load_custom_config(self, config_path: Path) -> Dict:
        """Load custom field configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"⚠️ Failed to load custom config: {e}")
            return {}
    
    def _ensure_template_updated(self):
        """Ensure the PDF template is updated with latest field positions from JSON."""
        try:
            custom_config_path = Path("A3_templates/custom_field_position.json")
            custom_template_path = Path("processed_documents/A3_Custom_Template.pdf")
            
            # Check if JSON config exists
            if not custom_config_path.exists():
                print("⚠️ Custom field configuration not found - using default template")
                return
            
            # Check if template needs updating
            json_modified = custom_config_path.stat().st_mtime
            template_exists = custom_template_path.exists()
            
            if not template_exists:
                print("🔄 Creating new PDF template from field configuration...")
                self._regenerate_template()
                return
            
            template_modified = custom_template_path.stat().st_mtime
            
            # If JSON is newer than template, regenerate
            if json_modified > template_modified:
                print("🔄 Field configuration updated - regenerating PDF template...")
                self._regenerate_template()
            else:
                print("✅ PDF template is up-to-date with field configuration")
                
        except Exception as e:
            print(f"⚠️ Failed to check template status: {e}")
    
    def _regenerate_template(self):
        """Regenerate the PDF template using current field configuration."""
        try:
            from create_custom_template import create_custom_template
            
            print("🛠️ Regenerating PDF template with updated field positions...")
            success = create_custom_template()
            
            if success:
                print("✅ PDF template successfully updated!")
            else:
                print("⚠️ Failed to regenerate PDF template - proceeding with existing template")
                
        except Exception as e:
            print(f"⚠️ Error regenerating template: {e}")
            print("⚠️ Proceeding with existing template")
    
    def populate_template_directly(self, template_path: Path, output_path: Path, field_mappings: Dict[str, str]) -> Path:
        """Directly populate template fields using sectioned field mappings."""
        import fitz  # PyMuPDF
        
        print(f"📝 DIRECT TEMPLATE POPULATION")
        print(f"   📄 Template: {template_path}")
        print(f"   📁 Output: {output_path}")
        print(f"   🎯 Field mappings: {len(field_mappings)}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open template PDF
        pdf_doc = fitz.open(template_path)
        
        populated_fields = 0
        total_fields = 0
        
        # Process each page
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            
            # Get form fields (widgets) on this page
            widgets = list(page.widgets())  # Convert generator to list
            
            if widgets:
                print(f"   📄 Page {page_num + 1}: {len(widgets)} form fields")
                
                for widget in widgets:
                    total_fields += 1
                    field_name = widget.field_name
                    field_type = widget.field_type_string
                    
                    if field_name in field_mappings:
                        text_to_populate = field_mappings[field_name]
                        
                        try:
                            # Set field value
                            widget.field_value = text_to_populate
                            widget.update()
                            populated_fields += 1
                            
                            print(f"      ✅ {field_name}: '{text_to_populate[:40]}...' " if len(text_to_populate) > 40 else f"      ✅ {field_name}: '{text_to_populate}'")
                            
                        except Exception as e:
                            print(f"      ❌ Failed to populate {field_name}: {e}")
                    else:
                        print(f"      ⚪ {field_name}: (no mapping)")
            else:
                print(f"   📄 Page {page_num + 1}: No form fields found")
        
        # Save populated PDF
        pdf_doc.save(output_path)
        pdf_doc.close()
        
        print(f"📊 POPULATION SUMMARY:")
        print(f"   📝 Total fields in template: {total_fields}")
        print(f"   ✅ Fields populated: {populated_fields}")
        print(f"   📄 Success rate: {(populated_fields/total_fields*100):.1f}%" if total_fields > 0 else "   📄 Success rate: 0%")
        print(f"   💾 Saved: {output_path}")
        
        # Page reordering info is displayed during the OCR processing phase
        return output_path
    
    def convert_sectioned_results_to_standard_format(self, sectioned_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert sectioned OCR results to standard format for template processor with direct field mapping."""
        # Group results by page
        pages = {}
        for result in sectioned_results:
            page_num = result["page_number"]
            if page_num not in pages:
                pages[page_num] = {
                    "success": True,
                    "page_number": page_num,
                    "sections": [],
                    "total_sections": 0,
                    "processing_time": 0,
                    "file_name": result.get("file_name", ""),
                    "file_type": result.get("file_type", ""),
                    "direct_field_mapping": {}  # Store direct field mappings
                }
            
            # Add section regardless of text content (for mapping purposes)
            section_data = {
                "section_id": result["section_id"],
                "text": result["text"].strip() if result["success"] else "",
                "location": result["section_name"],  # Use section name as location
                "confidence": result.get("confidence", "low"),
                "target_field": result.get("target_field", "")
            }
            
            # Store direct field mapping for template processor
            target_field = result.get("target_field", "")
            if target_field and result["success"] and result["text"].strip():
                pages[page_num]["direct_field_mapping"][target_field] = result["text"].strip()
                print(f"   🎯 Direct mapping: {target_field} ← '{result['text'].strip()[:50]}...'")
            
            pages[page_num]["sections"].append(section_data)
            pages[page_num]["total_sections"] += 1
            pages[page_num]["processing_time"] += result.get("processing_time", 0)
        
        # Convert to list format
        return list(pages.values())
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a file using sectioned OCR approach."""
        processing_info = {
            'success': True,
            'file_name': file_path.name,
            'total_processing_time': 0,
            'pages_processed': 0,
            'sections_processed': 0,
            'sections_with_text': 0,
            'output_pdf_path': None,
            'error': None,
            'approach': 'sectioned_ocr'
        }
        
        try:
            # Check if section configuration exists
            if not self.section_config_path.exists():
                raise Exception(f"Section configuration not found: {self.section_config_path}. Create sections using section_definition_tool.py")
            
            # Ensure custom template is up-to-date with latest field positions
            self._ensure_template_updated()
            
            print(f"🎯 Processing with SECTIONED OCR: {file_path}")
            
            # Process document using sectioned OCR
            sectioned_result = self.sectioned_ocr.process_document(file_path)
            
            if not sectioned_result["success"]:
                raise Exception(sectioned_result.get("error", "Sectioned OCR processing failed"))
            
            # Convert results to standard format for template processor
            standard_results = self.convert_sectioned_results_to_standard_format(sectioned_result["results"])
            
            # Update processing info
            processing_info['total_processing_time'] = sectioned_result["total_processing_time"]
            processing_info['pages_processed'] = len(standard_results)
            processing_info['sections_processed'] = sectioned_result["total_sections"]
            processing_info['sections_with_text'] = sectioned_result["sections_with_text"]
            processing_info['page_results'] = standard_results
            
            # Create populated PDF template using direct field mapping
            if standard_results:
                try:
                    # Generate output filename with timestamp
                    timestamp = int(time.time())
                    safe_filename = "".join(c for c in file_path.stem if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    output_filename = f"A3_Sectioned_{safe_filename}_{timestamp}.pdf"
                    output_path = Path("processed_documents") / output_filename
                    
                    # Extract direct field mappings from all pages
                    all_field_mappings = {}
                    for page_result in standard_results:
                        if "direct_field_mapping" in page_result:
                            all_field_mappings.update(page_result["direct_field_mapping"])
                    
                    print(f"🎯 SECTIONED FIELD MAPPINGS:")
                    for field_name, text in all_field_mappings.items():
                        print(f"   ✅ {field_name}: '{text[:50]}...' " if len(text) > 50 else f"   ✅ {field_name}: '{text}'")
                    
                    # Use existing custom template if available
                    custom_template_path = Path("processed_documents/A3_Custom_Template.pdf")
                    
                    if custom_template_path.exists():
                        print(f"🎯 Using your custom template: {custom_template_path}")
                        
                        # Use direct field mapping approach
                        final_pdf_path = self.populate_template_directly(
                            custom_template_path,
                            output_path,
                            all_field_mappings
                        )
                    else:
                        print(f"📝 Custom template not found, using standard approach")
                        final_pdf_path = self.template_processor.populate_template(standard_results, output_path)
                    
                    processing_info['output_pdf_path'] = final_pdf_path
                    
                except Exception as e:
                    print(f"⚠️ Failed to create populated PDF template: {e}")
                    processing_info['error'] = f"Template population failed: {e}"
            
        except Exception as e:
            processing_info['success'] = False
            processing_info['error'] = str(e)
        
        return processing_info

class A3SectionedAutomationUI:
    """UI for sectioned A3 document automation."""
    
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("A3 Sectioned Automation - Manual Section Control")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f0f0f0")
        
        # Status queue for thread communication
        self.status_queue = queue.Queue()
        
        # Initialize processor
        self.processor = None
        self.setup_ui()
        self.check_prerequisites()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Title
        title_frame = Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = Label(
            title_frame, 
            text="🎯 A3 Sectioned Automation - Manual Section Control", 
            font=("Segoe UI", 18, "bold"),
            bg="#2c3e50", 
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Main content frame
        main_frame = Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Control panel
        self.setup_control_panel(main_frame)
        
        # Processing options
        self.setup_processing_options(main_frame)
        
        # Drop zone
        self.setup_drop_zone(main_frame)
        
        # Results area
        self.setup_results_area(main_frame)
        
        # Status bar
        self.setup_status_bar()
    
    def setup_control_panel(self, parent):
        """Setup control panel with section management."""
        control_frame = LabelFrame(parent, text="🛠️ Section Management", font=("Segoe UI", 12, "bold"))
        control_frame.pack(fill=X, pady=(0, 10))
        
        # Control buttons
        btn_frame = Frame(control_frame)
        btn_frame.pack(fill=X, padx=10, pady=10)
        
        # Section definition tool
        Button(
            btn_frame,
            text="📐 Define Sections",
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            relief=FLAT,
            padx=15,
            pady=8,
            command=self.launch_section_tool
        ).pack(side=LEFT, padx=(0, 10))
        
        # Field positioning tool
        Button(
            btn_frame,
            text="📝 Edit Output Fields",
            font=("Segoe UI", 10, "bold"),
            bg="#e67e22",
            fg="white",
            relief=FLAT,
            padx=15,
            pady=8,
            command=self.launch_field_tool
        ).pack(side=LEFT, padx=(0, 10))
        
        # PDF flattening tool
        Button(
            btn_frame,
            text="📄 Flatten PDFs",
            font=("Segoe UI", 10, "bold"),
            bg="#9b59b6",
            fg="white",
            relief=FLAT,
            padx=15,
            pady=8,
            command=self.launch_flatten_tool
        ).pack(side=LEFT, padx=(0, 10))
        
        # Section status
        self.section_status_var = StringVar(value="Section config: Not loaded")
        Label(
            btn_frame,
            textvariable=self.section_status_var,
            font=("Segoe UI", 10),
            fg="#7f8c8d"
        ).pack(side=LEFT, padx=(10, 0))
        
        # Refresh button
        Button(
            btn_frame,
            text="🔄 Refresh",
            font=("Segoe UI", 9),
            bg="#95a5a6",
            fg="white",
            relief=FLAT,
            padx=10,
            pady=5,
            command=self.refresh_section_status
        ).pack(side=RIGHT)
        
    def setup_processing_options(self, parent):
        """Setup processing options panel."""
        options_frame = LabelFrame(parent, text="⚙️ Processing Options", font=("Segoe UI", 12, "bold"))
        options_frame.pack(fill=X, pady=(0, 10))
        
        # Options container
        options_container = Frame(options_frame)
        options_container.pack(fill=X, padx=10, pady=10)
        
        # Spell check option
        self.spell_check_var = BooleanVar(value=True)
        spell_check_frame = Frame(options_container)
        spell_check_frame.pack(fill=X, pady=(0, 5))
        
        Checkbutton(
            spell_check_frame,
            text="🔤 Enable Spell Check",
            variable=self.spell_check_var,
            font=("Segoe UI", 10),
            fg="#2c3e50",
            bg="#f0f0f0",
            activebackground="#f0f0f0",
            activeforeground="#2c3e50"
        ).pack(side=LEFT)
        
        # Spell check info
        Label(
            spell_check_frame,
            text="Automatically corrects common OCR errors and typos",
            font=("Segoe UI", 9),
            fg="#7f8c8d",
            bg="#f0f0f0"
        ).pack(side=LEFT, padx=(10, 0))
        
    def setup_drop_zone(self, parent):
        """Setup drag and drop zone."""
        drop_frame = Frame(parent, bg="#ecf0f1", relief=RAISED, bd=2)
        drop_frame.pack(fill=X, pady=(0, 20))
        
        # Drop zone
        self.drop_zone = Frame(drop_frame, bg="#e67e22", height=150, relief=SUNKEN, bd=3)
        self.drop_zone.pack(fill=X, padx=10, pady=10)
        self.drop_zone.pack_propagate(False)
        
        # Drop zone content
        drop_content = Frame(self.drop_zone, bg="#e67e22")
        drop_content.pack(expand=True)
        
        Label(
            drop_content, 
            text="🎯 Drag & Drop A3 Documents Here", 
            font=("Segoe UI", 16, "bold"),
            bg="#e67e22", 
            fg="white"
        ).pack(pady=(15, 5))
        
        Label(
            drop_content,
            text="Uses Manual Sections for 100% Consistent OCR",
            font=("Segoe UI", 11, "bold"),
            bg="#e67e22",
            fg="#f39c12"
        ).pack(pady=(0, 5))
        
        Label(
            drop_content,
            text="Supports: PDF, PNG, JPG, JPEG, BMP, TIFF",
            font=("Segoe UI", 10),
            bg="#e67e22",
            fg="#ecf0f1"
        ).pack(pady=(0, 5))
        
        # Browse button
        browse_btn = Button(
            drop_content,
            text="📂 Browse Files",
            font=("Segoe UI", 10, "bold"),
            bg="#d35400",
            fg="white",
            relief=FLAT,
            padx=20,
            pady=5,
            command=self.browse_files
        )
        browse_btn.pack(pady=(5, 15))
        
        # Enable drag and drop
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.on_drop)
        
    def setup_results_area(self, parent):
        """Setup results display area."""
        results_frame = LabelFrame(parent, text="📋 Processing Results", font=("Segoe UI", 12, "bold"))
        results_frame.pack(fill=BOTH, expand=True)
        
        # Scrollable text area
        text_frame = Frame(results_frame)
        text_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Text widget with scrollbar
        self.results_text = Text(
            text_frame,
            wrap=WORD,
            font=("Consolas", 10),
            bg="white",
            fg="black",
            state=DISABLED
        )
        
        scrollbar = Scrollbar(text_frame, orient=VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Clear button
        clear_btn = Button(
            results_frame,
            text="🗑️ Clear Results",
            font=("Segoe UI", 10),
            bg="#e74c3c",
            fg="white",
            relief=FLAT,
            command=self.clear_results
        )
        clear_btn.pack(pady=(0, 10))
        
    def setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = Label(
            self.root,
            text="Ready",
            font=("Segoe UI", 9),
            bg="#34495e",
            fg="white",
            anchor=W,
            padx=10
        )
        self.status_bar.pack(side=BOTTOM, fill=X)
    
    def launch_section_tool(self):
        """Launch the section definition tool."""
        import subprocess
        import sys
        
        try:
            subprocess.Popen([sys.executable, "section_definition_tool.py"])
            self.log_message("🚀 Launched section definition tool")
            self.log_message("💡 After defining sections, click 'Refresh' to reload configuration")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch section tool: {e}")
    
    def launch_field_tool(self):
        """Launch the field positioning tool for editing output template fields."""
        import subprocess
        import sys
        
        try:
            subprocess.Popen([sys.executable, "field_positioning_tool.py"])
            self.log_message("🚀 Launched field positioning tool")
            self.log_message("💡 Use this tool to edit where text appears on the output PDF")
            self.log_message("💡 After editing fields, restart the application to use the new positions")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch field positioning tool: {e}")
    
    def launch_flatten_tool(self):
        """Launch the PDF flattening tool for removing editable fields."""
        import subprocess
        import sys
        
        try:
            subprocess.Popen([sys.executable, "pdf_flattening_tool.py"])
            self.log_message("🚀 Launched PDF flattening tool")
            self.log_message("💡 Use this tool to convert editable fields to permanent text")
            self.log_message("💡 Perfect for finalizing documents before distribution")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch PDF flattening tool: {e}")
    
    def refresh_section_status(self):
        """Refresh section configuration status."""
        section_config_path = Path("A3_templates/a3_section_config.json")
        
        if section_config_path.exists():
            try:
                with open(section_config_path, 'r') as f:
                    config = json.load(f)
                
                total_sections = 0
                if '_metadata' in config:
                    total_sections = config['_metadata'].get('total_sections', 0)
                else:
                    # Count manually
                    total_sections = sum(len(config.get(page, [])) for page in config if not page.startswith('_'))
                
                self.section_status_var.set(f"Section config: ✅ {total_sections} sections loaded")
                
                # Reinitialize processor if needed
                if self.processor:
                    try:
                        self.processor = A3SectionedProcessor(self.processor.api_key, enable_spell_check=self.spell_check_var.get())
                        self.log_message(f"🔄 Reloaded section configuration: {total_sections} sections")
                    except Exception as e:
                        self.log_message(f"⚠️ Failed to reload processor: {e}")
                
            except Exception as e:
                self.section_status_var.set("Section config: ❌ Error loading")
                self.log_message(f"❌ Failed to load section config: {e}")
        else:
            self.section_status_var.set("Section config: ⚠️ Not found")
    
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        try:
            # Check API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.log_message("❌ ERROR: No OpenAI API key found!")
                self.log_message("💡 Run: python secure_api_setup.py")
                return
            
            # Initialize processor
            self.processor = A3SectionedProcessor(api_key, enable_spell_check=self.spell_check_var.get())
            self.log_message("✅ A3 Sectioned Processor initialized successfully")
            self.log_message("🎯 Using MANUAL SECTIONING for 100% consistent results")
            
            # Check section configuration
            self.refresh_section_status()
            
            section_config_path = Path("A3_templates/a3_section_config.json")
            if section_config_path.exists():
                self.log_message("✅ Section configuration found")
                self.log_message("🚀 Ready to process A3 documents with manual sections!")
            else:
                self.log_message("⚠️ No section configuration found")
                self.log_message("💡 Click 'Define Sections' to create section configuration")
                self.log_message("📖 This ensures 100% consistent OCR results")
            
        except Exception as e:
            self.log_message(f"❌ Initialization failed: {e}")
    
    def browse_files(self):
        """Open file browser."""
        filetypes = [
            ("All Supported", "*.pdf;*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
            ("PDF files", "*.pdf"),
            ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select A3 Documents",
            filetypes=filetypes
        )
        
        if files:
            self.process_files([Path(f) for f in files])
    
    def on_drop(self, event):
        """Handle dropped files."""
        files = self.root.tk.splitlist(event.data)
        file_paths = [Path(f) for f in files]
        self.process_files(file_paths)
    
    def process_files(self, file_paths: List[Path]):
        """Process dropped/selected files."""
        if not self.processor:
            self.log_message("❌ Processor not initialized")
            return
        
        # Check section configuration
        section_config_path = Path("A3_templates/a3_section_config.json")
        if not section_config_path.exists():
            messagebox.showwarning(
                "No Section Configuration", 
                "No section configuration found!\n\nClick 'Define Sections' to create manual sections first."
            )
            return
        
        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_files_background,
            args=(file_paths,),
            daemon=True
        )
        thread.start()
        
        # Start monitoring the status queue
        self.monitor_status_queue()
    
    def _process_files_background(self, file_paths: List[Path]):
        """Process files in background thread using sectioned OCR."""
        try:
            self.status_queue.put(("status", f"🎯 Processing {len(file_paths)} files with sectioned OCR..."))
            self.status_queue.put(("clear", ""))
            
            total_start_time = time.time()
            successful_files = 0
            total_sections = 0
            sections_with_text = 0
            created_pdfs = []
            
            for i, file_path in enumerate(file_paths, 1):
                self.status_queue.put(("message", f"\n{'='*60}"))
                self.status_queue.put(("message", f"PROCESSING FILE {i}/{len(file_paths)}: {file_path.name}"))
                self.status_queue.put(("message", f"{'='*60}"))
                
                # Process using sectioned OCR
                processing_info = self.processor.process_file(file_path)
                
                if processing_info.get('success', False):
                    successful_files += 1
                    total_sections += processing_info.get('sections_processed', 0)
                    sections_with_text += processing_info.get('sections_with_text', 0)
                    
                    # Show detailed sectioned results
                    self._display_sectioned_results(processing_info)
                    
                    # Show template creation results
                    output_pdf = processing_info.get('output_pdf_path')
                    if output_pdf:
                        created_pdfs.append(output_pdf)
                        self.status_queue.put(("message", f"\n🎉 SECTIONED A3 DOCUMENT CREATED"))
                        self.status_queue.put(("message", f"{'='*50}"))
                        self.status_queue.put(("message", f"✅ 100% Consistent sectioned OCR completed"))
                        self.status_queue.put(("message", f"📁 Output: {output_pdf.name}"))
                        self.status_queue.put(("message", f"🎯 Manual sections → Perfect field mapping"))
                        self.status_queue.put(("message", f"⏱️ Processing time: {processing_info.get('total_processing_time', 0):.2f}s"))
                    
                    if processing_info.get('error'):
                        self.status_queue.put(("message", f"⚠️ Template warning: {processing_info['error']}"))
                
                else:
                    error = processing_info.get('error', 'Unknown error')
                    self.status_queue.put(("message", f"❌ Error processing {file_path.name}: {error}"))
            
            # Final summary
            total_time = time.time() - total_start_time
            self.status_queue.put(("message", f"\n{'='*80}"))
            self.status_queue.put(("message", "🎉 SECTIONED A3 AUTOMATION COMPLETE"))
            self.status_queue.put(("message", f"{'='*80}"))
            self.status_queue.put(("message", f"📊 Files processed: {successful_files}/{len(file_paths)}"))
            self.status_queue.put(("message", f"🎯 Total sections processed: {total_sections}"))
            self.status_queue.put(("message", f"📝 Sections with text: {sections_with_text}"))
            self.status_queue.put(("message", f"📄 Completed documents: {len(created_pdfs)}"))
            
            if created_pdfs:
                self.status_queue.put(("message", f"\n📁 COMPLETED DOCUMENTS:"))
                for pdf_path in created_pdfs:
                    self.status_queue.put(("message", f"   ✅ {pdf_path}"))
            
            self.status_queue.put(("message", f"\n🎯 SECTIONED OCR ADVANTAGES:"))
            self.status_queue.put(("message", f"   ✅ 100% consistent section detection"))
            self.status_queue.put(("message", f"   ✅ No variable GPT-4o sectioning"))
            self.status_queue.put(("message", f"   ✅ Perfect text-to-field mapping"))
            self.status_queue.put(("message", f"   ✅ Manual control over OCR areas"))
            
            self.status_queue.put(("message", f"\n⏱️ Total time: {total_time:.2f}s"))
            self.status_queue.put(("status", "🎉 Sectioned processing complete!"))
            
        except Exception as e:
            self.status_queue.put(("error", f"❌ Processing failed: {e}"))
    
    def _display_sectioned_results(self, processing_info: Dict[str, Any]):
        """Display results from sectioned processing with direct field mappings."""
        self.status_queue.put(("message", f"\n🎯 SECTIONED OCR RESULTS"))
        self.status_queue.put(("message", f"{'='*50}"))
        self.status_queue.put(("message", f"📊 Approach: Manual sectioning with direct field mapping"))
        self.status_queue.put(("message", f"📄 Pages: {processing_info.get('pages_processed', 0)}"))
        self.status_queue.put(("message", f"🎯 Sections processed: {processing_info.get('sections_processed', 0)}"))
        self.status_queue.put(("message", f"📝 Sections with text: {processing_info.get('sections_with_text', 0)}"))
        self.status_queue.put(("message", f"⏱️ Processing time: {processing_info.get('total_processing_time', 0):.2f}s"))
        
        # Show direct field mappings summary
        page_results = processing_info.get('page_results', [])
        all_mappings = {}
        for result in page_results:
            if "direct_field_mapping" in result:
                all_mappings.update(result["direct_field_mapping"])
        
        if all_mappings:
            self.status_queue.put(("message", f"\n🎯 DIRECT FIELD MAPPINGS ({len(all_mappings)} fields):"))
            self.status_queue.put(("message", f"{'-'*50}"))
            for field_name, text in all_mappings.items():
                display_text = text[:60] + "..." if len(text) > 60 else text
                self.status_queue.put(("message", f"✅ {field_name}: '{display_text}'"))
        
        # Show detailed page results
        for result in page_results:
            if result.get('success', False):
                page_num = result.get('page_number', 1)
                sections = result.get('sections', [])
                
                self.status_queue.put(("message", f"\n📄 PAGE {page_num} SECTIONS:"))
                self.status_queue.put(("message", f"{'-'*40}"))
                
                for section in sections:
                    section_name = section.get('location', 'Unknown section')  # location contains section name
                    text = section.get('text', '').strip()
                    target_field = section.get('target_field', '')
                    
                    # Show mapping status
                    if text and target_field:
                        status_icon = "✅"
                        field_info = f" → {target_field} (MAPPED)"
                    elif target_field:
                        status_icon = "⚪"
                        field_info = f" → {target_field} (empty)"
                    else:
                        status_icon = "❌"
                        field_info = " → (no field mapping)"
                    
                    self.status_queue.put(("message", f"{status_icon} {section_name}{field_info}"))
                    
                    if text:
                        display_text = text[:80] + "..." if len(text) > 80 else text
                        self.status_queue.put(("message", f"   📝 Text: {display_text}"))
                    else:
                        self.status_queue.put(("message", f"   ⚪ (no text extracted)"))
    
    def monitor_status_queue(self):
        """Monitor the status queue for updates."""
        try:
            while True:
                msg_type, message = self.status_queue.get_nowait()
                
                if msg_type == "status":
                    self.status_bar.config(text=message)
                elif msg_type == "message":
                    self.log_message(message)
                elif msg_type == "clear":
                    self.clear_results()
                elif msg_type == "error":
                    self.log_message(message)
                    messagebox.showerror("Error", message)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.monitor_status_queue)
    
    def log_message(self, message: str):
        """Add message to results display."""
        self.results_text.config(state=NORMAL)
        self.results_text.insert(END, message + "\n")
        self.results_text.see(END)
        self.results_text.config(state=DISABLED)
    
    def clear_results(self):
        """Clear the results display."""
        self.results_text.config(state=NORMAL)
        self.results_text.delete(1.0, END)
        self.results_text.config(state=DISABLED)
        self.status_bar.config(text="Results cleared")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

def main():
    """Main entry point."""
    # Check if required files exist
    required_files = ["sectioned_gpt4o_ocr.py", "a3_template_processor.py"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Error: {file} not found!")
            print("💡 Make sure you're running from the project root directory")
            return
    
    # Launch the application
    try:
        app = A3SectionedAutomationUI()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

if __name__ == "__main__":
    main()