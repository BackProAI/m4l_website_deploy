"""
Minimal FastAPI backend scaffold for synchronous processing endpoints.
Endpoints:
- POST /api/a3/process  (multipart file)
- POST /api/a3/flatten   (multipart file)
- POST /api/post-review/process (multipart pdf + docx)
- POST /api/value-creator/process (multipart pdf + docx)

Note: This scaffold calls existing Python processors synchronously. For production
we should add a job queue (RQ/Celery) and proper auth.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import os
import shutil
import uuid
from typing import Optional, Dict, Any
import threading

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="M4L Processing API")

# Add CORS middleware to allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://m4l-website-deploy.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    password: str

# Simple password - should be in environment variable in production
LOGIN_PASSWORD = "more4life123"

# Storage dirs
ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT / "backend_storage" / "uploads"
OUTPUT_DIR = ROOT / "backend_storage" / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Expose a safe downloads endpoint for frontend to fetch processed files
app.mount("/downloads_static", StaticFiles(directory=str(OUTPUT_DIR)), name="downloads_static")

# In-memory job storage (use Redis/DB in production)
jobs: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "M4L Processing API"}

# Try imports for existing processors
try:
    from ..a3_automation.a3_sectioned_automation import A3SectionedProcessor
except Exception as e:
    print(f"Failed to import A3SectionedProcessor: {e}")
    A3SectionedProcessor = None

# Import flatten separately so the headless flattener remains available
try:
    from ..a3_automation.flatten import flatten_pdf
except Exception as e:
    print(f"Failed to import flatten_pdf: {e}")
    flatten_pdf = None

try:
    from ..post_review.src.core.unified_post_review_processor import process_post_review_documents
except Exception as e:
    print(f"Failed to import post_review processor: {e}")
    import traceback
    traceback.print_exc()
    process_post_review_documents = None

try:
    from ..value_creator.src.production_orchestrator import ProductionDocumentOrchestrator as ProductionOrchestrator
except Exception as e:
    print(f"Failed to import ProductionOrchestrator: {e}")
    import traceback
    traceback.print_exc()
    ProductionOrchestrator = None


def _save_upload(upload: UploadFile, dest: Path) -> Path:
    """Save an UploadFile to disk with a configurable max size enforcement.

    Raises HTTPException(413) if the uploaded file exceeds `MAX_UPLOAD_SIZE_BYTES`.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Configurable max upload size (bytes) via env var, default 100MB
    try:
        MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(100 * 1024 * 1024)))
    except Exception:
        MAX_UPLOAD_SIZE = 100 * 1024 * 1024

    chunk_size = 1024 * 1024
    total_written = 0
    try:
        with open(dest, "wb") as f:
            while True:
                chunk = upload.file.read(chunk_size)
                if not chunk:
                    break
                total_written += len(chunk)
                if total_written > MAX_UPLOAD_SIZE:
                    # cleanup partial file
                    try:
                        f.close()
                    except Exception:
                        pass
                    try:
                        dest.unlink()
                    except Exception:
                        pass
                    raise HTTPException(status_code=413, detail="Uploaded file is too large")
                f.write(chunk)
    finally:
        try:
            upload.file.seek(0)
        except Exception:
            pass

    return dest


def _process_a3_background(job_id: str, save_path: Path, api_key: str):
    """Background task to process A3 document"""
    try:
        jobs[job_id]["status"] = "processing"
        processor = A3SectionedProcessor(api_key=api_key)
        result = processor.process_file(save_path)

        # Move processed file to outputs
        if result and "output_pdf_path" in result and result["output_pdf_path"]:
            output_path = Path(result["output_pdf_path"])
            if output_path.exists():
                output_filename = f"{job_id}_processed.pdf"
                download_path = OUTPUT_DIR / output_filename
                shutil.copy2(output_path, download_path)
                
                result["output_pdf_path"] = f"/view/{output_filename}"
                result["downloadUrl"] = f"/downloads/{output_filename}"
            else:
                result["output_pdf_path"] = str(output_path)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        import traceback
        traceback.print_exc()
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/api/a3/process")
async def api_a3_process(file: UploadFile = File(...)):
    if A3SectionedProcessor is None:
        raise HTTPException(status_code=500, detail="A3 processor not available")

    if not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.tiff')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    upload_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{upload_id}_{file.filename}"
    _save_upload(file, save_path)

    # Ensure API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    # Initialize job status
    jobs[upload_id] = {
        "status": "queued",
        "filename": file.filename,
        "result": None,
        "error": None
    }

    # Start background processing
    thread = threading.Thread(target=_process_a3_background, args=(upload_id, save_path, api_key))
    thread.daemon = True
    thread.start()

    return JSONResponse(content={"jobId": upload_id, "status": "processing"})


