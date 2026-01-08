# Automation Hub Implementation Plan
## Unified Web Platform for More4Life Automations

---

## Executive Summary

This document outlines the implementation plan for creating a unified web platform that consolidates three existing Python automation tools into a single Next.js/TypeScript web application. The platform will integrate:

1. **Post Review Automation** - Document annotation processing
2. **A3 Handwriting Automation** - Handwritten form processing  
3. **Value Creator Letter Automation** - Financial document generation

The frontend is built using the More4Life brand identity with a clean, modern design system featuring a collapsible sidebar, dashboard stats, and modular tool cards. The backend Python automation logic remains unchanged, exposed via FastAPI endpoints.

---

## Current State Analysis

### 1. Post Review Automation
**Location:** `C:\Users\dodso\post_review\`  
**Entry Point:** `C:\Users\dodso\post_review\src\ui\post_review_modern_ui.py`

**Purpose:**  
Process handwritten annotations on PDF documents and apply changes to Word documents using M4L VL Model vision analysis.

**Key Features:**
- Drag & drop document upload (PDF + Word)
- OCR processing with M4L VL Model
- Change detection and tracking
- Document comparison
- Backup creation
- Preview functionality
- Logging and error handling

**Architecture:**
```
src/
├── core/           # Core processing logic
├── sections/       # Section-based processing
├── ui/            # Tkinter GUI (to be replaced)
└── utils/         # Utility functions
```

**Tech Stack:**
- Python 3.x
- tkinter + tkinterdnd2 (GUI - to be replaced by web UI)
- M4L VL Model API (OpenAI GPT-4o Vision)
- python-docx (Word processing)
- PyPDF2/pdf2image

**Color Scheme:**
- Primary: `#667eea` (purple gradient)
- Background: `#ffffff`
- Accent: Various status colors

---

### 2. A3 Handwriting Automation  
**Location:** `C:\Users\dodso\A3_handtotext\`  
**Entry Point:** `C:\Users\dodso\A3_handtotext\a3_sectioned_automation.py`

**Purpose:**  
Process handwritten A3 financial planning forms, extract data via OCR, and populate PDF templates with recognized data.

**Key Features:**
- Section-based OCR processing
- Template management (custom field positioning)
- Spell checking integration
- Batch processing support
- Visual section debugging
- Template creation tools
- Field positioning tool

**Architecture:**
```
├── a3_sectioned_automation.py      # Main automation
├── a3_template_processor.py        # Template handling
├── sectioned_gpt4o_ocr.py         # OCR engine
├── A3_templates/                  # Template configurations
├── processed_documents/           # Output folder
└── section_images/                # Debug images
```

**Tech Stack:**
- Python 3.x
- tkinter + tkinterdnd2 (GUI - to be replaced by web UI)
- M4L VL Model API (OpenAI GPT-4o Vision)
- PyPDF2 (PDF manipulation)
- Custom template system

**Key Workflow:**
1. Upload handwritten A3 form (PDF/image)
2. Define/load section configuration
3. Extract sections with OCR
4. Validate and spell-check
5. Populate PDF template
6. Export final document

---

### 3. Value Creator Letter Automation  
**Location:** `C:\Users\dodso\value_creator_sfml\`  
**Entry Point:** `C:\Users\dodso\value_creator_sfml\value_creator_letter_app.py`

**Purpose:**  
Parse financial documents, detect strikethroughs and changes, and generate updated Word documents with detected modifications.

**Key Features:**
- PDF to image conversion (Poppler)
- Strikethrough detection
- Amount/date detection
- Section-based chunking
- Word document generation
- Business plan row detection
- Conservative processing mode

**Architecture:**
```
src/
├── core/              # Core orchestration
├── gui/              # Tkinter GUI (to be replaced)
└── processors/       # Document processors
```

**Tech Stack:**
- Python 3.x
- tkinter (GUI)
- Poppler (PDF processing)
- python-docx (Word generation)
- Custom detection algorithms

**Color Scheme (from Tkinter UI):**
- Primary Blue: `#1e3a8a`
- Orange: `#f97316`
- Slate grays: `#f8fafc` to `#1e293b`
- Green: `#16a34a`
- Rounded corners: 20px

---

## Target State: More4Life Theme

### Design System

**Framework:** Next.js 14 with App Router  
**Language:** TypeScript  
**Styling:** Tailwind CSS v3  
**Icons:** lucide-react

**Color Palette (More4Life Branding):**

