import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

modules = [
    'backend.a3_automation.flatten',
    'backend.a3_automation.a3_sectioned_automation',
    'backend.post_review.src.core.unified_post_review_processor',
    'backend.value_creator.src.production_orchestrator'
]

for m in modules:
    try:
        mod = __import__(m, fromlist=['*'])
        print(f'OK: {m} ->', mod)
    except Exception as e:
        print(f'ERROR importing {m}:', repr(e))
