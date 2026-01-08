# Backend - Automation Systems

This directory contains the core automation logic from three separate Python automation systems that will be integrated into the unified web platform.

## Directory Structure

```
backend/
├── post_review/          # Post Review Document Processor
├── a3_automation/        # A3 Handwriting Processor
├── value_creator/        # Value Creator Letter Automation
└── README.md            # This file
```

---

## 1. Post Review Automation (`post_review/`)

**Purpose:** Process handwritten annotations on PDF documents and apply changes to Word documents using GPT-4o Vision.

### Files Copied:
- **requirements.txt** - Python dependencies
- **config/** - Section configurations with PDF coordinates
  - `page1n2n3n4_sections_config.json` - Original section config
  - `post_review_sections_part2.json` - Updated section definitions (18+ sections)
- **src/core/** - Core processing engine
  - `master_unified_processor.py` - Main orchestrator
  - `unified_section_implementations.py` - 18+ section-specific Word implementations
  - `pdf_section_splitter.py` - PDF section extraction
  - `post_review_config_adapter.py` - Configuration management
  - `unified_post_review_processor.py` - Unified processing wrapper
- **src/sections/** - Individual section test files (18 files)
  - Each section has its own processor (test_section_1_1.py through test_section_4_6.py)
- **src/utils/** - Utility functions
  - `section_implementations_reference.py` - Reference implementations
  - `word_implementation_framework.py` - Word manipulation framework
  - `cleanup_test_folders.py` - Cleanup utilities

### Key Features:
- 18+ configurable document sections
- GPT-4o Vision OCR for handwriting recognition
- 3-strategy text matching (exact → similarity → keyword)
- Section-based processing with coordinate definitions
- Comprehensive change tracking

### Technology:
- Python 3.11+
- python-docx (Word manipulation)
- PyMuPDF (PDF processing)
- GPT-4o Vision API
- JSON-based section configurations

---

## 2. A3 Handwriting Automation (`a3_automation/`)

**Purpose:** Extract handwritten data from A3 financial planning forms and populate PDF templates.

### Files Copied:
- **requirements.txt** - Python dependencies
- **a3_sectioned_automation.py** - Main automation orchestrator
- **sectioned_gpt4o_ocr.py** - GPT-4o Vision OCR engine (21 sections)
- **a3_template_processor.py** - PDF template field management
- **ocr_spell_checker.py** - Spell checking integration
- **A3_templates/** - Template configurations
  - `a3_section_config.json` - 21 predefined sections (2 pages)
  - `custom_field_position.json` - Custom field positioning
  - `More4Life A3 Goals - blank.pdf` - Blank template
  - `More4Life Personal Goals - July 2025.pdf` - Sample filled form

### Key Features:
- 21 predefined sections (Page 1: 6 sections, Page 2: 15 sections)
- Section-based OCR with GPT-4o Vision
- PDF form field population
- Custom field positioning via JSON
- Spell checking integration
- Template regeneration from JSON config

### Section Layout:
**Page 1:**
- Section_1_1: Dangers to be eliminated
- Section_1_2: Opportunities to be focused on
- Section_1_3: Strengths to be reinforced
- Sections_1_4-1_6: Right-side content areas

**Page 2:**
- 5-column goal grid (Money, Business, Leisure, Health, Family)
- Each column has: Goals, Now, Todo (15 total sections)

### Technology:
- Python 3.11+
- PyMuPDF (PDF form fields)
- GPT-4o Vision API
- JSON section coordinates
- Pillow (image processing)

---

## 3. Value Creator Letter Automation (`value_creator/`)

**Purpose:** Parse financial documents, detect changes/strikethroughs, and generate updated Word documents.

### Files Copied:
- **requirements.txt** - Python dependencies
- **src/production_orchestrator.py** - Master orchestration logic
- **src/core/** - Core processing
  - `document_parser.py` - PDF parsing and chunking
  - `chunk_analyzer.py` - GPT-4o Vision analysis per chunk
  - `document_preprocessor.py` - PDF preprocessing
- **src/processors/** - Document processors
  - `unified_section_processor.py` - 10-chunk processing with 3-strategy system
  - `word_processor.py` - Word document generation
  - `advanced_word_processor.py` - Advanced Word operations
  - `processor_helpers.py` - Helper functions
- **data/templates/** - Configuration and templates
  - `config.yaml` - Main configuration
  - `chunk_template.json` - Chunk coordinate definitions

### Key Features:
- 10-chunk template-based processing
- GPT-4o Vision analysis per chunk
- 3-strategy cascading (exact → similarity 0.6 → keyword)
- Strikethrough detection (conservative mode)
- Date replacement (XXXX → handwritten date)
- Amount and date detection
- Business plan row analysis
- Comprehensive debug JSON output

### Chunk Layout:
- **Chunk 1:** Date replacement
- **Chunks 2-3:** Bullet points (concerns/opportunities)
- **Chunk 4:** Context-aware routing (opportunities vs strengths)
- **Chunk 5:** Portfolio selection
- **Chunks 6-9:** Business plan analysis
- **Chunk 8:** Strikethrough detection

### Technology:
- Python 3.11+
- Poppler (PDF to image conversion)
- GPT-4o Vision API
- python-docx (Word generation)
- PyYAML (configuration)
- OpenCV (image processing)

---

## Common Dependencies Across All Systems

### Core Libraries:
- **openai** (>=1.0.0) - GPT-4o Vision API
- **python-docx** (>=0.8.11) - Word document manipulation
- **Pillow** (>=9.0.0) - Image processing
- **PyMuPDF** (>=1.23.0) - PDF processing
- **requests** (>=2.28.0) - HTTP requests
- **python-dotenv** (>=0.19.0) - Environment variables

### UI Libraries (Original - Not Needed for Web):
- tkinter (built-in)
- tkinterdnd2 (drag & drop)

---

## Integration Notes

### API Endpoints to Create:
Each automation will need FastAPI wrappers:

1. **POST /api/post-review/upload** - Upload Word + PDF
2. **POST /api/post-review/process** - Start processing
3. **GET /api/post-review/status/{job_id}** - Check status
4. **GET /api/post-review/result/{job_id}** - Download result

5. **POST /api/a3/upload** - Upload A3 form
6. **POST /api/a3/process** - Process with template
7. **GET /api/a3/templates** - List available templates
8. **POST /api/a3/create-template** - Create custom template

9. **POST /api/value-creator/upload** - Upload PDF
10. **POST /api/value-creator/process** - Process document
11. **GET /api/value-creator/status/{job_id}** - Check status

### Environment Variables Required:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Next Steps:
1. Create FastAPI wrapper files (`api.py`) for each system
2. Implement async job processing (Celery + Redis)
3. Add file upload handling (multipart/form-data)
4. Implement progress tracking (WebSocket or polling)
5. Add error handling and logging
6. Create unified backend requirements.txt
7. Set up Docker containers for each service

---

## File Count Summary

- **Post Review:** 45+ files (core logic, 18 section processors, configs)
- **A3 Automation:** 5 Python files + 4 template files
- **Value Creator:** 9 Python files + 2 config files

**Total:** 60+ essential working files copied and preserved

---

## Status: ✅ Files Successfully Copied

All essential working files from the three automation systems have been copied to this backend directory. The original file structure and working code have been preserved.

**Next:** Create FastAPI wrappers to expose these automation systems as REST APIs.