#### Primary Colors
- **M4L Orange:** `#e67e22` - Primary brand color, used for CTAs and highlights
- **M4L Blue:** `#00426b` - Secondary brand color, used for headings and important text
- **Background:** `#f9fafb` (gray-50) - Neutral light background
- **Foreground:** `#171717` - Dark text

#### Component Colors
- **White:** `#ffffff` - Cards, sidebar, header backgrounds
- **Gray Scale:** Tailwind's default grays (50-900)
- **Status Colors:**
  - Success: `green-600` / `green-100`
  - Warning: `yellow-600` / `yellow-100`
  - Error: `red-600` / `red-100`
  - Info: `blue-600` / `blue-100`

**Typography:**
- Sans: Inter (Google Fonts)
- Weights: 300, 400, 500, 600, 700

**Layout:**
- Sidebar width: `280px` (expanded) / `80px` (collapsed)
- Collapsible sidebar with smooth transitions
- Fixed header with shadow
- Content padding: `2rem` (8 on Tailwind scale)

**Border Radius:**
- Cards: `rounded-xl` (12px)
- Buttons: `rounded-lg` (8px)
- Icons: `rounded-full` or `rounded-lg`

**Key Components:**
- **Sidebar:** Collapsible navigation with More4Life branding
- **DashboardStats:** Three stat cards with icons and metrics
- **ToolCard:** Reusable cards for automation tools with hover effects
- **RecentActivity:** Activity feed showing job status
- **Header:** Fixed header with notifications and help icons

---

## Implementation Plan

### Phase 1: Project Setup & Architecture (Week 1)

#### 1.1 Repository Structure
```
m4l_website/
├── frontend/                    # ✅ COMPLETED: Next.js frontend
│   ├── app/
│   │   ├── page.tsx            # ✅ Main dashboard
│   │   ├── layout.tsx          # ✅ Root layout with Sidebar
│   │   ├── globals.css         # ✅ Tailwind + Inter font
│   │   ├── post-review/        # TODO: Post Review page
│   │   ├── a3-automation/      # TODO: A3 automation page
│   │   └── value-creator/      # TODO: Value Creator page
│   ├── components/             # ✅ COMPLETED: Core components
│   │   ├── Sidebar.tsx         # ✅ Collapsible navigation
│   │   ├── DashboardStats.tsx  # ✅ Stats cards
│   │   ├── ToolCard.tsx        # ✅ Reusable tool cards
│   │   └── RecentActivity.tsx  # ✅ Activity feed
│   ├── tailwind.config.ts      # ✅ M4L colors configured
│   └── package.json            # ✅ Next 14, lucide-react
├── backend/                    # ✅ COMPLETED: Python backends
│   ├── post_review/            # ✅ 32 files migrated
│   ├── a3_automation/          # ✅ 9 files migrated
│   ├── value_creator/          # ✅ 15 files migrated
│   └── README.md               # ✅ Documentation
└── IMPLEMENTATION_PLAN.md      # This file
```

#### 1.2 Backend API Wrappers

Create FastAPI wrappers for each automation tool:

**Post Review API (`backend/post_review/api.py`):**
```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Import existing logic
sys.path.insert(0, str(Path(__file__).parent / "src"))
from src.core.post_review_processor import PostReviewProcessor

app = FastAPI(title="Post Review API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/post-review/upload")
async def upload_documents(
    original_doc: UploadFile = File(...),
    annotated_pdf: UploadFile = File(...)
):
    # Existing logic wrapped in API endpoint
    pass

@app.post("/api/post-review/process")
async def process_document(job_id: str):
    # Call existing processor
    pass

@app.get("/api/post-review/status/{job_id}")
async def get_status(job_id: str):
    # Return processing status
    pass

@app.get("/api/post-review/result/{job_id}")
async def get_result(job_id: str):
    # Return processed document
    pass
```

**A3 Processor API (`backend/a3_automation/api.py`):**
```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from a3_sectioned_automation import A3SectionedProcessor

app = FastAPI(title="A3 Processor API")

# Similar structure to Post Review API

@app.post("/api/a3/upload")
async def upload_a3_form(form_image: UploadFile = File(...)):
    pass

@app.post("/api/a3/process")
async def process_a3_form(job_id: str, template_id: str):
    pass

@app.get("/api/a3/templates")
async def list_templates():
    pass

@app.post("/api/a3/create-template")
async def create_template(config: dict):
    pass
```

**Value Creator API (`backend/value_creator/api.py`):**
```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from src.production_orchestrator import ProductionDocumentOrchestrator

app = FastAPI(title="Value Creator API")

# Similar structure

@app.post("/api/value-creator/upload")
async def upload_document(pdf_file: UploadFile = File(...)):
    pass

@app.post("/api/value-creator/process")
async def process_value_creator(job_id: str, options: dict):
    pass
```