@app.get("/api/a3/status/{job_id}")
async def api_a3_status(job_id: str):
    """Check the status of an A3 processing job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    response = {
        "jobId": job_id,
        "status": job["status"],
        "filename": job.get("filename")
    }
    
    if job["status"] == "completed":
        response["result"] = job["result"]
    elif job["status"] == "failed":
        response["error"] = job["error"]
    
    return JSONResponse(content=response)


@app.post("/api/a3/flatten")
async def api_a3_flatten(file: UploadFile = File(...)):
    """Flatten PDF form fields to make them non-editable."""
    if flatten_pdf is None:
        raise HTTPException(status_code=500, detail="Flatten utility not available")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for flattening")

    upload_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{upload_id}_{file.filename}"
    _save_upload(file, save_path)

    output_path = OUTPUT_DIR / f"{upload_id}_flattened.pdf"
    try:
        flattened = flatten_pdf(str(save_path), str(output_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flatten failed: {e}")

    return JSONResponse(content={"flattenedPdf": str(output_path), "downloadUrl": f"/downloads/{output_path.name}"})


@app.get("/downloads/{filename}")
async def download_file(filename: str):
    # Prevent path traversal by using only the basename
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(file_path), filename=safe_name, media_type='application/pdf')


@app.get("/downloads/{job_id}/{filename}")
async def download_file_from_job(job_id: str, filename: str):
    """Download files from job-specific subdirectories (e.g., post-review, value-creator)"""
    # Prevent path traversal
    safe_job_id = Path(job_id).name
    safe_filename = Path(filename).name
    file_path = OUTPUT_DIR / safe_job_id / safe_filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    media_type = 'application/pdf' if safe_filename.lower().endswith('.pdf') else \
                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    return FileResponse(path=str(file_path), filename=safe_filename, media_type=media_type)


@app.get("/api/history")
async def get_history(days: int = 30):
    """
    Get processing history for the last N days
    
    Scans the outputs directory and returns job information including:
    - Job ID, tool type, status, timestamp, download URL
    """
    from datetime import datetime, timedelta
    import json
    
    # Get the base URL for constructing download links
    # In production, use the deployed backend URL
    base_url = os.getenv("BACKEND_URL", "")
    
    cutoff_time = datetime.now() - timedelta(days=days)
    history_items = []
    
    try:
        # Scan outputs directory
        for item in OUTPUT_DIR.iterdir():
            try:
                # Get modification time
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                
                # Skip items older than cutoff
                if mtime < cutoff_time:
                    continue
                
                # Determine job type and details
                if item.is_dir():
                    # Post-review or value-creator (subdirectory structure)
                    job_id = item.name
                    
                    # Check for value-creator
                    if (item / "value_creator_output.docx").exists():
                        debug_file = item / "value_creator_output.debug.json"
                        output_file = "value_creator_output.docx"
                        
                        # Try to extract original filename from debug JSON
                        original_name = "value-creator-document.pdf"
                        if debug_file.exists():
                            try:
                                with open(debug_file, 'r', encoding='utf-8') as f:
                                    debug_data = json.load(f)
                                    input_path = debug_data.get('input_path', '')
                                    if input_path:
                                        original_name = Path(input_path).name
                            except:
                                pass
                        
                        history_items.append({
                            "id": job_id,
                            "tool": "value-creator",
                            "fileName": original_name,
                            "status": "completed",
                            "timestamp": mtime.isoformat(),
                            "downloadUrl": f"{base_url}/downloads/{job_id}/{output_file}"
                        })
                    
                    # Check for post-review
                    elif any(f.name.startswith('changes_summary_') for f in item.iterdir() if f.is_file()):
                        # Find the DOCX file
                        docx_files = [f for f in item.iterdir() if f.suffix == '.docx']
                        if docx_files:
                            output_file = docx_files[0].name
                            
                            # Try to extract info from changes summary
                            original_name = "post-review-document.pdf"
                            summary_files = [f for f in item.iterdir() if f.name.startswith('changes_summary_')]
                            if summary_files:
                                try:
                                    with open(summary_files[0], 'r', encoding='utf-8') as f:
                                        summary_data = json.load(f)
                                        # Could extract more info here if available
                                except:
                                    pass
                            
                            history_items.append({
                                "id": job_id,
                                "tool": "post-review",
                                "fileName": original_name,
                                "status": "completed",
                                "timestamp": mtime.isoformat(),
                                "downloadUrl": f"{base_url}/downloads/{job_id}/{output_file}"
                            })
                
                elif item.is_file():
                    # A3 automation (direct PDF files)
                    if item.suffix == '.pdf' and ('_processed.pdf' in item.name or '_flattened.pdf' in item.name):
                        # Extract UUID from filename
                        job_id = item.stem.replace('_processed', '').replace('_flattened', '')
                        
                        history_items.append({
                            "id": job_id,
                            "tool": "a3-automation",
                            "fileName": item.name,
                            "status": "completed",
                            "timestamp": mtime.isoformat(),
                            "downloadUrl": f"{base_url}/downloads/{item.name}"
                        })
            
            except Exception as e:
                # Skip items that cause errors (permissions, etc.)
                continue
        
        # Sort by timestamp descending (most recent first)
        history_items.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return JSONResponse(content={"history": history_items, "total": len(history_items)})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Simple authentication - creates a session ID"""
    if request.password == LOGIN_PASSWORD:
        session_id = str(uuid.uuid4())
        response = JSONResponse(content={"success": True, "message": "Login successful"})
        response.set_cookie(
            key="m4l_session",
            value=session_id,
            httponly=True,
            max_age=30*24*60*60,  # 30 days
            samesite="lax"
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid password")


@app.post("/api/auth/logout")
async def logout():
    """Logout and clear session"""
    response = JSONResponse(content={"success": True, "message": "Logged out"})
    response.delete_cookie(key="m4l_session")
    return response
    
    try:
        # Scan outputs directory
        for item in OUTPUT_DIR.iterdir():
            try:
                # Get modification time
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                
                # Skip items older than cutoff
                if mtime < cutoff_time:
                    continue
                
                # Determine job type and details
                if item.is_dir():
                    # Post-review or value-creator (subdirectory structure)
                    job_id = item.name
                    
                    # Check for value-creator
                    if (item / "value_creator_output.docx").exists():
                        debug_file = item / "value_creator_output.debug.json"
                        output_file = "value_creator_output.docx"
                        
                        # Try to extract original filename from debug JSON
                        original_name = "value-creator-document.pdf"
                        if debug_file.exists():
                            try:
                                with open(debug_file, 'r', encoding='utf-8') as f:
                                    debug_data = json.load(f)
                                    input_path = debug_data.get('input_path', '')
                                    if input_path:
                                        original_name = Path(input_path).name
                            except:
                                pass
                        
                        history_items.append({
                            "id": job_id,
                            "tool": "value-creator",
                            "fileName": original_name,
                            "status": "completed",
                            "timestamp": mtime.isoformat(),
                            "downloadUrl": f"{base_url}/downloads/{job_id}/{output_file}"
                        })
                    
                    # Check for post-review
                    elif any(f.name.startswith('changes_summary_') for f in item.iterdir() if f.is_file()):
                        # Find the DOCX file
                        docx_files = [f for f in item.iterdir() if f.suffix == '.docx']
                        if docx_files:
                            output_file = docx_files[0].name
                            
                            # Try to extract info from changes summary
                            original_name = "post-review-document.pdf"
                            summary_files = [f for f in item.iterdir() if f.name.startswith('changes_summary_')]
                            if summary_files:
                                try:
                                    with open(summary_files[0], 'r', encoding='utf-8') as f:
                                        summary_data = json.load(f)
                                        # Could extract more info here if available
                                except:
                                    pass
                            
                            history_items.append({
                                "id": job_id,
                                "tool": "post-review",
                                "fileName": original_name,
                                "status": "completed",
                                "timestamp": mtime.isoformat(),
                                "downloadUrl": f"{base_url}/downloads/{job_id}/{output_file}"
                            })
                
                elif item.is_file():
                    # A3 automation (direct PDF files)
                    if item.suffix == '.pdf' and ('_processed.pdf' in item.name or '_flattened.pdf' in item.name):
                        # Extract UUID from filename
                        job_id = item.stem.replace('_processed', '').replace('_flattened', '')
                        
                        history_items.append({
                            "id": job_id,
                            "tool": "a3-automation",
                            "fileName": item.name,
                            "status": "completed",
                            "timestamp": mtime.isoformat(),
                            "downloadUrl": f"{base_url}/downloads/{item.name}"
                        })
            
            except Exception as e:
                # Skip items that cause errors (permissions, etc.)
                continue
        
        # Sort by timestamp descending (most recent first)
        history_items.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return JSONResponse(content={"history": history_items, "total": len(history_items)})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@app.get("/view/{filename}")
async def view_file(filename: str):
    """Serve PDF for inline viewing (not download)"""
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(file_path),
        media_type='application/pdf',
        headers={"Content-Disposition": "inline"}  # Force inline display
    )


