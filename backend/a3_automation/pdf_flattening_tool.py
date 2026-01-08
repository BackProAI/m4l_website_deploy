#!/usr/bin/env python3
"""
PDF Flattening Tool
Converts editable PDF form fields to permanent text, removing the ability to edit them.
Perfect for finalizing documents before distribution.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from pathlib import Path
import os
from typing import List, Optional

class PDFFlatteningTool:
    """Tool for flattening PDF form fields into permanent text."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📄 PDF Flattening Tool - Remove Editable Fields")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")
        
        # Data
        self.input_files: List[Path] = []
        self.output_folder: Optional[Path] = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface with scrollable content."""
        # Title (fixed at top)
        title_frame = tk.Frame(self.root, bg="#34495e", height=80)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="📄 PDF Flattening Tool - Convert Editable Fields to Permanent Text", 
            font=("Segoe UI", 16, "bold"),
            bg="#34495e", 
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Create main scrollable frame
        self.setup_scrollable_content()
        
        # Description
        desc_frame = tk.LabelFrame(self.scrollable_frame, text="ℹ️ What This Tool Does", font=("Segoe UI", 12, "bold"))
        desc_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, bg="#ecf0f1", relief=tk.FLAT)
        desc_text.pack(fill=tk.X, padx=10, pady=10)
        desc_text.insert(tk.END, 
            "This tool converts editable PDF form fields (blue text boxes) into permanent text that cannot be edited. "
            "Perfect for finalizing documents before sending to clients or archiving. The enhanced tool automatically "
            "captures exact content from Adobe Acrobat or online PDF editors, filters out null/empty values, and "
            "preserves formatting, alignment, and spacing exactly as they appear in the original. Empty fields remain "
            "blank (no 'null' text). Special handling for Right_mid, Right_belowmid, and Right_bottom fields prevents "
            "unwanted lines when these fields are empty. The blue field borders disappear, leaving only clean, professional text."
        )
        desc_text.config(state=tk.DISABLED)
        
        # File selection
        self.setup_file_selection(self.scrollable_frame)
        
        # Output options
        self.setup_output_options(self.scrollable_frame)
        
        # Processing controls
        self.setup_processing_controls(self.scrollable_frame)
        
        # Results area
        self.setup_results_area(self.scrollable_frame)
    
    def setup_scrollable_content(self):
        """Create a scrollable content area."""
        # Create main container frame
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(container, bg="#f0f0f0", highlightthickness=0)
        
        # Create scrollbar
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        # Create the scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.bind_mousewheel()
        
        # Bind canvas resize to adjust scrollable frame width
        self.canvas.bind('<Configure>', self.on_canvas_configure)
    
    def on_canvas_configure(self, event):
        """Handle canvas resize to adjust scrollable frame width."""
        # Update the scrollable frame width to match canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def bind_mousewheel(self):
        """Bind mousewheel events for scrolling."""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind mousewheel when mouse enters the canvas
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def setup_file_selection(self, parent):
        """Setup file selection area."""
        file_frame = tk.LabelFrame(parent, text="📁 Select PDF Files to Flatten", font=("Segoe UI", 12, "bold"))
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), padx=20)
        
        # Buttons
        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="📄 Add PDF Files",
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.add_files
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="📂 Add Folder",
            font=("Segoe UI", 10, "bold"),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.add_folder
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="🗑️ Clear List",
            font=("Segoe UI", 10),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.clear_files
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # File list
        list_frame = tk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Listbox with scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            height=8
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
    
    def setup_output_options(self, parent):
        """Setup output options."""
        output_frame = tk.LabelFrame(parent, text="📁 Output Settings", font=("Segoe UI", 12, "bold"))
        output_frame.pack(fill=tk.X, pady=(0, 10), padx=20)
        
        # Output folder selection
        folder_frame = tk.Frame(output_frame)
        folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(folder_frame, text="Output Folder:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        self.output_folder_var = tk.StringVar(value="Same as input files")
        self.output_label = tk.Label(
            folder_frame, 
            textvariable=self.output_folder_var,
            font=("Segoe UI", 9),
            fg="#7f8c8d",
            relief=tk.SUNKEN,
            padx=10,
            pady=5,
            bg="white"
        )
        self.output_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Button(
            folder_frame,
            text="📂 Choose Folder",
            font=("Segoe UI", 9),
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.choose_output_folder
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Naming options
        naming_frame = tk.Frame(output_frame)
        naming_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(naming_frame, text="File Naming:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        self.naming_var = tk.StringVar(value="suffix")
        
        tk.Radiobutton(
            naming_frame,
            text="Add '_flattened' suffix",
            variable=self.naming_var,
            value="suffix",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(20, 10))
        
        tk.Radiobutton(
            naming_frame,
            text="Overwrite original",
            variable=self.naming_var,
            value="overwrite",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT)
    
    def setup_processing_controls(self, parent):
        """Setup processing controls."""
        control_frame = tk.LabelFrame(parent, text="⚙️ Processing", font=("Segoe UI", 12, "bold"))
        control_frame.pack(fill=tk.X, pady=(0, 10), padx=20)
        
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_btn = tk.Button(
            btn_frame,
            text="🔧 Flatten PDFs",
            font=("Segoe UI", 12, "bold"),
            bg="#e67e22",
            fg="white",
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.process_files
        )
        self.process_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(btn_frame, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 0))
    
    def setup_results_area(self, parent):
        """Setup results display area."""
        results_frame = tk.LabelFrame(parent, text="📋 Processing Results", font=("Segoe UI", 12, "bold"))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Text area with scrollbar
        text_frame = tk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(text_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.results_text = tk.Text(
            text_frame,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            font=("Consolas", 9),
            wrap=tk.NONE,
            state=tk.DISABLED
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=self.results_text.yview)
        scrollbar_x.config(command=self.results_text.xview)
    
    def add_files(self):
        """Add PDF files to the processing list."""
        files = filedialog.askopenfilenames(
            title="Select PDF Files to Flatten",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        for file_path in files:
            path = Path(file_path)
            if path not in self.input_files:
                self.input_files.append(path)
        
        self.update_file_list()
    
    def add_folder(self):
        """Add all PDF files from a folder."""
        folder = filedialog.askdirectory(title="Select Folder Containing PDF Files")
        if folder:
            folder_path = Path(folder)
            pdf_files = list(folder_path.glob("*.pdf"))
            
            for pdf_file in pdf_files:
                if pdf_file not in self.input_files:
                    self.input_files.append(pdf_file)
            
            self.update_file_list()
            self.log_message(f"Added {len(pdf_files)} PDF files from {folder}")
    
    def clear_files(self):
        """Clear the file list."""
        self.input_files.clear()
        self.update_file_list()
        self.log_message("File list cleared")
    
    def update_file_list(self):
        """Update the file listbox."""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.input_files:
            self.file_listbox.insert(tk.END, str(file_path))
    
    def choose_output_folder(self):
        """Choose output folder."""
        folder = filedialog.askdirectory(title="Choose Output Folder")
        if folder:
            self.output_folder = Path(folder)
            self.output_folder_var.set(str(self.output_folder))
        else:
            self.output_folder = None
            self.output_folder_var.set("Same as input files")
    
    def process_files(self):
        """Process all selected files."""
        if not self.input_files:
            messagebox.showwarning("No Files", "Please add some PDF files to process.")
            return
        
        self.process_btn.config(state=tk.DISABLED)
        self.clear_results()
        
        total_files = len(self.input_files)
        self.progress.config(maximum=total_files)
        
        success_count = 0
        error_count = 0
        
        self.log_message(f"🔧 Starting PDF flattening process...")
        self.log_message(f"📊 Processing {total_files} files")
        self.log_message("=" * 60)
        
        for i, input_file in enumerate(self.input_files):
            try:
                self.log_message(f"\n📄 Processing: {input_file.name}")
                
                # Determine output path
                if self.output_folder:
                    output_dir = self.output_folder
                else:
                    output_dir = input_file.parent
                
                if self.naming_var.get() == "overwrite":
                    output_path = output_dir / input_file.name
                else:
                    # Add suffix
                    stem = input_file.stem
                    output_path = output_dir / f"{stem}_flattened.pdf"
                
                # Flatten the PDF
                success = self.flatten_pdf(input_file, output_path)
                
                if success:
                    success_count += 1
                    self.log_message(f"✅ Success: {output_path.name}")
                else:
                    error_count += 1
                    self.log_message(f"❌ Failed: {input_file.name}")
                
            except Exception as e:
                error_count += 1
                self.log_message(f"❌ Error processing {input_file.name}: {str(e)}")
            
            # Update progress
            self.progress.config(value=i + 1)
            self.root.update()
        
        # Final summary
        self.log_message("\n" + "=" * 60)
        self.log_message(f"🏁 Processing Complete!")
        self.log_message(f"✅ Successful: {success_count}")
        self.log_message(f"❌ Failed: {error_count}")
        self.log_message(f"📊 Total: {total_files}")
        
        self.process_btn.config(state=tk.NORMAL)
        self.progress.config(value=0)
        
        if success_count > 0:
            messagebox.showinfo("Complete", f"Successfully flattened {success_count} PDF files!")
    
    def flatten_pdf(self, input_path: Path, output_path: Path) -> bool:
        """
        Flatten a PDF by converting form fields to permanent text.
        Properly reads user-edited field values from Adobe Acrobat or online editors.
        Special handling for Right_mid, Right_belowmid, Right_bottom fields to prevent unwanted lines.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open the PDF
            pdf_doc = fitz.open(input_path)
            
            field_count = 0
            processed_count = 0
            skipped_empty_count = 0
            
            # Pre-processing: Ensure PDF is in proper state for reading
            self.log_message(f"   🔄 Pre-processing PDF for field reading...")
            preprocessed_doc = self.preprocess_pdf_for_field_reading(pdf_doc, input_path)
            if preprocessed_doc:
                pdf_doc.close()
                pdf_doc = preprocessed_doc
            
            # First pass: Comprehensive field analysis
            self.log_message(f"   🔍 Analyzing all fields with advanced detection...")
            total_fields_found = 0
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                widgets = list(page.widgets())
                total_fields_found += len(widgets)
                
                for widget in widgets:
                    # Force comprehensive widget update
                    try:
                        widget.update()
                        # Run advanced field analysis but don't modify yet
                        field_name = getattr(widget, 'field_name', f'field_{total_fields_found}')
                        self.log_message(f"   📋 Found field: '{field_name}' at {widget.rect}")
                    except Exception as e:
                        self.log_message(f"   ⚠️ Warning analyzing widget: {str(e)}")
            
            self.log_message(f"   📊 Total fields found: {total_fields_found}")
            
            # Second pass: Process and flatten fields
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                
                # Get all form fields (widgets) on this page
                widgets = list(page.widgets())
                
                for widget in widgets:
                    field_count += 1
                    
                    # Get field properties with enhanced value retrieval
                    field_name = widget.field_name or f"field_{field_count}"
                    field_value = self.get_current_field_value(widget)
                    field_rect = widget.rect
                    
                    # Special handling for problematic fields when empty
                    problematic_fields = ['Right_mid', 'Right_belowmid', 'Right_bottom']
                    is_problematic_field = any(prob_field in field_name for prob_field in problematic_fields)
                    
                    # Only process fields with actual content (skip truly empty fields)
                    if field_value and field_value.strip():  # Ensure we have actual content, not just whitespace
                        processed_count += 1
                        
                        # Get comprehensive font and formatting properties
                        font_props = self.get_field_font_properties(widget)
                        
                        self.log_message(f"   📝 FLATTENING '{field_name}': {len(field_value)} chars")
                        self.log_message(f"       Content preview: {repr(field_value[:100])}{'...' if len(field_value) > 100 else ''}")
                        
                        # Insert text with exact formatting preservation
                        self.insert_formatted_text(
                            page, 
                            field_value, 
                            field_rect, 
                            font_props
                        )
                        
                        self.log_message(f"   ✅ Successfully flattened '{field_name}'")
                    else:
                        skipped_empty_count += 1
                        if is_problematic_field:
                            self.log_message(f"   🚫 SKIPPING empty problematic field '{field_name}' (prevents unwanted lines)")
                        else:
                            self.log_message(f"   ⏭️ SKIPPING empty field '{field_name}' (no content found)")
                
                # Remove all form fields from this page - but handle problematic fields carefully
                for widget in widgets:
                    try:
                        field_name = widget.field_name or "unnamed_field"
                        problematic_fields = ['Right_mid', 'Right_belowmid', 'Right_bottom']
                        is_problematic_field = any(prob_field in field_name for prob_field in problematic_fields)
                        
                        widget.update()  # Ensure widget is current
                        
                        # For problematic fields that are empty, ensure clean removal
                        if is_problematic_field:
                            field_value = self.get_current_field_value(widget)
                            if not field_value or not field_value.strip():
                                # Clear any appearance streams or visual artifacts before deletion
                                self.clean_empty_field_artifacts(widget, page)
                                self.log_message(f"   🧹 Cleaned artifacts from empty field '{field_name}'")
                        
                        page.delete_widget(widget)
                        
                    except Exception as e:
                        self.log_message(f"   ⚠️ Warning deleting widget: {str(e)}")
            
            # Save the flattened PDF
            pdf_doc.save(output_path)
            pdf_doc.close()
            
            self.log_message(f"   🔧 Found {field_count} form fields, flattened {processed_count} with content, skipped {skipped_empty_count} empty fields")
            return True
            
        except Exception as e:
            self.log_message(f"   ❌ Error: {str(e)}")
            return False
    
    def get_current_field_value(self, widget) -> str:
        """
        Advanced field value detection using multiple methods to capture user edits.
        Handles Adobe Acrobat, online editors, and various PDF field storage methods.
        Enhanced to handle problematic fields with template formatting.
        
        Args:
            widget: PyMuPDF widget object
            
        Returns:
            str: Current field value or empty string if truly empty
        """
        field_name = getattr(widget, 'field_name', 'unnamed_field')
        page = widget.parent
        doc = page.parent
        
        self.log_message(f"     🔍 Analyzing field '{field_name}'...")
        
        # Check if this is a problematic field that often has template formatting
        problematic_fields = ['Right_mid', 'Right_belowmid', 'Right_bottom']
        is_problematic_field = any(prob_field in field_name for prob_field in problematic_fields)
        
        # Try multiple methods in order of reliability
        methods_tried = []
        final_value = ""
        
        # Method 1: Direct field value after update
        try:
            widget.update()
            raw_value = widget.field_value
            if raw_value and self.clean_field_value(raw_value):
                final_value = self.clean_field_value(raw_value)
                methods_tried.append(f"✅ Direct: {repr(final_value)}")
            else:
                methods_tried.append(f"❌ Direct: {repr(raw_value)}")
        except Exception as e:
            methods_tried.append(f"❌ Direct: Error - {str(e)}")
        
        # Method 2: Field appearance stream (captures visual content)
        if not final_value:
            appearance_value = self.read_field_appearance(widget, doc)
            if appearance_value:
                final_value = appearance_value
                methods_tried.append(f"✅ Appearance: {repr(final_value)}")
            else:
                methods_tried.append("❌ Appearance: No content")
        
        # Method 3: PDF object direct access with multiple keys
        if not final_value:
            object_value = self.read_field_from_pdf_objects(widget, doc)
            if object_value:
                final_value = object_value
                methods_tried.append(f"✅ PDF Object: {repr(final_value)}")
            else:
                methods_tried.append("❌ PDF Object: No content")
        
        # Method 4: Visual text extraction from field area (with special handling for problematic fields)
        if not final_value:
            visual_value = self.extract_text_from_field_area(page, widget.rect, field_name)
            if visual_value:
                # For problematic fields, be extra strict about template formatting
                if is_problematic_field:
                    import re
                    # If it's all underscores, reject it
                    if re.match(r'^[_\s\n]+$', visual_value):
                        methods_tried.append("❌ Visual Extract: Template formatting detected")
                    else:
                        final_value = visual_value
                        methods_tried.append(f"✅ Visual Extract: {repr(final_value)}")
                else:
                    final_value = visual_value
                    methods_tried.append(f"✅ Visual Extract: {repr(final_value)}")
            else:
                methods_tried.append("❌ Visual Extract: No text found")
        
        # Method 5: Form data extraction (for online editors)
        if not final_value:
            form_value = self.read_form_data_value(widget, doc)
            if form_value:
                final_value = form_value
                methods_tried.append(f"✅ Form Data: {repr(final_value)}")
            else:
                methods_tried.append("❌ Form Data: No content")
        
        # Log all attempts
        for method in methods_tried:
            self.log_message(f"       {method}")
        
        self.log_message(f"     🎯 Final result '{field_name}': {repr(final_value)}")
        return final_value
    
    def clean_field_value(self, raw_value) -> str:
        """
        Clean and validate field value, filtering out null/empty indicators.
        Enhanced to be more strict about empty content detection.
        
        Args:
            raw_value: Raw value from PDF field
            
        Returns:
            str: Cleaned value or empty string
        """
        # Handle None or empty values
        if raw_value is None:
            return ""
        
        # Convert to string if needed
        if not isinstance(raw_value, str):
            try:
                raw_value = str(raw_value)
            except:
                return ""
        
        # Filter out null/undefined indicators (case insensitive)
        null_indicators = [
            'null', 'undefined', 'none', 'nil', 'empty', 
            '(null)', '(undefined)', '(none)', '(empty)',
            'null\x00', '\x00null', 'null ', ' null',
            'n/a', 'na', 'not applicable', 'not available',
            '---', '--', '-', '___', '__', '_',
            '...', '..', '.', '   ', '  ', ' '
        ]
        
        # Check if the value is a null indicator
        value_lower = raw_value.lower().strip()
        if value_lower in null_indicators:
            return ""
        
        # Remove null bytes and control characters
        cleaned = raw_value.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove common placeholder characters
        cleaned = cleaned.replace('\u00A0', ' ')  # Non-breaking space
        cleaned = cleaned.replace('\u2000', ' ')  # En quad
        cleaned = cleaned.replace('\u2001', ' ')  # Em quad
        cleaned = cleaned.replace('\u2002', ' ')  # En space
        cleaned = cleaned.replace('\u2003', ' ')  # Em space
        
        # If after cleaning we only have whitespace, return empty
        if not cleaned.strip():
            return ""
        
        # Additional check: if it's only punctuation or special characters, consider it empty
        import re
        if re.match(r'^[\s\-_\.]+$', cleaned):
            return ""
        
        # Check for template line patterns (underscores forming lines)
        if re.match(r'^[_\s\n]+$', cleaned):
            return ""
        
        # Check for repeated underscore patterns that indicate template lines
        lines = cleaned.split('\n')
        non_underscore_lines = []
        for line in lines:
            line_stripped = line.strip()
            # If line is mostly underscores (template formatting), skip it
            if line_stripped and not re.match(r'^_{10,}$', line_stripped):
                non_underscore_lines.append(line)
        
        # If all lines were underscore patterns, consider it empty
        if not non_underscore_lines:
            return ""
        
        # If we have actual content mixed with underscores, keep the real content
        if len(non_underscore_lines) < len(lines):
            cleaned = '\n'.join(non_underscore_lines)
        
        return cleaned.strip()
    
    def read_field_appearance(self, widget, doc) -> str:
        """
        Read field content from appearance streams (captures visual representation).
        This is crucial for Adobe Acrobat and online editor compatibility.
        """
        try:
            if not hasattr(widget, 'xref') or not widget.xref:
                return ""
            
            # Try to get appearance stream
            ap_obj = doc.xref_get_key(widget.xref, "AP")
            if ap_obj and len(ap_obj) > 1 and ap_obj[1]:
                # Parse appearance stream for text content
                ap_content = ap_obj[1]
                
                # Look for text content in appearance stream
                if "BT" in ap_content and "ET" in ap_content:  # Text object markers
                    # Extract text between BT (Begin Text) and ET (End Text)
                    import re
                    text_matches = re.findall(r'BT.*?\((.*?)\).*?ET', ap_content, re.DOTALL)
                    if text_matches:
                        # Clean and return the first text match
                        text = text_matches[0].strip()
                        if text and text not in ['null', 'undefined', '']:
                            return text
                
                # Alternative: look for Tj operators (show text)
                tj_matches = re.findall(r'\((.*?)\)\s*Tj', ap_content)
                if tj_matches:
                    combined_text = ' '.join(tj_matches).strip()
                    if combined_text and combined_text not in ['null', 'undefined', '']:
                        return combined_text
            
            return ""
            
        except Exception as e:
            return ""
    
    def read_field_from_pdf_objects(self, widget, doc) -> str:
        """
        Read field value using direct PDF object access with multiple keys.
        """
        try:
            if not hasattr(widget, 'xref') or not widget.xref:
                return ""
            
            # Try different PDF field value keys
            value_keys = ['V', 'DV', 'RV']  # Value, Default Value, Rich Text Value
            
            for key in value_keys:
                try:
                    obj = doc.xref_get_key(widget.xref, key)
                    if obj and len(obj) > 1 and obj[1]:
                        value_str = obj[1].strip()
                        
                        # Handle different string formats
                        if value_str.startswith('(') and value_str.endswith(')'):
                            # PDF string literal
                            content = value_str[1:-1]
                        elif value_str.startswith('<') and value_str.endswith('>'):
                            # Hex string - convert to text
                            try:
                                hex_content = value_str[1:-1]
                                content = bytes.fromhex(hex_content).decode('utf-8', errors='ignore')
                            except:
                                content = value_str
                        else:
                            content = value_str
                        
                        if content and content.strip() and content.lower() not in ['null', 'undefined']:
                            return content.strip()
                except:
                    continue
            
            return ""
            
        except Exception as e:
            return ""
    
    def extract_text_from_field_area(self, page, field_rect, field_name) -> str:
        """
        Extract text directly from the field's visual area.
        This captures what's actually rendered, regardless of field properties.
        """
        try:
            # Extract all text from the page
            text_dict = page.get_text("dict")
            
            # Find text that overlaps with the field rectangle
            field_texts = []
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        line_rect = fitz.Rect(line["bbox"])
                        
                        # Check if line intersects with field rectangle
                        if field_rect.intersects(line_rect):
                            line_text = ""
                            for span in line.get("spans", []):
                                span_rect = fitz.Rect(span["bbox"])
                                # More precise intersection check
                                if field_rect.intersects(span_rect):
                                    text = span.get("text", "").strip()
                                    if text:
                                        line_text += text + " "
                            
                            if line_text.strip():
                                field_texts.append(line_text.strip())
            
            # Combine all text found in the field area
            if field_texts:
                combined_text = "\n".join(field_texts).strip()
                
                # Filter out common non-content text
                if combined_text and combined_text.lower() not in ['null', 'undefined', 'none', '']:
                    # Additional filtering for template formatting
                    import re
                    
                    # Check if it's all underscores (template lines)
                    if re.match(r'^[_\s\n]+$', combined_text):
                        return ""
                    
                    # Filter out lines that are just underscores
                    lines = combined_text.split('\n')
                    content_lines = []
                    for line in lines:
                        line_stripped = line.strip()
                        # Skip lines that are just underscores (10 or more consecutive underscores)
                        if not re.match(r'^_{10,}$', line_stripped):
                            content_lines.append(line)
                    
                    # If we have actual content after filtering
                    if content_lines and any(line.strip() for line in content_lines):
                        filtered_text = '\n'.join(content_lines).strip()
                        # Make sure it's not just whitespace after filtering
                        if filtered_text:
                            return filtered_text
            
            return ""
            
        except Exception as e:
            return ""
    
    def read_form_data_value(self, widget, doc) -> str:
        """
        Read form data using alternative methods (for online editors).
        """
        try:
            # Try to access form field data through document form
            if hasattr(doc, 'get_form_field_value'):
                try:
                    value = doc.get_form_field_value(widget.field_name)
                    if value and str(value).strip() and str(value).lower() not in ['null', 'undefined']:
                        return str(value).strip()
                except:
                    pass
            
            # Try alternative widget properties
            alt_properties = ['text_value', 'choice_values', 'field_display_value']
            for prop in alt_properties:
                if hasattr(widget, prop):
                    try:
                        value = getattr(widget, prop)
                        if value and str(value).strip() and str(value).lower() not in ['null', 'undefined']:
                            return str(value).strip()
                    except:
                        continue
            
            return ""
            
        except Exception as e:
            return ""
    
    def clean_empty_field_artifacts(self, widget, page):
        """
        Clean any visual artifacts from empty fields before deletion.
        This prevents unwanted lines or borders from appearing in flattened PDFs.
        
        Args:
            widget: The widget to clean
            page: The page containing the widget
        """
        try:
            field_name = getattr(widget, 'field_name', 'unnamed_field')
            
            # Clear appearance streams that might contain visual artifacts
            if hasattr(widget, 'xref') and widget.xref:
                doc = page.parent
                
                # Remove appearance streams (AP entry)
                try:
                    doc.xref_set_key(widget.xref, "AP", "null")
                except:
                    pass
                
                # Clear any border or background that might create lines
                try:
                    # Remove border style
                    doc.xref_set_key(widget.xref, "BS", "null")
                    # Remove border
                    doc.xref_set_key(widget.xref, "Border", "null")
                    # Remove background color
                    doc.xref_set_key(widget.xref, "BG", "null")
                    # Remove any highlight mode
                    doc.xref_set_key(widget.xref, "H", "null")
                except:
                    pass
                
                # Ensure field value is truly empty
                try:
                    doc.xref_set_key(widget.xref, "V", "null")
                    doc.xref_set_key(widget.xref, "DV", "null")
                except:
                    pass
            
            # Clear widget properties that might cause visual artifacts
            try:
                widget.field_value = ""
                widget.update()
            except:
                pass
                
        except Exception as e:
            self.log_message(f"     ⚠️ Warning cleaning field artifacts: {str(e)}")
    
    def preprocess_pdf_for_field_reading(self, pdf_doc, input_path):
        """
        Pre-process PDF to ensure field values are properly accessible.
        This handles Adobe Acrobat saves and online editor compatibility.
        """
        try:
            # Check if PDF needs special handling
            needs_preprocessing = False
            
            # Test a sample field to see if we can read values properly
            sample_field_found = False
            for page_num in range(min(len(pdf_doc), 3)):  # Check first 3 pages
                page = pdf_doc[page_num]
                widgets = list(page.widgets())
                if widgets:
                    sample_field_found = True
                    widget = widgets[0]
                    try:
                        widget.update()
                        value = widget.field_value
                        # If we can't read the field value, we need preprocessing
                        if value is None:
                            needs_preprocessing = True
                            break
                    except:
                        needs_preprocessing = True
                        break
            
            if not sample_field_found:
                self.log_message(f"   ℹ️ No form fields found in PDF")
                return None
            
            if needs_preprocessing:
                self.log_message(f"   🔧 PDF needs preprocessing - creating temporary copy...")
                
                # Create a temporary processed copy
                import tempfile
                temp_path = tempfile.mktemp(suffix='.pdf')
                
                # Save and reload to commit any pending changes
                pdf_doc.save(temp_path, incremental=False, encryption=fitz.PDF_ENCRYPT_NONE)
                
                # Reopen the processed PDF
                new_doc = fitz.open(temp_path)
                
                # Clean up temp file
                try:
                    import os
                    os.unlink(temp_path)
                except:
                    pass
                
                self.log_message(f"   ✅ PDF preprocessing complete")
                return new_doc
            else:
                self.log_message(f"   ✅ PDF is ready for field reading")
                return None
                
        except Exception as e:
            self.log_message(f"   ⚠️ PDF preprocessing error: {str(e)}")
            return None
    
    def get_field_font_properties(self, widget) -> dict:
        """
        Get comprehensive field font and formatting properties.
        
        Args:
            widget: PyMuPDF widget object
            
        Returns:
            dict: Font properties including size, alignment, and other formatting
        """
        properties = {
            'font_size': 12.0,
            'font_name': 'helv',  # Default PDF font
            'text_color': (0, 0, 0),  # Black
            'alignment': 0,  # Left aligned
            'border_width': 0,
            'background_color': None
        }
        
        field_name = getattr(widget, 'field_name', 'unnamed_field')
        
        try:
            # Get font size
            font_size = None
            
            # Method 1: Direct font size attributes
            for attr in ['text_font_size', 'text_fontsize', 'fontsize']:
                if hasattr(widget, attr):
                    size = getattr(widget, attr)
                    if size and size > 0:
                        font_size = float(size)
                        self.log_message(f"     🔤 Font size from {attr}: {font_size}")
                        break
            
            # Method 2: Parse default appearance string
            if not font_size and hasattr(widget, 'text_da') and widget.text_da:
                try:
                    da_parts = widget.text_da.split()
                    for i, part in enumerate(da_parts):
                        if part == 'Tf' and i > 0:
                            font_size = float(da_parts[i-1])
                            if font_size > 0:
                                self.log_message(f"     🔤 Font size from DA: {font_size}")
                                break
                        # Also try to get font name
                        if part.startswith('/') and i < len(da_parts) - 1:
                            if da_parts[i+1] != 'Tf':
                                properties['font_name'] = part[1:]  # Remove leading /
                except Exception as e:
                    self.log_message(f"     ⚠️ DA parsing error: {str(e)}")
            
            # Method 3: Estimate from field height
            if not font_size:
                try:
                    field_height = widget.rect.height
                    if field_height > 0:
                        # More conservative estimation
                        font_size = min(field_height * 0.6, 24.0)  # Cap at 24pt
                        if font_size < 6:
                            font_size = 10.0  # Minimum readable size
                        self.log_message(f"     🔤 Font size estimated from height: {font_size}")
                except:
                    pass
            
            if font_size:
                properties['font_size'] = font_size
            
            # Get text alignment
            if hasattr(widget, 'text_align'):
                properties['alignment'] = getattr(widget, 'text_align', 0)
            
            # Get colors if available
            if hasattr(widget, 'text_color'):
                properties['text_color'] = getattr(widget, 'text_color', (0, 0, 0))
            
            self.log_message(f"     🎨 Field '{field_name}' properties: {properties}")
            
        except Exception as e:
            self.log_message(f"     ❌ Error getting font properties: {str(e)}")
        
        return properties
    
    def insert_formatted_text(self, page, text: str, rect: fitz.Rect, font_props: dict):
        """
        Insert text with exact formatting preservation matching the original field.
        Handles alignment, font properties, and preserves user-edited formatting.
        
        Args:
            page: PDF page object
            text: Text to insert (already cleaned of null values)
            rect: Rectangle of the original field
            font_props: Font and formatting properties dictionary
        """
        try:
            font_size = font_props.get('font_size', 12.0)
            text_color = font_props.get('text_color', (0, 0, 0))
            alignment = font_props.get('alignment', 0)  # 0=left, 1=center, 2=right
            
            # Calculate dimensions with minimal padding to match original exactly
            padding = 2  # Minimal padding to match PDF field rendering
            available_width = rect.width - (padding * 2)
            line_height = font_size * 1.2  # Standard PDF line height
            
            # Preserve original text formatting exactly
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            
            # Handle different text alignment
            def get_x_position(line_text, line_width):
                if alignment == 1:  # Center
                    return rect.x0 + (rect.width - line_width) / 2
                elif alignment == 2:  # Right
                    return rect.x1 - line_width - padding
                else:  # Left (default)
                    return rect.x0 + padding
            
            # Split into lines preserving original line breaks
            lines = text.split('\n')
            current_y = rect.y0 + font_size + padding  # Start position
            
            for line_idx, line in enumerate(lines):
                # Handle empty lines
                if not line:
                    current_y += line_height * 0.8
                    continue
                
                # Word wrap if line is too long
                words = line.split(' ')
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    
                    # Measure text width accurately
                    try:
                        text_width = fitz.get_text_length(test_line, fontsize=font_size)
                    except:
                        # Fallback calculation
                        text_width = len(test_line) * font_size * 0.6
                    
                    if text_width <= available_width or not current_line:
                        current_line = test_line
                    else:
                        # Insert current line before adding new word
                        if current_line:
                            try:
                                line_width = fitz.get_text_length(current_line, fontsize=font_size)
                            except:
                                line_width = len(current_line) * font_size * 0.6
                            
                            x_pos = get_x_position(current_line, line_width)
                            
                            page.insert_text(
                                fitz.Point(x_pos, current_y),
                                current_line,
                                fontsize=font_size,
                                color=text_color
                            )
                            current_y += line_height
                        
                        current_line = word
                        
                        # Check vertical space
                        if current_y > rect.y1 - font_size:
                            self.log_message(f"     ⚠️ Text truncated - insufficient vertical space")
                            return
                
                # Insert the final line
                if current_line:
                    try:
                        line_width = fitz.get_text_length(current_line, fontsize=font_size)
                    except:
                        line_width = len(current_line) * font_size * 0.6
                    
                    x_pos = get_x_position(current_line, line_width)
                    
                    page.insert_text(
                        fitz.Point(x_pos, current_y),
                        current_line,
                        fontsize=font_size,
                        color=text_color
                    )
                    current_y += line_height
                
                # Check if we're running out of space
                if current_y > rect.y1 - font_size:
                    if line_idx < len(lines) - 1:
                        self.log_message(f"     ⚠️ Remaining text truncated - field height insufficient")
                    break
                    
        except Exception as e:
            self.log_message(f"     ❌ Text insertion error: {str(e)}")
            # Simple fallback - insert text at top-left of field
            try:
                fallback_text = text.replace('\n', ' ')[:200]  # Limit length
                page.insert_text(
                    fitz.Point(rect.x0 + 2, rect.y0 + font_props.get('font_size', 12) + 2),
                    fallback_text,
                    fontsize=font_props.get('font_size', 12),
                    color=font_props.get('text_color', (0, 0, 0))
                )
            except Exception as fallback_error:
                self.log_message(f"     ❌ Fallback insertion failed: {str(fallback_error)}")
                pass
    
    def log_message(self, message: str):
        """Add a message to the results area."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.root.update()
    
    def clear_results(self):
        """Clear the results area."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Main entry point."""
    app = PDFFlatteningTool()
    app.run()

if __name__ == "__main__":
    main()