#### 1.3 Environment Configuration

Update `.env.local`:
```env
# Existing
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=BackPro X SFML (Dev)

# New - Automation APIs
NEXT_PUBLIC_POST_REVIEW_API=http://localhost:8001
NEXT_PUBLIC_A3_API=http://localhost:8002
NEXT_PUBLIC_VALUE_CREATOR_API=http://localhost:8003

# Python Backend Settings
OPENAI_API_KEY=your_key_here
```

#### 1.4 Package Dependencies

Update `package.json`:
```json
{
  "dependencies": {
    // Existing dependencies...
    
    // New - for automation features
    "react-dropzone": "^14.2.3",
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0",  // For real-time updates
    "zustand": "^4.5.0"             // State management for jobs
  }
}
```

Create `backend/requirements.txt`:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
python-docx==1.1.0
PyPDF2==3.0.1
pdf2image==1.17.0
Pillow==10.2.0
openai==1.12.0
python-dotenv==1.0.0
aiofiles==23.2.1
celery==5.3.6           # For background tasks
redis==5.0.1            # Task queue
```

---

### Phase 2: Core Infrastructure (Week 2)

#### 2.1 Shared TypeScript Types

**`types/automations.ts`:**
```typescript
export interface AutomationTool {
  id: string;
  name: string;
  description: string;
  icon: string;
  route: string;
  color: string;
  status: 'active' | 'beta' | 'coming-soon';
  features: string[];
  estimatedTime: string;
}

export interface ProcessingJob {
  id: string;
  toolId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  createdAt: Date;
  completedAt?: Date;
  files: JobFile[];
  result?: JobResult;
  error?: string;
}

export interface JobFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
}

export interface JobResult {
  outputFiles: string[];
  summary: string;
  metadata: Record<string, any>;
}

// Tool-specific types
export interface PostReviewOptions {
  enableOcr: boolean;
  createBackup: boolean;
  preserveFormatting: boolean;
  showPreview: boolean;
}

export interface A3ProcessorOptions {
  templateId: string;
  enableSpellCheck: boolean;
  customFieldPositions?: boolean;
}

export interface ValueCreatorOptions {
  detectStrikethrough: boolean;
  detectAmounts: boolean;
  detectDates: boolean;
  conservativeMode: boolean;
}
```

#### 2.2 Shared Components

**`components/automations/AutomationCard.tsx`:**
```typescript
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowRight, Clock, CheckCircle } from "lucide-react";
import Link from "next/link";
import type { AutomationTool } from "@/types/automations";

interface AutomationCardProps {
  tool: AutomationTool;
}

