"""Two ways to summarise a note, plus a safety check.

structured_summary  Builds the summary from the extracted sections. Every word
                    comes from the note, so it cannot invent a drug or a dose.
model_summary       Abstractive summary with sshleifer/distilbart-cnn-12-6
                    (needs `transformers` and `torch`). Fluent, but the model
                    was trained on news articles and can drop or change details.
unsupported_numbers Numbers in a summary that do not appear in the note. A dose
                    or duration that the model made up shows up here.
"""
from __future__ import annotations

import re
from functools import lru_cache

from .extractor import Extraction

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"
MIN_WORDS_FOR_MODEL = 35


def structured_summary(extraction: Extraction) -> str:
    s = extraction.sections
    parts = []
    if s["Chief Complaint"]:
        parts.append("Presents with " + "; ".join(_strip_lead_in(x) for x in s["Chief Complaint"]) + ".")
    if s["Negated Findings"]:
        parts.append("Negatives: " + "; ".join(_lower_first(x) for x in s["Negated Findings"]) + ".")
    if s["Diagnosis"]:
        parts.append("Assessment: " + "; ".join(_lower_first(x) for x in s["Diagnosis"]) + ".")
    active = [m for m in extraction.medications if m.status == "active"]
    stopped = [m for m in extraction.medications if m.status == "stopped"]
    if active:
        parts.append("Medications: " + ", ".join(f"{m.name} {m.dose}".strip() for m in active) + ".")
    if stopped:
        parts.append("Stopped: " + ", ".join(m.name for m in stopped) + ".")
    if s["Follow-up Plan"]:
        parts.append("Plan: " + "; ".join(_lower_first(x) for x in s["Follow-up Plan"]) + ".")
    return " ".join(parts) or "No structured content detected."


LEAD_IN = re.compile(
    r"^(?:\d+\s+year\s+old\s+)?(?:[a-z]+\s+){0,2}?"
    r"(?:patient|male|female|man|woman|child|toddler|teenager|boy|girl|infant)?\s*"
    r"(?:complains of|complaining of|presents with|presented with|reports|has|with|brought with)\s+",
    re.IGNORECASE,
)


def _strip_lead_in(text: str) -> str:
    """'Patient complains of chest pain' -> 'chest pain'."""
    return _lower_first(LEAD_IN.sub("", text.strip(), count=1))


def _lower_first(text: str) -> str:
    text = text.strip()
    return text[:1].lower() + text[1:] if text[:2] != text[:2].upper() else text


@lru_cache(maxsize=1)
def _load_model():
    from transformers import pipeline  # imported lazily: the rest of the package needs no ML libraries

    return pipeline("summarization", model=MODEL_NAME)


def model_available() -> bool:
    try:
        import transformers  # noqa: F401
        import torch  # noqa: F401
    except ImportError:
        return False
    return True


def model_summary(note: str) -> str:
    if len(note.split()) < MIN_WORDS_FOR_MODEL:
        return note.strip()
    result = _load_model()(note, max_length=80, min_length=20, do_sample=False)
    return result[0]["summary_text"].strip()


def unsupported_numbers(summary: str, note: str) -> list[str]:
    """Numbers (with their unit, if any) in the summary that the note never mentions."""
    def numbers(text: str) -> set[str]:
        return {n.replace(",", "") for n in re.findall(r"\d+(?:[.,]\d+)?", text)}

    in_note = numbers(note)
    return sorted(n for n in numbers(summary) if n not in in_note)
