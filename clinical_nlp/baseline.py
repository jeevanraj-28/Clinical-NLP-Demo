"""Version 1 extractor: the original keyword rules, kept unchanged as a baseline.

Every comma/period/semicolon fragment is checked against four keyword lists and
can land in several sections at once. Kept so evaluate.py can compare it with
the current extractor on the same test set.
"""
from typing import Dict, List

import re


def split_items(text: str) -> List[str]:
    parts = re.split(r"[,.;\n]+", text)
    return [part.strip() for part in parts if part.strip()]


def contains_any(text: str, keywords: List[str]) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def extract_section(note: str) -> Dict[str, List[str]]:
    items = split_items(note)

    sections = {
        "Chief Complaint": [],
        "Diagnosis": [],
        "Medications": [],
        "Follow-up Plan": [],
    }

    complaint_keywords = [
        "complains",
        "complaint",
        "pain",
        "fever",
        "cough",
        "breath",
        "nausea",
        "vomiting",
        "headache",
        "dizziness",
        "fatigue",
    ]
    diagnosis_keywords = [
        "diagnosed",
        "diagnosis",
        "suspected",
        "likely",
        "assessment",
        "impression",
        "infection",
        "hypertension",
        "diabetes",
        "asthma",
    ]
    medication_keywords = [
        "prescribed",
        "started",
        "continue",
        "aspirin",
        "paracetamol",
        "ibuprofen",
        "metformin",
        "antibiotic",
        "tablet",
        "mg",
        "medication",
    ]
    followup_keywords = [
        "follow up",
        "follow-up",
        "review",
        "return",
        "revisit",
        "refer",
        "weeks",
        "days",
        "month",
        "monitor",
    ]

    for item in items:
        if contains_any(item, complaint_keywords):
            sections["Chief Complaint"].append(item)
        if contains_any(item, diagnosis_keywords):
            sections["Diagnosis"].append(item)
        if contains_any(item, medication_keywords):
            sections["Medications"].append(item)
        if contains_any(item, followup_keywords):
            sections["Follow-up Plan"].append(item)

    if not sections["Chief Complaint"] and items:
        sections["Chief Complaint"].append(items[0])

    return sections
