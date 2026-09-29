#!/usr/bin/env python3
import json
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "diag26", ROOT / "scripts" / "26_claude_review_diagnostics.py")
diag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diag)

def main():
    voy = diag.sequence_units(diag.load_corpus())
    payload = {
        "voynich_exact_repeats": diag.exact_repeat_diagnostics(voy),
        "comparator_seam_sensitivity": diag.comparator_seam_diagnostics(),
        "voynich_omitted_item_break_sensitivity": (
            diag.voynich_omitted_item_break_diagnostics()
        ),
    }
    out = ROOT / "results" / "claude_review_quick_diagnostics.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
