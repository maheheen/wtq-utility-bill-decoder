"""Golden test: live model call on KESC_0008. Strings exact, numbers within +-1."""
import json
from pathlib import Path

import pytest

from src.config import ROOT, load_config
from src.extract import extract_l1

IMAGE = ROOT.parent / "data" / "train" / "bills" / "KESC_0008.png"
GOLDEN = Path(__file__).parent / "golden" / "KESC_0008.json"


def diff(got, want, path=""):
    if isinstance(want, dict):
        return [d for k in want for d in diff(got.get(k), want[k], f"{path}.{k}")]
    if isinstance(want, list):
        if not isinstance(got, list) or len(got) != len(want):
            return [f"{path}: {got!r} != {want!r}"]
        return [d for i, (g, w) in enumerate(zip(got, want)) for d in diff(g, w, f"{path}[{i}]")]
    if isinstance(want, (int, float)) and isinstance(got, (int, float)):
        return [] if abs(got - want) <= 1 else [f"{path}: {got!r} != {want!r}"]
    return [] if got == want else [f"{path}: {got!r} != {want!r}"]


@pytest.mark.skipif(not IMAGE.exists(), reason="train bill not found")
def test_kesc_0008():
    got = extract_l1(IMAGE, load_config())
    assert diff(got, json.loads(GOLDEN.read_text(encoding="utf-8"))) == []
