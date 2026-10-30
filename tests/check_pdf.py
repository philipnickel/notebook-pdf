"""End-to-end check: export the test notebooks to PDF the way VS Code does.

Run with the target env's Python, inside an activated env (e.g. `conda run -n base python tests/check_pdf.py`).
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NOTEBOOKS = Path(__file__).parent / "notebooks"
# broken_math.ipynb contains a LaTeX error; -Z continue-on-errors must still produce a PDF
CASES = ["sample.ipynb", "broken_math.ipynb"]


def export(name: str) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        nb = Path(tmp) / name
        shutil.copy(NOTEBOOKS / name, nb)
        # VS Code's "Export to PDF" runs nbconvert with the kernel env's interpreter
        proc = subprocess.run(
            [sys.executable, "-m", "jupyter", "nbconvert", "--to", "pdf", nb.name],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        print(proc.stdout, proc.stderr, sep="\n")
        if proc.returncode != 0:
            print(f"FAIL {name}: nbconvert exited with {proc.returncode}")
            return False
        if "Running tectonic" not in proc.stderr:
            print(f"FAIL {name}: nbconvert did not use tectonic; is the config in $PREFIX/etc/jupyter picked up?")
            return False
        pdf = nb.with_suffix(".pdf")
        if not pdf.exists() or pdf.read_bytes()[:4] != b"%PDF":
            print(f"FAIL {name}: {pdf.name} missing or not a PDF")
            return False
        print(f"OK {name}: {pdf.name} ({pdf.stat().st_size} bytes)")
    return True


def main() -> int:
    results = [export(name) for name in CASES]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
