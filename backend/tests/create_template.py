from pathlib import Path
import fitz
p = Path('A3_templates/More4Life A3 Goals - blank.pdf')
if not p.exists():
    doc = fitz.open()
    doc.new_page()
    doc.save(str(p))
    doc.close()
    print('Created template', p)
else:
    print('Template exists')
