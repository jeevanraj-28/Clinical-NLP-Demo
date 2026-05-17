import re
from typing import Dict, List

import streamlit as st
from transformers import pipeline


st.set_page_config(
    page_title="Clinical NLP Demo",
    layout="wide",
)


@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


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


def make_summary(note: str) -> str:
    words = note.split()
    if len(words) < 35:
        return note.strip()

    summarizer = load_summarizer()
    result = summarizer(note, max_length=80, min_length=20, do_sample=False)
    return result[0]["summary_text"].strip()


def render_section(title: str, values: List[str]) -> None:
    with st.container(border=True):
        st.subheader(title)
        if values:
            for value in values:
                st.write(f"- {value}")
        else:
            st.caption("No clear mention detected in the note.")


st.markdown(
    """
    <style>
      .main { background: #0b1120; }
      .block-container { padding-top: 2rem; padding-bottom: 2rem; }
      h1, h2, h3, p, li, label, .stMarkdown { color: #e5e7eb; }
      [data-testid="stTextArea"] textarea {
        background: #111827;
        color: #f8fafc;
        border: 1px solid #334155;
      }
      [data-testid="stMetricValue"] { color: #38bdf8; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Clinical NLP Demo")
st.caption("Public demo for structuring fake doctor notes. Not for real patient data or clinical decision-making.")

sample_note = (
    "Patient complains of chest pain and mild shortness of breath. "
    "Likely acid reflux after initial assessment. Prescribed aspirin 75 mg and antacid. "
    "Follow up in 2 weeks and return earlier if symptoms worsen."
)

note = st.text_area(
    "Doctor voice note text",
    value=sample_note,
    height=180,
    placeholder="Paste a fake doctor note here...",
)

col_a, col_b, col_c = st.columns([1, 1, 2])
with col_a:
    structure = st.button("Structure Note", type="primary", use_container_width=True)
with col_b:
    clear = st.button("Use Sample", use_container_width=True)

if clear:
    note = sample_note

if structure or note:
    clean_note = note.strip()
    if not clean_note:
        st.warning("Enter a fake clinical note to continue.")
    else:
        sections = extract_section(clean_note)
        summary = make_summary(clean_note)

        st.divider()

        left, right = st.columns(2)
        with left:
            render_section("Chief Complaint", sections["Chief Complaint"])
            render_section("Diagnosis", sections["Diagnosis"])
        with right:
            render_section("Medications", sections["Medications"])
            render_section("Follow-up Plan", sections["Follow-up Plan"])

        with st.container(border=True):
            st.subheader("Summary")
            st.write(summary)

st.divider()
st.caption(
    "Model: sshleifer/distilbart-cnn-12-6 for lightweight summarization. "
    "Extraction uses transparent rule-based parsing to avoid private healthcare IP."
)
