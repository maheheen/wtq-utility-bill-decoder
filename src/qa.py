"""Level 2: one call per bill answers all questions as JSON keyed by question_id."""
import json
import logging

from src import llm
from src.config import ModelCfg

log = logging.getLogger(__name__)

FALLBACK = "I could not determine this from the bill reliably, so I cannot give a confident answer."

SYSTEM = """You answer customer questions about ONE electricity bill (K-Electric, LESCO or IESCO) in plain English.

You get JSON with: bill (the Level 1 fields as printed), extras (usage history, payment history, printed split, slab lines, notes read from the bill), facts (numbers computed by code, authoritative) and questions (id and text).

RULES
- Answer in English only, even if the bill has Urdu.
- Ground every answer in the given data. Do not use outside tariff, rate, regulatory or company knowledge.
- Numbers must be right. Use the numbers in facts for averages, differences, counts, percentages and shares. Do not do your own arithmetic when facts has the value. Quote printed values from bill and extras as they are.
- If a needed value is null, missing, or not in the data, say plainly that the bill does not show it. Never invent a value.
- Label estimates as estimates and say how they were calculated.
- If a question is ambiguous, state the meaning you used or answer both meanings.
- Negative amounts are credits. Say so.
- Write amounts as PKR with thousands separators (PKR 3,430.24). Name the months and amounts that matter. Be specific and concise, 1 to 4 sentences per answer.
- Never output personal identifiers (names, addresses, CNIC, account, reference, consumer or meter numbers).
- Return a JSON object whose keys are exactly the question ids, each with a non-empty string answer.

STYLE EXAMPLES
"Taxes and duties total PKR 569.62 out of your current bill of PKR 3,430.24, or about 16.6%. The bill shows a split of 83.39% energy charges and 16.61% taxes. The tax lines are sales tax (PKR 520.21), electricity duty (PKR 29.41), and MUCT (KMC) (PKR 20.00)."
"Two of the 12 previous months exceeded 200 units: July 2025 (239) and August 2025 (203). The current month used 151 units, so the count is two whether or not the current month is included."
"""


def _ok(answer) -> bool:
    return isinstance(answer, str) and bool(answer.strip())


def _ask(cfg: ModelCfg, l1: dict, extras: dict, facts: dict, questions: list[tuple[str, str]]) -> dict:
    payload = {"bill": l1, "extras": extras, "facts": facts,
               "questions": [{"id": qid, "question": text} for qid, text in questions]}
    schema = {"type": "object",
              "properties": {qid: {"type": "string"} for qid, _ in questions},
              "required": [qid for qid, _ in questions]}
    try:
        out = llm.call(cfg, SYSTEM, json.dumps(payload, sort_keys=True, ensure_ascii=False), None, schema)
        return out if isinstance(out, dict) else {}
    except Exception as e:  # network, quota, bad JSON after retries
        log.warning("qa call failed: %s: %s", type(e).__name__, str(e)[:200])
        return {}


def answer_bill(cfg: ModelCfg, l1: dict, extras: dict, facts: dict, questions: list[tuple[str, str]]) -> dict[str, str]:
    """Never returns an empty answer: missing ones are retried once, then get an honest fallback."""
    answers = _ask(cfg, l1, extras, facts, questions)
    missing = [q for q in questions if not _ok(answers.get(q[0]))]
    if missing:
        log.warning("retrying %d missing answers", len(missing))
        answers = {**answers, **{k: v for k, v in _ask(cfg, l1, extras, facts, missing).items() if _ok(v)}}
    return {qid: answers[qid].strip() if _ok(answers.get(qid)) else FALLBACK for qid, _ in questions}
