## Results on the dev set (10 notes)

| Section | v1 precision | v1 recall | v1 F1 | v2 precision | v2 recall | v2 F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Chief Complaint | 0.77 | 0.92 | 0.84 | 1.00 | 1.00 | 1.00 |
| Diagnosis | 1.00 | 0.50 | 0.67 | 1.00 | 1.00 | 1.00 |
| Medications | 0.82 | 0.77 | 0.79 | 1.00 | 1.00 | 1.00 |
| Follow-up Plan | 0.67 | 1.00 | 0.80 | 1.00 | 1.00 | 1.00 |
| **Micro average** | 0.77 | 0.81 | 0.79 | 1.00 | 1.00 | 1.00 |

Negated findings listed as complaints: v1 1 of 5, v2 0 of 5.

| Medication extraction (v2) | Value |
| --- | --- |
| Drug name precision | 1.00 |
| Drug name recall | 1.00 (14 of 14) |
| Drug name F1 | 1.00 |
| Dose accuracy (on found drugs) | 1.00 |
