FastAPI backend scaffold for M4L processors

Run (development):

1. Create a virtual environment and install deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set environment vars (e.g., `OPENAI_API_KEY`) in your shell or `.env`.

3. Start the server:

```powershell
uvicorn backend.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:
- `POST /api/a3/process` - multipart file (pdf/image)
- `POST /api/a3/flatten` - multipart pdf file
- `POST /api/post-review/process` - multipart `pdf` + `docx`
- `POST /api/value-creator/process` - multipart `pdf` + `docx`

Notes:
- Current endpoints call processors synchronously. For production, add a background job queue (Redis + RQ/Celery) and convert endpoints to enqueue jobs.
- `backend/a3_automation/flatten.py` is a headless flatten function suitable for server use.
