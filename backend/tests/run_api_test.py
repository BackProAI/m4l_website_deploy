from pathlib import Path
import sys, json
# Ensure repo root on sys.path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

try:
    from fastapi.testclient import TestClient
    from backend.api.app import app
except Exception as e:
    print('IMPORT_ERROR', e)
    raise SystemExit(2)

client = TestClient(app)

infile = Path('backend/tests/sample_in.pdf')
if not infile.exists():
    print('sample_in.pdf not found; creating dummy')
    import fitz
    doc = fitz.open()
    doc.new_page()
    doc.save(str(infile))
    doc.close()

with open(infile,'rb') as f:
    files = {'file': ('sample_in.pdf', f, 'application/pdf')}
    r = client.post('/api/a3/flatten', files=files)
    print('POST status', r.status_code)
    print('POST body', r.text)
    if r.status_code != 200:
        raise SystemExit(3)
    data = r.json()
    download = data.get('downloadUrl') or data.get('flattenedPdf')
    print('download field:', download)
    if download.startswith('/'):
        resp = client.get(download)
    else:
        resp = client.get(download)
    print('GET download status', resp.status_code)
    out = Path('backend/tests/downloaded_via_client.pdf')
    out.write_bytes(resp.content)
    print('Wrote', out, 'size', out.stat().st_size)
