# Clinical NLP Demo

A public, lightweight Streamlit demo that structures fake doctor notes into clinical sections:

- Chief Complaint
- Diagnosis
- Medications
- Follow-up Plan
- Summary

This project is intentionally built with public open-source tools and simple transparent parsing. It does **not** include Kinetrix company IP, private healthcare data, hospital workflows, or proprietary model logic.

## Model Choice

Recommended free model:

```text
sshleifer/distilbart-cnn-12-6
```

Why this model:

- runs without an API key
- lightweight enough for Hugging Face Spaces CPU
- useful for summarizing longer notes
- simple to explain in interviews

The structured field extraction is rule-based so the demo remains transparent and safe for public hosting.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

For macOS/Linux:

```bash
source .venv/bin/activate
```

## Deploy on Hugging Face Spaces

1. Go to `https://huggingface.co/spaces`.
2. Click `Create new Space`.
3. Space name: `Clinical-NLP-Demo`.
4. SDK: `Streamlit`.
5. Visibility: `Public`.
6. Hardware: free CPU.
7. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `README.md`
8. Commit the files.
9. Open the Space URL:

```text
https://huggingface.co/spaces/jeevanraj-28/Clinical-NLP-Demo
```

## Safety Note

This demo is for portfolio and educational use only. Do not enter real patient information. It is not a medical device and must not be used for diagnosis or treatment.
