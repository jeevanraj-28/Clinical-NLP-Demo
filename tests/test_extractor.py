"""Unit tests for the clinical note extractor.

Run from the repository root (no ML libraries needed):
    python -m unittest discover -s tests -v
"""
import json
import unittest
from pathlib import Path

from clinical_nlp import extract, extract_section
from clinical_nlp.extractor import classify, split_clauses
from clinical_nlp.summarizer import structured_summary, unsupported_numbers

ROOT = Path(__file__).resolve().parents[1]


class SplitClausesTests(unittest.TestCase):
    def test_decimal_doses_are_not_split(self):
        self.assertIn("Colchicine 0.5 mg twice daily", split_clauses("Acute gout. Colchicine 0.5 mg twice daily."))

    def test_blood_pressure_is_not_split(self):
        self.assertEqual(split_clauses("Blood pressure 150/95."), ["Blood pressure 150/95"])

    def test_numeric_continuation_joins_previous_fragment(self):
        clauses = split_clauses("Prednisolone 2.5 mg tablets, 4 tablets daily for 5 days.")
        self.assertEqual(clauses, ["Prednisolone 2.5 mg tablets, 4 tablets daily for 5 days"])

    def test_commas_split_separate_findings(self):
        self.assertEqual(split_clauses("Cough for 3 weeks, low grade fever."),
                         ["Cough for 3 weeks", "low grade fever"])


class ClassifyTests(unittest.TestCase):
    def assertSection(self, clause, section):
        self.assertEqual(classify(clause)[0], section, clause)

    def test_negation(self):
        for clause in ("No fever", "Denies chest pain", "X-ray shows no fracture", "Without vomiting"):
            self.assertSection(clause, "Negated Findings")

    def test_complaints(self):
        self.assertSection("Patient complains of chest pain", "Chief Complaint")
        self.assertSection("Elderly male with swelling of both ankles", "Chief Complaint")
        self.assertSection("Patient has dry cough after starting enalapril", "Chief Complaint")

    def test_diagnosis(self):
        self.assertSection("Suspected dengue fever", "Diagnosis")
        self.assertSection("Plantar fasciitis", "Diagnosis")

    def test_medication(self):
        self.assertSection("Paracetamol 650 mg three times daily", "Medications")
        self.assertSection("Ibuprofen syrup 5 ml for pain", "Medications")

    def test_lab_values_are_not_medications(self):
        self.assertSection("Fasting sugar 182 mg/dl today", "Other Findings")

    def test_follow_up_beats_advice(self):
        self.assertSection("Maintain a headache diary and review in 4 weeks", "Follow-up Plan")

    def test_advice_is_not_a_medication(self):
        self.assertSection("Avoid ibuprofen", "Advice")


class MedicationTests(unittest.TestCase):
    def test_name_and_dose(self):
        meds = extract("Started amoxicillin 500mg three times daily.").medications
        self.assertEqual([(m.name, m.dose) for m in meds], [("amoxicillin", "500 mg")])

    def test_two_drugs_in_one_sentence(self):
        meds = extract("Amoxicillin 500 mg and metronidazole 400 mg for 5 days.").medications
        self.assertEqual({m.name: m.dose for m in meds}, {"amoxicillin": "500 mg", "metronidazole": "400 mg"})

    def test_later_instruction_overrides_earlier(self):
        meds = extract("On metformin 500 mg. Increase metformin to 1000 mg.").medications
        self.assertEqual([(m.name, m.dose) for m in meds], [("metformin", "1000 mg")])

    def test_stopped_drug(self):
        meds = {m.name: m.status for m in extract("Stop enalapril. Switch to losartan 50 mg.").medications}
        self.assertEqual(meds, {"enalapril": "stopped", "losartan": "active"})

    def test_unknown_drug_before_dose(self):
        meds = extract("Prescribed zentoprazine 20 mg once daily.").medications
        self.assertEqual([(m.name, m.dose) for m in meds], [("zentoprazine", "20 mg")])


class SummaryTests(unittest.TestCase):
    def test_structured_summary_uses_only_note_content(self):
        note = "Patient complains of fever. Suspected malaria. Paracetamol 650 mg. Review in 3 days."
        summary = structured_summary(extract(note))
        self.assertTrue(summary.startswith("Presents with fever."))
        self.assertEqual(unsupported_numbers(summary, note), [])

    def test_unsupported_number_is_flagged(self):
        self.assertEqual(unsupported_numbers("amoxicillin 500 mg", "amoxicillin 250 mg"), ["500"])


class RegressionTests(unittest.TestCase):
    """Guards against a rule change that quietly makes the test-set score worse."""

    def test_test_set_micro_f1(self):
        tp = items = found = gold_total = 0
        for line in (ROOT / "data" / "test_notes.jsonl").read_text(encoding="utf-8").splitlines():
            note = json.loads(line)
            predicted = extract_section(note["note"])
            for section, gold in note["gold"].items():
                got = [i.lower() for i in predicted[section]]
                gold = [g.lower() for g in gold]
                items += len(got)
                gold_total += len(gold)
                tp += sum(any(g in i for g in gold) for i in got)
                found += sum(any(g in i for i in got) for g in gold)
        precision, recall = tp / items, found / gold_total
        self.assertGreaterEqual(2 * precision * recall / (precision + recall), 0.95)


if __name__ == "__main__":
    unittest.main()
