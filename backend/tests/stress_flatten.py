from pathlib import Path
import sys
import time
import statistics

# Make repo root importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.a3_automation.flatten import flatten_pdf
import fitz

OUT_DIR = Path(__file__).resolve().parent / "stress_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Configurable parameters
FILES = 3
PAGES = 10

print(f"Stress test: {FILES} files x {PAGES} pages each")

results = []
errors = []

for i in range(FILES):
    in_path = OUT_DIR / f"stress_in_{i+1}.pdf"
    out_path = OUT_DIR / f"stress_out_{i+1}.pdf"

    # create PDF with PAGES pages
    try:
        doc = fitz.open()
        for p in range(PAGES):
            page = doc.new_page()
            # add some text to increase content
            page.insert_text((72, 72), f"Stress test doc {i+1} page {p+1}")
        doc.save(str(in_path))
        doc.close()
    except Exception as e:
        print(f"Failed to create test PDF {in_path}: {e}")
        errors.append((in_path, str(e)))
        continue

    # run flatten and time it
    start = time.perf_counter()
    try:
        flattened = flatten_pdf(str(in_path), str(out_path))
        elapsed = time.perf_counter() - start
        size_bytes = out_path.stat().st_size if out_path.exists() else -1
        print(f"File {in_path.name} flattened -> {out_path.name} in {elapsed:.2f}s size={size_bytes}")
        results.append(elapsed)
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"ERROR flattening {in_path.name}: {e} (elapsed {elapsed:.2f}s)")
        errors.append((in_path, str(e)))

print("\nSummary:")
print(f"Total files attempted: {FILES}")
print(f"Successful: {len(results)}; Failed: {len(errors)}")
if results:
    print(f"Mean: {statistics.mean(results):.2f}s, Median: {statistics.median(results):.2f}s, Max: {max(results):.2f}s")

if errors:
    print("Errors:")
    for e in errors:
        print(e)

print("Stress test complete")
