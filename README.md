<div align="center">

  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=28&duration=2500&pause=800&color=38BDF8&center=true&vCenter=true&width=700&lines=%F0%9F%A9%BA+Clinical+NLP+Demo" alt="Header" />

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
    <img src="https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" />
    <img src="https://img.shields.io/badge/Model-DistilBART-111827?style=for-the-badge" />
    <img src="https://img.shields.io/github/last-commit/jeevanraj-28/Clinical-NLP-Demo?style=for-the-badge" />
  </p>

  <p><i>A public Streamlit demo that structures synthetic doctor voice notes into organized clinical sections using open-source NLP — no API keys, no private data, no proprietary models.</i></p>

</div>

---

## 🎯 What It Does

Paste or type a **simulated doctor's dictation** (e.g., post-visit notes), and the app instantly structures it into:

| Section | Example Output |
|---|---|
| **Chief Complaint** | "Patient complains of chest pain and mild shortness of breath" |
| **Diagnosis** | "Likely acid reflux after initial assessment" |
| **Medications** | "Prescribed aspirin 75 mg and antacid" |
| **Follow-up Plan** | "Follow up in 2 weeks, return earlier if symptoms worsen" |
| **Summary** | Auto-generated summary using DistilBART |

> ⚠️ **This is a portfolio demo only.** Do not enter real patient data. This is not a medical device.

---

## 🧠 How It Works

```text
Doctor's Voice Note (text input)
        │
        ▼
┌─────────────────────────┐
│  Rule-Based Extraction  │──→ Chief Complaint, Diagnosis,
│  (keyword matching)     │    Medications, Follow-up Plan
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│  DistilBART Summarizer  │──→ Auto-generated Summary
│  (sshleifer/distilbart) │    (for notes > 35 words)
└─────────────────────────┘
        │
        ▼
   Structured Clinical Output
```

### Model Choice: `sshleifer/distilbart-cnn-12-6`
- ✅ Runs without any API key
- ✅ Lightweight enough for Hugging Face Spaces free CPU tier
- ✅ Good at summarizing clinical-style text
- ✅ Transparent and easy to explain in interviews

The structured field extraction uses **rule-based keyword matching** — intentionally transparent so the demo is safe for public hosting and does not include any proprietary healthcare logic.

---

## 🏗️ Architecture

| Component | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Interactive UI with dark theme |
| NLP Extraction | Rule-based (regex + keywords) | Classify sentences into clinical sections |
| Summarization | `sshleifer/distilbart-cnn-12-6` | Auto-summarize longer notes |
| Hosting | Hugging Face Spaces (free CPU) | Public deployment |

---

## ▶️ Run Locally

```bash
git clone https://github.com/jeevanraj-28/Clinical-NLP-Demo.git
cd Clinical-NLP-Demo
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🚀 Deploy on Hugging Face Spaces

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **Create new Space**
3. Configure:
   - **Space name:** `Clinical-NLP-Demo`
   - **SDK:** Streamlit
   - **Visibility:** Public
   - **Hardware:** Free CPU
4. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `README.md` (or the HF-specific metadata below)
5. Your Space will be live at:

```
https://huggingface.co/spaces/YOUR_USERNAME/Clinical-NLP-Demo
```

### Hugging Face Space Metadata (add to top of README.md in the Space)

```yaml
---
title: Clinical NLP Demo
emoji: 🩺
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: false
license: mit
---
```

---

## 📋 Sample Inputs to Try

```
Patient complains of chest pain and mild shortness of breath.
Likely acid reflux after initial assessment. Prescribed aspirin
75 mg and antacid. Follow up in 2 weeks and return earlier if
symptoms worsen.
```

```
45 year old male presents with persistent cough for 3 weeks,
low grade fever. Suspected upper respiratory infection.
Started antibiotic course amoxicillin 500mg three times daily.
Continue paracetamol for fever. Review in 5 days, refer to
pulmonologist if no improvement.
```

```
Patient complains of recurring headache and dizziness for the
past month. Blood pressure elevated at 150/95. Diagnosed with
stage 1 hypertension. Prescribed amlodipine 5mg daily and
lifestyle modifications. Monitor blood pressure daily. Follow
up in 4 weeks.
```

---

## 🔒 Safety & Ethics

- This demo processes **only fake/synthetic clinical notes**
- No real patient data should ever be entered
- No Kinetrix company IP, private models, or proprietary logic is used
- All models are publicly available on Hugging Face
- The keyword extraction is intentionally transparent and auditable
- This is **not** a medical device and must not be used for clinical decision-making

---

## 🔮 Future Improvements

- Replace rule-based extraction with a fine-tuned NER model (e.g., BioBERT for medical entities)
- Add ICD-10 code suggestions based on extracted diagnosis
- Support audio input with Whisper transcription → structured output
- Add confidence scores for each extracted section
- Support multi-language clinical notes

---

## 👨‍💻 Author

**Jeevan Raj M**  
AI/ML Engineer | Clinical NLP | Computer Vision  
B.E. Artificial Intelligence & Data Science, University of Mysore School of Engineering

[LinkedIn](https://linkedin.com/in/jeevan-raj-m-5ba64a383) · [GitHub](https://github.com/jeevanraj-28) · [Email](mailto:jeevanrajm2882004@gmail.com)
