import zipfile, os
from pathlib import Path

root = Path.cwd()
dest = root.parent / "smart-sales-backend.zip"

EXCLUDE_DIRS = {'.venv','__pycache__','media','.git','node_modules','.mypy_cache','.pytest_cache'}
EXCLUDE_FILES = {'.env'}
EXCLUDE_EXTS = {'.pyc','.log','.sqlite3'}

with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for fn in fns:
            if fn in EXCLUDE_FILES: 
                continue
            ext = os.path.splitext(fn)[1].lower()
            if ext in EXCLUDE_EXTS:
                continue
            p = Path(dp) / fn
            arc = p.relative_to(root)
            z.write(p, arc.as_posix())

print(f"ZIP creado: {dest}")