def _process_post_review_background(job_id: str, pdf_path: Path, docx_path: Path, output_dir: Path):
    """Background task to process Post Review document"""
    try:
        jobs[job_id]["status"] = "processing"
        result = process_post_review_documents(str(pdf_path), str(docx_path), output_dir=str(output_dir))
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        import traceback
        traceback.print_exc()
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/api/post-review/process")
async def api_post_review_process(pdf: UploadFile = File(...), docx: UploadFile = File(...)):
    if process_post_review_documents is None:
        raise HTTPException(status_code=500, detail="Post review processor not available")

    if not pdf.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="PDF required for post-review")
    if not docx.filename.lower().endswith('.docx'):
        raise HTTPException(status_code=400, detail="Word (.docx) required for post-review")

    upload_id = str(uuid.uuid4())
    pdf_path = UPLOAD_DIR / f"{upload_id}_{pdf.filename}"
    docx_path = UPLOAD_DIR / f"{upload_id}_{docx.filename}"
    output_dir = OUTPUT_DIR / upload_id
    
    _save_upload(pdf, pdf_path)
    _save_upload(docx, docx_path)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize job status
    jobs[upload_id] = {
        "status": "queued",
        "pdf_filename": pdf.filename,
        "docx_filename": docx.filename,
        "result": None,
        "error": None
    }

    # Start background processing
    thread = threading.Thread(target=_process_post_review_background, args=(upload_id, pdf_path, docx_path, output_dir))
    thread.daemon = True
    thread.start()

    return JSONResponse(content={"jobId": upload_id, "status": "processing"})


