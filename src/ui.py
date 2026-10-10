"""Local web UI: python -m src.ui [--bills DIR] [--questions CSV] [--port N]
Upload a bill image (or pick a sample) and see Level 1 fields plus the Level 2 answers.
Uses the same pipeline as src.run, so results match the CSVs (and share the disk cache)."""
import argparse
import csv
import io
import json
import logging
import sys
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from PIL import Image

from src.config import CACHE_DIR, load_config
from src.extract import extract_extras, extract_l1
from src.facts import compute_facts
from src.qa import answer_bill
from src.run import EMPTY_EXTRAS, IMAGE_EXTS, process_bill

PAGE = Path(__file__).with_name("ui_page.html")
MAX_BYTES = 20 * 1024 * 1024
log = logging.getLogger("ui")


def load_questions(path: Path) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            seen.setdefault(r["question_id"], r["question"])
    return list(seen.items())


def ask(cfg, image: Path, question: str) -> dict:
    """Answer one free-text question about a bill, with the same rules and facts as Level 2.
    Level 1 and extras come from the disk cache when the bill was already decoded."""
    l1 = extract_l1(image, cfg)
    try:
        extras = extract_extras(image, cfg)
    except Exception as e:
        log.warning("extras failed: %s", type(e).__name__)
        extras = EMPTY_EXTRAS
    answers = answer_bill(cfg, l1, extras, compute_facts(l1, extras), [("Ask", question)])
    return {"question": question, "answer": answers["Ask"]}


def make_handler(cfg, questions, bills: Path):
    samples = sorted(p.name for p in bills.iterdir() if p.suffix.lower() in IMAGE_EXTS) if bills.is_dir() else []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # keep the terminal quiet
            pass

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, obj) -> None:
            self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path == "/":
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif path == "/api/samples":
                self._json(200, samples)
            elif path.startswith("/api/sample/"):
                name = path[len("/api/sample/"):]
                if name not in samples:  # only names from the listing, no path tricks
                    return self._json(404, {"error": "unknown sample"})
                ext = Path(name).suffix.lower().lstrip(".")
                ctype = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
                self._send(200, (bills / name).read_bytes(), ctype)
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):
            parsed = urlparse(self.path)
            route = parsed.path
            if route not in ("/api/decode", "/api/ask"):
                return self._json(404, {"error": "not found"})
            question = (parse_qs(parsed.query).get("q") or [""])[0].strip()
            if route == "/api/ask" and not 3 <= len(question) <= 500:
                return self._json(400, {"error": "Type a question (3 to 500 characters)."})
            size = int(self.headers.get("Content-Length") or 0)
            if not 0 < size <= MAX_BYTES:
                return self._json(413, {"error": "Image must be under 20 MB."})
            data = self.rfile.read(size)
            try:
                Image.open(io.BytesIO(data)).verify()
            except Exception:
                return self._json(400, {"error": "That file is not a readable image."})
            tmp = CACHE_DIR / "uploads" / f"{uuid.uuid4().hex}.img"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_bytes(data)
            started = time.time()
            if route == "/api/ask":
                try:
                    return self._json(200, ask(cfg, tmp, question))
                except Exception as e:
                    log.warning("ask failed: %s", type(e).__name__)
                    return self._json(500, {"error": "Could not answer that question."})
                finally:
                    tmp.unlink(missing_ok=True)
            try:
                l1, answers = process_bill(cfg, tmp, questions)
            except Exception as e:
                log.warning("decode failed: %s", type(e).__name__)
                return self._json(500, {"error": "Something went wrong while reading this bill."})
            finally:
                tmp.unlink(missing_ok=True)
            readable = any(v not in (None, []) for v in l1.values())
            self._json(200, {
                "ok": readable,
                "level1": l1,
                "answers": [{"id": qid, "question": text, "answer": answers[qid]} for qid, text in questions],
                "seconds": round(time.time() - started, 1),
            })

    return Handler


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bills", default="../data/test/bills", help="folder offered as sample bills")
    ap.add_argument("--questions", default="../data/test/csv/level2.csv", help="level2 template, source of the 12 questions")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s", stream=sys.stderr)
    log.setLevel(logging.INFO)

    try:
        questions = load_questions(Path(a.questions))
    except (OSError, KeyError) as e:
        print(f"Cannot read questions from {a.questions}: {e}. Pass --questions PATH to a level2 template.", file=sys.stderr)
        return 1
    cfg = load_config()
    server = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(cfg, questions, Path(a.bills)))
    url = f"http://127.0.0.1:{a.port}"
    log.info("Bill Decoder running at %s (Ctrl+C to stop), %d questions", url, len(questions))
    if not a.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
