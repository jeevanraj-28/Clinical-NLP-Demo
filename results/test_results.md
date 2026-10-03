## Results on the test set (20 notes)

| Section | v1 precision | v1 recall | v1 F1 | v2 precision | v2 recall | v2 F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Chief Complaint | 0.47 | 0.74 | 0.57 | 0.95 | 1.00 | 0.97 |
| Diagnosis | 0.94 | 0.80 | 0.86 | 1.00 | 0.90 | 0.95 |
| Medications | 0.77 | 0.75 | 0.76 | 0.96 | 1.00 | 0.98 |
| Follow-up Plan | 0.56 | 0.91 | 0.69 | 0.95 | 1.00 | 0.98 |
| **Micro average** | 0.64 | 0.80 | 0.71 | 0.97 | 0.98 | 0.97 |

Negated findings listed as complaints: v1 6 of 9, v2 0 of 9.

| Medication extraction (v2) | Value |
| --- | --- |
| Drug name precision | 1.00 |
| Drug name recall | 1.00 (26 of 26) |
| Drug name F1 | 1.00 |
| Dose accuracy (on found drugs) | 1.00 |