@app.get("/api/post-review/status/{job_id}")
async def api_post_review_status(job_id: str):
    """Check the status of a Post Review processing job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    response = {
        "jobId": job_id,
        "status": job["status"],
        "pdf_filename": job.get("pdf_filename"),
        "docx_filename": job.get("docx_filename")
    }
    
    if job["status"] == "completed":
        response["result"] = job["result"]
    elif job["status"] == "failed":
        response["error"] = job["error"]
    
    return JSONResponse(content=response)


def _process_value_creator_background(job_id: str, pdf_path: Path, docx_path: Path, output_path: Path):
    """Background task to process Value Creator document"""
    try:
        jobs[job_id]["status"] = "processing"
        orchestrator = ProductionOrchestrator()
        result = orchestrator.process_value_creator_document(
            pdf_path=str(pdf_path), 
            word_template_path=str(docx_path),
            output_path=str(output_path)
        )
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        import traceback
        traceback.print_exc()
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/api/value-creator/process")
async def api_value_creator_process(pdf: UploadFile = File(...), docx: UploadFile = File(...)):
    if ProductionOrchestrator is None:
        raise HTTPException(status_code=500, detail="Value Creator processor not available")

    upload_id = str(uuid.uuid4())
    pdf_path = UPLOAD_DIR / f"{upload_id}_{pdf.filename}"
    docx_path = UPLOAD_DIR / f"{upload_id}_{docx.filename}"
    output_path = OUTPUT_DIR / upload_id / "value_creator_output.docx"
    
    _save_upload(pdf, pdf_path)
    _save_upload(docx, docx_path)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize job status
    jobs[upload_id] = {
        "status": "queued",
        "pdf_filename": pdf.filename,
        "docx_filename": docx.filename,
        "result": None,
        "error": None
    }

    # Start background processing
    thread = threading.Thread(target=_process_value_creator_background, args=(upload_id, pdf_path, docx_path, output_path))
    thread.daemon = True
    thread.start()

    return JSONResponse(content={"jobId": upload_id, "status": "processing"})


@app.get("/api/value-creator/status/{job_id}")
async def api_value_creator_status(job_id: str):
    """Check the status of a Value Creator processing job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    response = {
        "jobId": job_id,
        "status": job["status"],
        "pdf_filename": job.get("pdf_filename"),
        "docx_filename": job.get("docx_filename")
    }
    
    if job["status"] == "completed":
        response["result"] = job["result"]
    elif job["status"] == "failed":
        response["error"] = job["error"]
    
    return JSONResponse(content=response)
