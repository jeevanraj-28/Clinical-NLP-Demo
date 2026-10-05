"""Evaluate the extractors on a labelled set of synthetic notes.

    python evaluate.py                      # held-out test set, both versions
    python evaluate.py --split dev          # development set
    python evaluate.py --errors             # also print every mistake

Metrics (per section, then micro-averaged over the four core sections)
  precision  extracted items that contain a gold phrase for that section
             / all extracted items in that section
  recall     gold phrases found inside some extracted item of that section
             / all gold phrases
  F1         harmonic mean of precision and recall
Negation errors: a negated finding ("No fever") placed in Chief Complaint.
Medications (version 2 only): drug-name precision/recall, and dose accuracy on
correctly found drugs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_nlp import baseline, extractor

ROOT = Path(__file__).resolve().parent
CORE = ("Chief Complaint", "Diagnosis", "Medications", "Follow-up Plan")


def load(split: str) -> list[dict]:
    path = ROOT / "data" / f"{split}_notes.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def f1(p: float, r: float) -> float:
    return 2 * p * r / (p + r) if p + r else 0.0


def score_sections(notes, extract_fn):
    counts = {s: {"tp_items": 0, "items": 0, "found": 0, "gold": 0} for s in CORE}
    negation_errors, errors = 0, []
    for note in notes:
        predicted = extract_fn(note["note"])
        for section in CORE:
            items = [i.lower() for i in predicted.get(section, [])]
            gold = [g.lower() for g in note["gold"][section]]
            c = counts[section]
            c["items"] += len(items)
            c["gold"] += len(gold)
            for item in items:
                if any(g in item for g in gold):
                    c["tp_items"] += 1
                else:
                    errors.append((note["id"], section, "extra", item))
            for g in gold:
                if any(g in item for item in items):
                    c["found"] += 1
                else:
                    errors.append((note["id"], section, "missed", g))
        complaints = " | ".join(predicted.get("Chief Complaint", [])).lower()
        for neg in note.get("negated", []):
            if neg.lower() in complaints:
                negation_errors += 1
                errors.append((note["id"], "Chief Complaint", "negated finding listed as complaint", neg))
    rows = {}
    for section, c in counts.items():
        p = c["tp_items"] / c["items"] if c["items"] else 0.0
        r = c["found"] / c["gold"] if c["gold"] else 0.0
        rows[section] = (p, r, f1(p, r))
    tp = sum(c["tp_items"] for c in counts.values())
    items = sum(c["items"] for c in counts.values())
    found = sum(c["found"] for c in counts.values())
    gold = sum(c["gold"] for c in counts.values())
    p, r = tp / items, found / gold
    rows["Micro average"] = (p, r, f1(p, r))
    n_negated = sum(len(n.get("negated", [])) for n in notes)
    return rows, (negation_errors, n_negated), errors


def score_medications(notes):
    tp = predicted = gold = dose_correct = 0
    errors = []
    for note in notes:
        meds = [m for m in extractor.extract(note["note"]).medications if m.status == "active"]
        pred = {m.name: m.dose for m in meds}
        truth = {m["name"].lower(): m["dose"].lower() for m in note["meds"]}
        predicted += len(pred)
        gold += len(truth)
        for name, dose in pred.items():
            if name in truth:
                tp += 1
                if dose == truth[name]:
                    dose_correct += 1
                else:
                    errors.append((note["id"], "Medication dose", f"{name}: got '{dose}'", f"expected '{truth[name]}'"))
            else:
                errors.append((note["id"], "Medication name", "extra", name))
        for name in truth:
            if name not in pred:
                errors.append((note["id"], "Medication name", "missed", name))
    p, r = tp / predicted if predicted else 0.0, tp / gold if gold else 0.0
    return {"precision": p, "recall": r, "f1": f1(p, r), "dose_accuracy": dose_correct / tp if tp else 0.0,
            "found": tp, "gold": gold}, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["test", "dev"], default="test")
    parser.add_argument("--errors", action="store_true", help="print every mistake of version 2")
    parser.add_argument("--out", type=Path, default=None, help="write a Markdown report here")
    parser.add_argument("--unseen-drugs", action="store_true",
                        help="stress test: remove every drug in this split from the drug list first")
    args = parser.parse_args()

    notes = load(args.split)
    if args.unseen_drugs:
        from clinical_nlp import lexicon
        held_out = {m["name"].lower() for n in notes for m in n["meds"]}
        lexicon.DRUGS = tuple(d for d in lexicon.DRUGS if d not in held_out)
        print(f"Stress test: {len(held_out)} drug names removed from the drug list\n")
    v1, v1_neg, _ = score_sections(notes, baseline.extract_section)
    v2, v2_neg, v2_errors = score_sections(notes, extractor.extract_section)
    meds, med_errors = score_medications(notes)

    lines = [f"## Results on the {args.split} set ({len(notes)} notes)", "",
             "| Section | v1 precision | v1 recall | v1 F1 | v2 precision | v2 recall | v2 F1 |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for section in (*CORE, "Micro average"):
        a, b = v1[section], v2[section]
        name = f"**{section}**" if section == "Micro average" else section
        lines.append(f"| {name} | " + " | ".join(f"{x:.2f}" for x in (*a, *b)) + " |")
    lines += ["",
              f"Negated findings listed as complaints: v1 {v1_neg[0]} of {v1_neg[1]}, v2 {v2_neg[0]} of {v2_neg[1]}.",
              "",
              "| Medication extraction (v2) | Value |", "| --- | --- |",
              f"| Drug name precision | {meds['precision']:.2f} |",
              f"| Drug name recall | {meds['recall']:.2f} ({meds['found']} of {meds['gold']}) |",
              f"| Drug name F1 | {meds['f1']:.2f} |",
              f"| Dose accuracy (on found drugs) | {meds['dose_accuracy']:.2f} |", ""]
    report = "\n".join(lines)
    print(report)
    if args.errors:
        print("Version 2 mistakes:")
        for e in v2_errors + med_errors:
            print("  " + " | ".join(e))
    if args.out:
        args.out.write_text(report, encoding="utf-8")
        (args.out.with_suffix(".errors.json")).write_text(
            json.dumps([dict(zip(("note", "section", "type", "text"), e)) for e in v2_errors + med_errors], indent=2),
            encoding="utf-8")


if __name__ == "__main__":
    main()