export function AutomationCard({ tool }: AutomationCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'beta': return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'coming-soon': return 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200';
      default: return '';
    }
  };

  return (
    <Card className="group hover:shadow-lg transition-all duration-300 border-2 hover:border-primary">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className={`p-3 rounded-lg ${tool.color} mb-4`}>
            <div className="text-3xl">{tool.icon}</div>
          </div>
          <Badge className={getStatusColor(tool.status)} variant="secondary">
            {tool.status.replace('-', ' ')}
          </Badge>
        </div>
        <CardTitle className="text-xl">{tool.name}</CardTitle>
        <CardDescription className="text-base">{tool.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">Key Features:</p>
            <ul className="space-y-1">
              {tool.features.slice(0, 3).map((feature, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>{tool.estimatedTime}</span>
          </div>

          <Link href={tool.route}>
            <Button 
              className="w-full group-hover:bg-primary group-hover:text-primary-foreground"
              disabled={tool.status === 'coming-soon'}
            >
              Launch Tool
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
```

**`components/automations/FileUploader.tsx`:**
```typescript
"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Card } from "@/components/ui/card";
import { Upload, File, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface FileUploaderProps {
  accept?: Record<string, string[]>;
  maxFiles?: number;
  maxSize?: number;
  onUpload: (files: File[]) => Promise<void>;
  uploading?: boolean;
  uploadProgress?: number;
}

export function FileUploader({
  accept = { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"] },
  maxFiles = 2,
  maxSize = 50 * 1024 * 1024, // 50MB
  onUpload,
  uploading = false,
  uploadProgress = 0,
}: FileUploaderProps) {
  const [files, setFiles] = useState<File[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxFiles,
    maxSize,
    disabled: uploading,
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length > 0) {
      await onUpload(files);
    }
  };

  return (
    <div className="space-y-4">
      <Card
        {...getRootProps()}
        className={`border-2 border-dashed p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"}
          ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-4">
          <Upload className="h-12 w-12 text-muted-foreground" />
          <div>
            <p className="text-lg font-medium">
              {isDragActive ? "Drop files here" : "Drag & drop files here"}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              or click to browse (max {maxFiles} files, {Math.round(maxSize / 1024 / 1024)}MB each)
            </p>
          </div>
        </div>
      </Card>

      {files.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">Selected Files:</p>
          {files.map((file, index) => (
            <Card key={index} className="p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <File className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                {!uploading && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {uploading && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <Progress value={uploadProgress} />
        </div>
      )}

      {files.length > 0 && !uploading && (
        <Button onClick={handleUpload} className="w-full">
          Upload & Process
        </Button>
      )}
    </div>
  );
}
```

**`components/automations/ProcessingStatus.tsx`:**
```typescript
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Clock, AlertCircle, Loader2 } from "lucide-react";
import type { ProcessingJob } from "@/types/automations";

interface ProcessingStatusProps {
  job: ProcessingJob;
}

export function ProcessingStatus({ job }: ProcessingStatusProps) {
  const getStatusIcon = () => {
    switch (job.status) {
      case 'queued':
        return <Clock className="h-5 w-5 text-orange-600" />;
      case 'processing':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
    }
  };

  const getStatusColor = () => {
    switch (job.status) {
      case 'queued': return 'bg-orange-100 text-orange-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Processing Status</CardTitle>
          <Badge className={getStatusColor()}>
            <div className="flex items-center gap-1">
              {getStatusIcon()}
              <span className="capitalize">{job.status}</span>
            </div>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Progress</span>
            <span className="font-medium">{job.progress}%</span>
          </div>
          <Progress value={job.progress} />
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Job ID</p>
            <p className="font-mono text-xs">{job.id}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Created</p>
            <p>{new Date(job.createdAt).toLocaleString()}</p>
          </div>
        </div>

        {job.error && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-800 dark:text-red-200 font-medium">Error</p>
            <p className="text-sm text-red-600 dark:text-red-300 mt-1">{job.error}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

### Phase 3: Automation Hub Landing Page (Week 2)

#### 3.1 Main Hub Page

**`app/automations/page.tsx`:**
```typescript
import { AutomationCard } from "@/components/automations/AutomationCard";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Info } from "lucide-react";
import type { AutomationTool } from "@/types/automations";

const AUTOMATION_TOOLS: AutomationTool[] = [
  {
    id: 'post-review',
    name: 'Post Review Processor',
    description: 'Process handwritten annotations on PDF documents and apply changes to Word documents using AI vision analysis.',
    icon: '📝',
    route: '/automations/post-review',
    color: 'bg-purple-100 dark:bg-purple-900/20',
    status: 'active',
    features: [
      'GPT-4o Vision OCR',
      'Automatic change detection',
      'Word document updates',
      'Backup creation',
      'Preview before applying'
    ],
    estimatedTime: '2-5 minutes per document'
  },
  {
    id: 'a3-processor',
    name: 'A3 Handwriting Processor',
    description: 'Extract handwritten data from A3 financial planning forms and populate PDF templates automatically.',
    icon: '✍️',
    route: '/automations/a3-processor',
    color: 'bg-blue-100 dark:bg-blue-900/20',
    status: 'active',
    features: [
      'Section-based OCR',
      'Custom template support',
      'Spell checking',
      'Field positioning tools',
      'Batch processing'
    ],
    estimatedTime: '5-7 minutes per A3 form'
  },
  {
    id: 'value-creator',
    name: 'Value Creator Letter',
    description: 'Parse financial documents, detect changes and strikethroughs, and generate updated Word documents.',
    icon: '💰',
    route: '/automations/value-creator',
    color: 'bg-orange-100 dark:bg-orange-900/20',
    status: 'active',
    features: [
      'Strikethrough detection',
      'Amount parsing',
      'Date recognition',
      'Section chunking',
      'Word generation'
    ],
    estimatedTime: '3-6 minutes per letter'
  }
];

export default function AutomationsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Automation Hub</h1>
        <p className="text-muted-foreground mt-2">
          Unified platform for More4Life document automation tools
        </p>
      </div>

      {/* Info Alert */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>AI-Powered Document Processing</AlertTitle>
        <AlertDescription>
          These tools use GPT-4o Vision to process handwritten documents, detect changes,
          and automate document generation tasks. All processing happens securely with your data.
        </AlertDescription>
      </Alert>

      {/* Automation Cards Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {AUTOMATION_TOOLS.map(tool => (
          <AutomationCard key={tool.id} tool={tool} />
        ))}
      </div>

      {/* Statistics Section */}
      <div className="grid gap-4 md:grid-cols-3 mt-8">
        <div className="p-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="text-3xl font-bold text-green-700 dark:text-green-300">76%</div>
          <p className="text-sm text-green-600 dark:text-green-400 mt-1">
            Average time savings
          </p>
        </div>
        <div className="p-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div className="text-3xl font-bold text-blue-700 dark:text-blue-300">0</div>
          <p className="text-sm text-blue-600 dark:text-blue-400 mt-1">
            Transcription errors
          </p>
        </div>
        <div className="p-6 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
          <div className="text-3xl font-bold text-purple-700 dark:text-purple-300">3</div>
          <p className="text-sm text-purple-600 dark:text-purple-400 mt-1">
            Active automation tools
          </p>
        </div>
      </div>
    </div>
  );
}
```

#### 3.2 Update Sidebar Navigation

Add automation section to sidebar (`components/sidebar-container.tsx` or relevant sidebar component):

```typescript
{
  title: "Automations",
  url: "/automations",
  icon: Zap,
  items: [
    {
      title: "Automation Hub",
      url: "/automations",
    },
    {
      title: "Post Review",
      url: "/automations/post-review",
    },
    {
      title: "A3 Processor",
      url: "/automations/a3-processor",
    },
    {
      title: "Value Creator",
      url: "/automations/value-creator",
    },
  ],
}
```

---

### Phase 4: Post Review Automation (Week 3)

#### 4.1 Post Review Page

**`app/automations/post-review/page.tsx`:**
```typescript
"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileUploader } from "@/components/automations/FileUploader";
import { ProcessingStatus } from "@/components/automations/ProcessingStatus";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import type { ProcessingJob, PostReviewOptions } from "@/types/automations";

export default function PostReviewPage() {
  const [job, setJob] = useState<ProcessingJob | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [options, setOptions] = useState<PostReviewOptions>({
    enableOcr: true,
    createBackup: true,
    preserveFormatting: true,
    showPreview: true,
  });

  const handleUpload = async (files: File[]) => {
    setUploading(true);
    
    try {
      // Upload files to API
      const formData = new FormData();
      formData.append('originalDoc', files[0]);
      formData.append('annotatedPdf', files[1]);
      formData.append('options', JSON.stringify(options));

      const response = await fetch(process.env.NEXT_PUBLIC_POST_REVIEW_API + '/api/post-review/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      // Create job object
      const newJob: ProcessingJob = {
        id: data.jobId,
        toolId: 'post-review',
        status: 'queued',
        progress: 0,
        createdAt: new Date(),
        files: files.map((f, idx) => ({
          id: `${data.jobId}-${idx}`,
          name: f.name,
          size: f.size,
          type: f.type,
          uploadedAt: new Date(),
        })),
      };

      setJob(newJob);
      
      // Start processing
      await processDocument(data.jobId);
      
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const processDocument = async (jobId: string) => {
    // Poll for job status
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_POST_REVIEW_API}/api/post-review/status/${jobId}`
        );
        const data = await response.json();

        setJob(prev => prev ? { ...prev, ...data } : null);

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Status check failed:', error);
        clearInterval(pollInterval);
      }
    }, 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Post Review Processor</h1>
        <p className="text-muted-foreground mt-2">
          Process handwritten annotations and apply changes to Word documents
        </p>
      </div>

      {/* Info Alert */}
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Upload your original Word document and the annotated PDF with handwritten changes.
          The system will detect changes and update your document automatically.
        </AlertDescription>
      </Alert>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left Column - Upload & Options */}
        <div className="space-y-6">
          {/* File Upload */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Documents</CardTitle>
              <CardDescription>
                Select your original Word document and annotated PDF
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FileUploader
                accept={{
                  "application/pdf": [".pdf"],
                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"]
                }}
                maxFiles={2}
                onUpload={handleUpload}
                uploading={uploading}
                uploadProgress={uploadProgress}
              />
            </CardContent>
          </Card>

          {/* Processing Options */}
          <Card>
            <CardHeader>
              <CardTitle>Processing Options</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="enableOcr"
                  checked={options.enableOcr}
                  onCheckedChange={(checked) => 
                    setOptions(prev => ({ ...prev, enableOcr: checked as boolean }))
                  }
                />
                <Label htmlFor="enableOcr">Enable OCR (GPT-4o Vision)</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="createBackup"
                  checked={options.createBackup}
                  onCheckedChange={(checked) => 
                    setOptions(prev => ({ ...prev, createBackup: checked as boolean }))
                  }
                />
                <Label htmlFor="createBackup">Create backup of original</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="preserveFormatting"
                  checked={options.preserveFormatting}
                  onCheckedChange={(checked) => 
                    setOptions(prev => ({ ...prev, preserveFormatting: checked as boolean }))
                  }
                />
                <Label htmlFor="preserveFormatting">Preserve document formatting</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="showPreview"
                  checked={options.showPreview}
                  onCheckedChange={(checked) => 
                    setOptions(prev => ({ ...prev, showPreview: checked as boolean }))
                  }
                />
                <Label htmlFor="showPreview">Show preview before applying changes</Label>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Status */}
        <div>
          {job && <ProcessingStatus job={job} />}
          
          {job?.status === 'completed' && job.result && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Results</CardTitle>
              </CardHeader>
              <CardContent>
                {/* Display results */}
                <div className="space-y-2">
                  <p className="text-sm">{job.result.summary}</p>
                  {/* Download buttons for output files */}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### Phase 5: A3 Processor Automation (Week 4)

#### 5.1 A3 Processor Page

**`app/automations/a3-processor/page.tsx`:**

Similar structure to Post Review page but with:
- Single file upload (A3 form PDF/image)
- Template selection dropdown
- Custom field positioning option
- Spell check toggle
- Section preview/debugging visualization

Key differences:
```typescript
interface A3ProcessorOptions {
  templateId: string;
  enableSpellCheck: boolean;
  customFieldPositions: boolean;
}

// Add template selector
<Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
  <SelectTrigger>
    <SelectValue placeholder="Select template" />
  </SelectTrigger>
  <SelectContent>
    {templates.map(t => (
      <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
    ))}
  </SelectContent>
</Select>

// Add section visualization
{job?.status === 'processing' && sectionData && (
  <Card>
    <CardHeader>
      <CardTitle>Section Detection</CardTitle>
    </CardHeader>
    <CardContent>
      {/* Show detected sections with bounding boxes */}
      <div className="grid grid-cols-2 gap-2">
        {sectionData.sections.map(section => (
          <div key={section.id} className="border rounded p-2">
            <p className="text-sm font-medium">{section.name}</p>
            <p className="text-xs text-muted-foreground">{section.confidence}%</p>
          </div>
        ))}
      </div>
    </CardContent>
  </Card>
)}
```

---

### Phase 6: Value Creator Automation (Week 5)

#### 6.1 Value Creator Page

**`app/automations/value-creator/page.tsx`:**

Similar structure with specific options:
```typescript
interface ValueCreatorOptions {
  detectStrikethrough: boolean;
  detectAmounts: boolean;
  detectDates: boolean;
  conservativeMode: boolean;
}

// Processing options specific to value creator
<div className="space-y-4">
  <Checkbox
    id="detectStrikethrough"
    checked={options.detectStrikethrough}
    onCheckedChange={(checked) => 
      setOptions(prev => ({ ...prev, detectStrikethrough: checked as boolean }))
    }
  />
  <Label htmlFor="detectStrikethrough">
    Detect strikethrough text
  </Label>
  
  {/* Similar for other options */}
</div>
```

---

### Phase 7: Backend Integration & Testing (Week 6)

#### 7.1 Docker Compose Setup

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  # Next.js Frontend
  frontend:
    build:
      context: .
      dockerfile: dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_POST_REVIEW_API=http://post-review:8001
      - NEXT_PUBLIC_A3_API=http://a3-processor:8002
      - NEXT_PUBLIC_VALUE_CREATOR_API=http://value-creator:8003
    depends_on:
      - post-review
      - a3-processor
      - value-creator

  # Post Review API
  post-review:
    build:
      context: ./backend/post_review
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend/post_review/output:/app/output

  # A3 Processor API
  a3-processor:
    build:
      context: ./backend/a3_automation
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend/a3_automation/processed_documents:/app/processed_documents

  # Value Creator API
  value-creator:
    build:
      context: ./backend/value_creator
      dockerfile: Dockerfile
    ports:
      - "8003:8003"
    volumes:
      - ./backend/value_creator/output:/app/output

  # Redis for task queue
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

#### 7.2 Backend Dockerfiles

**`backend/post_review/Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8001

# Run API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
```

Similar Dockerfiles for other backends.

---

### Phase 8: Additional Features & Polish (Week 7-8)

#### 8.1 Job History & Management

**`app/automations/history/page.tsx`:**
```typescript
// Show all past processing jobs
// Allow re-download of results
// Filter by tool, date, status
```

#### 8.2 Real-time Updates with WebSockets

Upgrade from polling to WebSocket connections for real-time status updates:

```typescript
// Use socket.io-client
import io from 'socket.io-client';

const socket = io(process.env.NEXT_PUBLIC_POST_REVIEW_API);

socket.on('job-update', (data) => {
  setJob(prev => prev?.id === data.jobId ? { ...prev, ...data } : prev);
});
```

#### 8.3 Batch Processing

Add ability to process multiple documents:
```typescript
// Queue multiple jobs
// Show batch progress
// Download all results as zip
```

#### 8.4 Settings & Configuration

**`app/automations/settings/page.tsx`:**
```typescript
// API key management
// Default processing options
// Output folder preferences
// Notification settings
```

---

## File Migration Strategy

### Backend Code Migration

1. **Post Review:**
   ```bash
   # Copy entire directory
   cp -r C:/Users/dodso/post_review ./backend/post_review
   
   # Remove GUI files
   rm -rf ./backend/post_review/src/ui
   
   # Create API wrapper
   # api.py wraps existing src/core logic
   ```

2. **A3 Automation:**
   ```bash
   cp -r C:/Users/dodso/A3_handtotext ./backend/a3_automation
   
   # Remove UI files
   rm ./backend/a3_automation/*_launcher.py
   rm ./backend/a3_automation/main_launcher.py
   
   # Create API wrapper
   ```

3. **Value Creator:**
   ```bash
   cp -r C:/Users/dodso/value_creator_sfml ./backend/value_creator
   
   # Remove UI files
   rm ./backend/value_creator/value_creator_letter_app.py
   
   # Create API wrapper
   ```

### Frontend Migration

All Tkinter UI logic is **re-implemented** in TypeScript/React:
- No direct code migration
- Logic patterns translated to React components
- State management via React hooks
- Styling converted to Tailwind CSS classes

---

## Testing Strategy

### Unit Tests
- Backend API endpoints (pytest)
- React components (Jest + React Testing Library)
- File upload/download flows

### Integration Tests
- End-to-end automation flows
- API communication
- File processing pipelines

### User Acceptance Testing
1. Test with real More4Life documents
2. Verify output quality matches original tools
3. Performance benchmarking

---

## Deployment Strategy

### Development
```bash
# Start all services
docker-compose up

# Access at http://localhost:3000
```

### Production (Azure)

1. **Frontend:** Azure Static Web Apps (existing pipeline)
2. **Backend APIs:** Azure Container Apps (3 separate containers)
3. **Storage:** Azure Blob Storage for processed files
4. **Queue:** Azure Service Bus or Redis

**Architecture:**
```
Azure Static Web Apps (Frontend)
    ↓
Azure Application Gateway / API Management
    ↓
Azure Container Apps
    ├── Post Review API
    ├── A3 Processor API
    └── Value Creator API
    ↓
Azure Blob Storage (files)
Azure Service Bus (task queue)
```

---

## Success Criteria

✅ All three automation tools accessible via unified web interface  
✅ Backend logic unchanged - only API wrappers added  
✅ Frontend matches FW_Frontend theme and design system  
✅ File upload/download working smoothly  
✅ Real-time processing status updates  
✅ Error handling and user feedback  
✅ Mobile-responsive design  
✅ Dark mode support  
✅ Docker-based deployment  
✅ Production-ready on Azure  

---

## Timeline Summary

| Week | Phase | Deliverables |
|------|-------|-------------|
| 1 | Setup & Architecture | Project structure, API wrappers, environment config |
| 2 | Core Infrastructure | Shared components, hub page, backend APIs |
| 3 | Post Review | Complete Post Review automation page |
| 4 | A3 Processor | Complete A3 automation page |
| 5 | Value Creator | Complete Value Creator page |
| 6 | Integration & Testing | Docker setup, end-to-end testing |
| 7-8 | Polish & Deployment | History, real-time updates, batch processing, production deployment |

**Total Estimated Time:** 8 weeks (1 developer)

---

## Risk Mitigation

### Technical Risks

**Risk:** Backend Python code has dependencies on local file system  
**Mitigation:** Use Docker volumes for file I/O, abstract file paths

**Risk:** File upload size limits  
**Mitigation:** Implement chunked uploads, increase server limits

**Risk:** Long processing times block UI  
**Mitigation:** Async processing with job queue (Celery + Redis)

**Risk:** GPT-4o API rate limits  
**Mitigation:** Implement retry logic, queue management, rate limiting

### Operational Risks

**Risk:** Existing tools break during migration  
**Mitigation:** Keep original Python scripts unchanged, only add API layer

**Risk:** User training required for new interface  
**Mitigation:** Match familiar workflows, add tooltips and help text

---

## Future Enhancements

1. **Batch Processing Dashboard:** Process multiple documents simultaneously
2. **Template Library:** Share and manage A3 templates across team
3. **Audit Trail:** Track all document processing for compliance
4. **Email Notifications:** Alert when processing complete
5. **Mobile App:** Native iOS/Android apps
6. **Advanced Analytics:** Processing statistics, time savings metrics
7. **API Access:** RESTful API for external integrations
8. **User Management:** Multi-user support with permissions

---

## Appendix A: Technology Stack Summary

### Frontend
- **Framework:** Next.js 14.2.35 (React 18)
- **Language:** TypeScript 5
- **Styling:** Tailwind CSS 3.4.1
- **Icons:** lucide-react
- **State:** React useState hooks (future: Zustand for job management)
- **File Upload:** TODO: react-dropzone or native drag-and-drop
- **HTTP Client:** TODO: Axios or native fetch
- **Real-time:** TODO: Socket.io-client for live updates

### Backend
- **Framework:** FastAPI (TODO: Create API wrappers)
- **Language:** Python 3.11+
- **Server:** Uvicorn
- **Task Queue:** Celery + Redis (TODO)
- **File Storage:** Local / Azure Blob (TODO)
- **AI:** M4L VL Model (OpenAI GPT-4o Vision)
- **Document Processing:** python-docx, PyPDF2, pdf2image

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose / Azure Container Apps
- **Frontend Hosting:** Azure Static Web Apps
- **API Hosting:** Azure Container Apps
- **Storage:** Azure Blob Storage
- **Queue:** Redis / Azure Service Bus
- **CI/CD:** GitHub Actions

---

## Appendix B: Color Palette Reference

### More4Life Brand Colors

#### Primary Brand Colors
```css
/* tailwind.config.ts */
'm4l-orange': '#e67e22'  /* Primary orange - buttons, highlights, active states */
'm4l-blue': '#00426b'    /* Primary blue - headings, important text */
```

#### Application Colors
```css
/* globals.css */
--background: #f9fafb      /* gray-50 - Main background */
--foreground: #171717      /* Dark text */

/* Component backgrounds */
white: #ffffff             /* Cards, sidebar, header */
```

#### Tailwind Default Grays (Used throughout)
```css
gray-50: #f9fafb
gray-100: #f3f4f6
gray-200: #e5e7eb
gray-500: #6b7280
gray-600: #4b5563
gray-700: #374151
gray-900: #111827
```

### Status Colors (Tailwind Defaults)
```css
green-600: #16a34a   /* Success */
green-100: #dcfce7   /* Success background */
yellow-600: #ca8a04  /* Warning/Processing */
yellow-100: #fef9c3  /* Warning background */
red-600: #dc2626     /* Error */
red-100: #fee2e2     /* Error background */
blue-600: #2563eb    /* Info */
blue-100: #dbeafe    /* Info background */
orange-50: #fff7ed   /* Active nav item background */
```

### Component-Specific Colors
```css
/* Tool Cards */
Post Review: bg-orange-100 (icon), text-m4l-orange
A3 Form: bg-blue-100 (icon), text-m4l-blue
Value Creator: bg-green-100 (icon), text-green-600

/* Stats Cards */
Documents: bg-orange-100 (icon), text-m4l-orange
Time Saved: bg-blue-100 (icon), text-m4l-blue  
Active Jobs: bg-green-100 (icon), text-green-600
```

---

## Conclusion

This implementation plan provides a comprehensive roadmap for consolidating three Python automation tools into a unified web platform using the FW_Frontend theme and architecture. The approach prioritizes:

1. **Preservation:** Backend logic remains unchanged
2. **Modernization:** Web-based UI with modern tech stack
3. **Consistency:** Unified theme and UX across all tools
4. **Scalability:** Cloud-native architecture ready for Azure
5. **Maintainability:** Clean separation of concerns, Docker-based deployment

The 8-week timeline provides realistic milestones while allowing flexibility for testing and refinement. The result will be a professional, production-ready automation hub that dramatically improves the user experience while maintaining the proven backend logic.
