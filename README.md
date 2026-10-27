# StudySathi AI

An independent student-built study assistant prototype. Upload text-based PDF notes, ask questions, retrieve relevant passages, summarize notes, and create study prompts.

## Features
- PDF text extraction with `pypdf`
- Text chunking and keyword-based retrieval with TF-IDF and cosine similarity
- Optional grounded answer generation using the Gemini API
- Extractive-summary fallback if no API key is configured
- Simple flashcard prompts and Streamlit interface
- Explicit source inspection and limitations

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   streamlit run app.py
   ```
5. Open the local URL shown in your terminal.

The app works in retrieval-only mode without an API key. To enable generated answers, create a Gemini API key from Google AI Studio and set an environment variable named `GEMINI_API_KEY`. Never commit your key to GitHub.

## Deploy publicly on Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. Sign in to Streamlit Community Cloud using GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Deploy. The first build may take a few minutes.
5. Optional: in your app's **Settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "paste-your-own-key-here"
   ```
6. Reboot the app after changing secrets.

Provider quotas, eligibility, model availability, and free-tier limits may change. Check the current terms before relying on an API in a public demo.

## Important limitations
- Scanned/image-only PDFs are not OCR-processed.
- TF-IDF retrieval is keyword-based and may miss related passages.
- Generated answers can be incorrect even when source excerpts are provided.
- The app is a learning prototype; it should not be used as an authority for high-stakes advice.
- Avoid uploading confidential or copyrighted materials without permission.

## Evaluation plan
Before presenting this as a portfolio project, test with at least 15–20 questions:
- questions answered clearly by the document
- questions with partially relevant information
- questions absent from the notes

Record whether the correct passage appears in the top results and note failure cases. Do not claim performance figures you have not measured.

## Attribution
This is an independent educational project using open-source Python libraries. It is inspired by the general category of study-assistant tools and does not use another product's branding or proprietary code.
