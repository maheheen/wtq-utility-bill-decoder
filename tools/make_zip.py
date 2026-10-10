"""Build submission.zip from ../output, . (source) and ../demo. Refuses to build if it finds secrets or the size is over 15 MB."""
import pathlib, re, sys, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC, OUT, DEMO = ROOT / "source", ROOT / "output", ROOT / "demo"
SKIP_DIRS = {".git", ".cache", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache", "data"}
SKIP_FILES = {".env"}
SECRET = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,})")
LIMIT = 15 * 1024 * 1024

def walk(base):
    for p in sorted(base.rglob("*")):
        if p.is_dir() or p.name in SKIP_FILES: continue
        if any(part in SKIP_DIRS for part in p.relative_to(base).parts): continue
        yield p

files = []
for need in ("level1.csv", "level2.csv"):
    if not (OUT / need).exists(): sys.exit(f"missing output/{need}")
    files.append((OUT / need, f"output/{need}"))
for req in ("README.md", ".env.example", "requirements.txt"):
    if not (SRC / req).exists(): sys.exit(f"missing source/{req}")
for p in walk(SRC):
    files.append((p, f"source/{p.relative_to(SRC).as_posix()}"))
if DEMO.exists():
    for p in walk(DEMO):
        if p.suffix.lower() in {".mp4", ".mov", ".webm"}:
            files.append((p, f"demo/{p.name}"))

bad = []
for p, arc in files:
    if p.suffix.lower() in {".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg"}: continue
    try:
        if SECRET.search(p.read_text(encoding="utf-8", errors="ignore")): bad.append(arc)
    except Exception: pass
if bad: sys.exit(f"possible API key found in: {bad}")

target = ROOT / "submission.zip"
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
    for p, arc in files: z.write(p, arc)
size = target.stat().st_size
print(f"{target}  {size/1024/1024:.2f} MB")
with zipfile.ZipFile(target) as z:
    for n in z.namelist(): print("  ", n)
if size > LIMIT: sys.exit("ZIP is over 15 MB: shrink the demo video")
if not any(n.startswith("demo/") for n in zipfile.ZipFile(target).namelist()): print("note: no demo video included")
print("Now open the ZIP yourself and check it before uploading.")
