"""Streamlit front end for the clinical note structurer.

Run:  streamlit run app.py
"""
import json
from pathlib import Path

import streamlit as st

from clinical_nlp import extract
from clinical_nlp.summarizer import (
    model_available,
    model_summary,
    structured_summary,
    unsupported_numbers,
)

ROOT = Path(__file__).resolve().parent
CORE_SECTIONS = ("Chief Complaint", "Diagnosis", "Medications", "Follow-up Plan")

st.set_page_config(page_title="Clinical NLP Demo", page_icon="🩺", layout="wide")


@st.cache_data
def load_samples() -> dict[str, str]:
    """Example notes from the development set (synthetic, never real patients)."""
    path = ROOT / "data" / "dev_notes.jsonl"
    samples = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            note = json.loads(line)
            samples[f"{note['id']}: {note['note'][:60]}..."] = note["note"]
    return samples


def render_section(title: str, values: list[str]) -> None:
    with st.container(border=True):
        st.subheader(title)
        if values:
            for value in values:
                st.markdown(f"- {value}")
        else:
            st.caption("Nothing detected.")


st.title("Clinical NLP Demo")
st.caption(
    "Turns a synthetic doctor's dictation into structured sections and a medication list. "
    "Portfolio demo only: do not enter real patient data. Not a medical device."
)

samples = load_samples()
choice = st.selectbox("Load an example note", list(samples), index=0)
note = st.text_area("Dictation text", value=samples[choice], height=170)

summary_options = ["Structured (from extracted fields)"]
if model_available():
    summary_options.append("Model (DistilBART)")
summary_mode = st.radio("Summary type", summary_options, horizontal=True)

if st.button("Structure note", type="primary"):
    text = note.strip()
    if not text:
        st.warning("Enter a synthetic clinical note first.")
        st.stop()

    result = extract(text)
    st.divider()

    left, right = st.columns(2)
    for column, titles in ((left, CORE_SECTIONS[:2]), (right, CORE_SECTIONS[2:])):
        with column:
            for title in titles:
                render_section(title, result.sections[title])

    with st.container(border=True):
        st.subheader("Medication list")
        if result.medications:
            st.table([{"Drug": m.name, "Dose": m.dose or "not stated", "Status": m.status}
                      for m in result.medications])
        else:
            st.caption("No medications detected.")

    extra_left, extra_right = st.columns(2)
    with extra_left:
        render_section("Negated findings", result.sections["Negated Findings"])
    with extra_right:
        render_section("Advice and other findings",
                       result.sections["Advice"] + result.sections["Other Findings"])

    with st.container(border=True):
        st.subheader("Summary")
        if summary_mode.startswith("Model"):
            with st.spinner("Running DistilBART (the first run downloads about 1 GB)..."):
                summary = model_summary(text)
        else:
            summary = structured_summary(result)
        st.write(summary)
        invented = unsupported_numbers(summary, text)
        if invented:
            st.error(f"The summary contains numbers that are not in the note: {', '.join(invented)}. "
                     "Check doses and durations before relying on it.")
        else:
            st.caption("Check passed: every number in the summary appears in the note.")

    with st.expander("Why was each sentence put where it is?"):
        st.table([{"Text": clause, "Section": section, "Rule that fired": rule}
                  for clause, section, rule in result.trace])

st.divider()
st.caption("Extraction: transparent rules in clinical_nlp/. Evaluation: python evaluate.py. "
           "Source: github.com/jeevanraj-28/Clinical-NLP-Demo")
