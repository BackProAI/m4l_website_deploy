from pathlib import Path
import sys

# Ensure repository root is on sys.path so `backend` can be imported when running this script directly
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Simple smoke test for headless flatten
try:
    from backend.a3_automation.flatten import flatten_pdf
    import fitz
except Exception as e:
    print("IMPORT_ERROR", e)
    raise SystemExit(2)

TEST_DIR = Path(__file__).resolve().parent
TEST_DIR.mkdir(parents=True, exist_ok=True)

input_pdf = TEST_DIR / "sample_in.pdf"
output_pdf = TEST_DIR / "sample_out.pdf"

# create a minimal PDF
try:
    doc = fitz.open()
    doc.new_page()
    doc.save(str(input_pdf))
    doc.close()
    print("Created sample PDF:", input_pdf)
except Exception as e:
    print("Failed to create sample PDF:", e)
    raise SystemExit(3)

# Run flatten
try:
    out = flatten_pdf(str(input_pdf), str(output_pdf))
    print("Flatten returned:", out)
    if Path(out).exists():
        print("Output exists:", out)
    else:
        print("Output missing")
except Exception as e:
    print("FLATTEN_ERROR", e)
    raise SystemExit(4)

print("SMOKE_TEST_OK")
