import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Ensure OPENAI_API_KEY present for A3SectionedProcessor
os.environ.setdefault('OPENAI_API_KEY', 'test-api-key')

from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)

# Ensure sample input exists
infile = Path('backend/tests/sample_in.pdf')
if not infile.exists():
    import fitz
    doc = fitz.open()
    doc.new_page()
    doc.save(str(infile))
    doc.close()

print('Uploading to /api/a3/process...')
with open(infile, 'rb') as f:
    files = {'file': ('sample_in.pdf', f, 'application/pdf')}
    r = client.post('/api/a3/process', files=files)
    print('status', r.status_code)
    print('body', r.text)
    if r.status_code != 200:
        raise SystemExit(2)
    data = r.json()

# Locate output pdf
output = data.get('result', {}).get('output_pdf_path') or data.get('result', {}).get('output_pdf')
if not output:
    print('No output PDF path returned')
    raise SystemExit(3)

print('Processing output path:', output)
# If returned as OS path, convert to URL path if needed
# For TestClient, request the path as route '/downloads/<name>' if output in outputs dir
outpath = Path(output)
if outpath.exists():
    # upload this file to flatten endpoint
    print('Found output file on disk:', outpath)
    with open(outpath, 'rb') as fo:
        files = {'file': (outpath.name, fo, 'application/pdf')}
        r2 = client.post('/api/a3/flatten', files=files)
        print('flatten status', r2.status_code)
        print('flatten body', r2.text)
        if r2.status_code != 200:
            raise SystemExit(4)
        j = r2.json()
        dl = j.get('downloadUrl') or j.get('flattenedPdf')
        print('download url:', dl)
        if dl.startswith('/'):
            rr = client.get(dl)
            print('download GET', rr.status_code, 'len', len(rr.content))
            out = Path('backend/tests/full_e2e_flattened.pdf')
            out.write_bytes(rr.content)
            print('Saved flattened ->', out)
else:
    print('Output file not present on disk, attempting to GET via returned URL')
    # Try to GET the returned path
    rget = client.get(output)
    print('GET output status', rget.status_code)
    if rget.status_code == 200:
        temp = Path('backend/tests/full_e2e_output.pdf')
        temp.write_bytes(rget.content)
        print('Saved output to', temp)
    else:
        print('Unable to retrieve output')
        raise SystemExit(5)
