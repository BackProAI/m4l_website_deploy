from pathlib import Path
import sys
ROOT=Path('C:/Users/dodso/m4l_website')
sys.path.insert(0,str(ROOT))

import importlib, traceback
try:
    m = importlib.import_module('backend.a3_automation.a3_sectioned_automation')
    print('A3 module imported OK')
except Exception:
    traceback.print_exc()
