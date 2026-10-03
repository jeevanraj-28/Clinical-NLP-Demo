"""Version 2 rule-based extractor for synthetic clinical dictations.

Pipeline
    1. Split the note into clauses without breaking numbers ("2.5 mg", "150/95").
    2. Put each clause into exactly ONE section using ordered rules
       (negation first, then follow-up, advice, presentation, diagnosis,
       medication, measurements, symptoms, conditions).
    3. Pull structured medications (name, dose, status) out of the
       Medications clauses.

Everything is deterministic and explainable: `explain(note)` returns the rule
that fired for every clause.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import lexicon as lx

SECTIONS = (
    "Chief Complaint",
    "Diagnosis",
    "Medications",
    "Follow-up Plan",
    "Negated Findings",
    "Advice",
    "Other Findings",
)

DOSE_UNITS = r"(?:mg|mcg|µg|g|ml|iu|units?|puffs?|drops?|sprays?|tablets?|caps?(?:ules?)?)"
NUMBER_WORDS = r"(?:one|two|three|four|five|half)"
DOSE_PATTERN = re.compile(
    rf"\b(?:\d+(?:\.\d+)?|{NUMBER_WORDS})\s?{DOSE_UNITS}\b(?!\s?/\s?(?:dl|l)\b)",
    re.IGNORECASE,
)
# Lab values and vital signs: "182 mg/dl", "150/95", "101 F", "8.2 g/dl".
MEASUREMENT_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:mg/dl|g/dl|mmol/l|mmhg|°?\s?[fc]\b|%)|\b\d{2,3}/\d{2,3}\b|\b\d+\.\d+\b",
    re.IGNORECASE,
)


@dataclass
class Medication:
    name: str
    dose: str = ""
    status: str = "active"  # "active" or "stopped"
    source: str = ""        # the clause it came from


@dataclass
class Extraction:
    sections: dict[str, list[str]] = field(default_factory=lambda: {s: [] for s in SECTIONS})
    medications: list[Medication] = field(default_factory=list)
    trace: list[tuple[str, str, str]] = field(default_factory=list)  # (clause, section, rule)


# --------------------------------------------------------------------------- helpers
def _has_word(text: str, words) -> bool:
    """True if any word or phrase in `words` occurs in `text` as whole words."""
    return any(re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", text) for w in words)


def _starts_with(text: str, words) -> bool:
    return any(re.match(rf"{re.escape(w)}(?![\w-])", text) for w in words)


def split_clauses(note: str) -> list[str]:
    """Split on sentence ends, semicolons, new lines and commas, but never inside a
    number. A comma fragment that starts with a digit ("4 tablets daily") is
    joined back to the previous fragment because it continues it."""
    sentences = re.split(r"\.(?!\d)|;|\n+", note)  # "2.5 mg" stays whole; "150/95. Next" splits
    clauses: list[str] = []
    for sentence in sentences:
        parts = [p.strip() for p in re.split(r",(?!\d)", sentence)]
        for position, part in enumerate(parts):
            if not part:
                continue
            if clauses and position > 0 and re.match(r"\d", part):
                clauses[-1] = f"{clauses[-1]}, {part}"
            else:
                clauses.append(part)
    return clauses


def classify(clause: str) -> tuple[str, str]:
    """Return (section, rule) for one clause. Rules are checked in order."""
    text = clause.lower().strip()
    text = re.sub(r"^(assessment|impression|diagnosis|plan)\s*:\s*", r"\1 ", text)

    if _starts_with(text, lx.NEGATION_START) or _has_word(text, lx.NEGATION_INNER):
        return "Negated Findings", "negation cue"
    if _has_word(text, lx.FOLLOW_UP_CUES):
        return "Follow-up Plan", "follow-up cue"
    if _starts_with(text, lx.ADVICE_CUES) or re.search(r"\badvised\b", text):
        return "Advice", "advice cue"
    person_with = re.match(
        rf"^(?:\d+\s+year\s+old\s+)?(?:[a-z]+\s+){{0,2}}(?:{'|'.join(lx.PERSON_WORDS)})\s+(?:with|has|presents)\b",
        text,
    )
    if _has_word(text, lx.PRESENTATION_CUES) or person_with:
        return "Chief Complaint", "presentation cue"
    if _has_word(text, lx.DIAGNOSIS_CUES):
        return "Diagnosis", "diagnosis cue"
    if (_has_word(text, lx.DRUGS) or DOSE_PATTERN.search(text) or _has_word(text, lx.FORMULATIONS)
            or (_starts_with(text, lx.MEDICATION_VERBS) and _has_word(text, lx.MEDICATION_WORDS))):
        return "Medications", "drug, dose or formulation"
    if MEASUREMENT_PATTERN.search(text):
        return "Other Findings", "measurement"
    if _has_word(text, lx.SYMPTOMS):
        return "Chief Complaint", "symptom word"
    if _has_word(text, lx.CONDITIONS) or any(re.search(rf"\w{s}\b", text) for s in lx.CONDITION_SUFFIXES):
        return "Diagnosis", "condition name"
    return "Other Findings", "no rule matched"


def extract_medications(clause: str) -> list[Medication]:
    """Find drug names and doses in one Medications clause."""
    text = clause.lower()
    stopped = _starts_with(text.strip(), lx.STOP_VERBS)
    found: list[tuple[int, str]] = []
    for drug in sorted(lx.DRUGS, key=len, reverse=True):  # longest first: "oral rehydration solution" before "ors"
        for match in re.finditer(rf"(?<![\w-]){re.escape(drug)}(?![\w-])", text):
            if not any(start <= match.start() < start + len(name) for start, name in found):
                found.append((match.start(), drug))
    # Unknown drug: the word right before a dose ("xyzomab 20 mg"), or before a formulation word.
    if not found:
        match = DOSE_PATTERN.search(text) or re.search(
            rf"\b({'|'.join(map(re.escape, lx.FORMULATIONS))})\b", text)
        if match:
            # Formulation and route words ("inhaler", "eye", "drops") are never the drug name itself.
            not_names = set(lx.MEDICATION_VERBS) | set(lx.FORMULATIONS) | {
                "with", "then", "after", "eye", "ear", "nasal", "oral", "topical", "course"}
            before = [w for w in re.findall(r"[a-z][a-z-]{3,}", text[:match.start()]) if w not in not_names]
            if before:
                found.append((text.find(before[-1]), before[-1]))
    found.sort()
    meds = []
    for i, (start, name) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else len(text)
        dose_match = DOSE_PATTERN.search(text, start, end)
        dose = ""
        if dose_match:
            dose = re.sub(r"(\d)\s?([a-z])", r"\1 \2", dose_match.group(0)).strip()
        meds.append(Medication(name=name, dose=dose, status="stopped" if stopped else "active",
                               source=clause.strip()))
    return meds


def extract(note: str) -> Extraction:
    result = Extraction()
    by_name: dict[str, Medication] = {}
    for clause in split_clauses(note):
        section, rule = classify(clause)
        result.sections[section].append(clause)
        result.trace.append((clause, section, rule))
        if section == "Medications":
            for med in extract_medications(clause):
                by_name[med.name] = med  # a later instruction for the same drug overrides an earlier one
    result.medications = list(by_name.values())
    return result


def extract_section(note: str) -> dict[str, list[str]]:
    """Same interface as the version 1 baseline: the four core sections only."""
    sections = extract(note).sections
    return {s: sections[s] for s in ("Chief Complaint", "Diagnosis", "Medications", "Follow-up Plan")}


def explain(note: str) -> list[tuple[str, str, str]]:
    """(clause, section, rule) for every clause, for debugging and the UI."""
    return extract(note).trace
