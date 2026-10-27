# Study Sathi AI 📚

**An AI-powered study assistant to help students learn from their own study materials.**

## About the Project

Study Sathi AI is a small project I started to explore how AI can be used to make studying easier for students.

The idea is simple: students often have to go through long PDFs and notes to find the information they need. I wanted to build a tool where students can upload their study materials and get help understanding them without having to search through every page manually.

This project is still in its early stage, and I am working on improving it as I learn more about Python and AI.

## What it can do

- **Upload PDFs:** Add your study materials in PDF format.
- **Find relevant information:** Search through the uploaded content to find passages related to a question.
- **Show source passages:** See the parts of the document that are relevant to your query.
- **View similarity scores:** Get an idea of how closely the retrieved passages match your question.
- **Summaries and flashcard prompts:** Use the available features to make revision easier.
- **AI-generated answers:** The project includes an optional Google Gemini integration, which I am still working on.

## How it works

The project uses Python and Streamlit for the application, along with text extraction and TF-IDF-based retrieval to find relevant parts of uploaded documents.

When a student asks a question, the application searches the document for passages that match the question. It can then show the relevant text to help the student find the information they need.

I have also tried integrating Google Gemini to make the answers more useful and conversational. However, that integration is not fully working yet, so the project currently relies on document retrieval and fallback behaviour when AI generation is unavailable.

## Technologies Used

- **Python** — Main programming language
- **Streamlit** — Web application interface
- **TF-IDF** — Finding relevant passages in documents
- **PDF text extraction** — Reading uploaded study materials
- **Google Gemini API** — Optional AI-generated responses (still being worked on)
- **Git and GitHub** — Version control and project hosting

## Current Status

Study Sathi AI is currently a **working prototype**, not a finished product.

The basic idea of uploading PDFs and retrieving relevant passages is implemented. I have also worked on features to support summaries and flashcard-style revision.

The main limitation right now is the Gemini integration. I am getting a client error when trying to generate AI responses, and I have not confirmed the exact cause yet. It could be related to the API key, model access, quota, or API configuration, so I still need to investigate it.

Until that is resolved, the project should not be considered a fully working AI chatbot. The document retrieval part can still be useful on its own.

## Running the Project Locally

If you want to try the project on your computer:

1. Clone this repository:

   ```bash
   git clone <your-repository-url>
   ```

2. Open the project folder:

   ```bash
   cd <repository-folder>
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the Streamlit application:

   ```bash
   streamlit run app.py
   ```

These commands assume the repository contains `requirements.txt` and the main application file is named `app.py`. Change the command if your actual filenames are different.

If you want to test Gemini features, you will also need a valid API key and the configuration expected by the application. Keep your API key private and never commit it to GitHub.

## What I Want to Improve Next

- Fix the Gemini API integration.
- Improve the quality of answers generated from uploaded documents.
- Make summaries and flashcards more useful for revision.
- Improve error handling and the overall user interface.
- Test the application with different PDFs and questions.
- Make the project more reliable and easier for other students to use.

## What I Learned

Building this project has helped me understand how document retrieval works, how to build a simple application with Streamlit, and how to connect an application to an AI API.

I also learned that integrating an AI model is not always as simple as calling an API. Configuration, API access, error handling, and testing are important parts of building a working application.

I took some help from AI tools while learning, understanding errors, and working through implementation problems. I am still learning and improving the project step by step.

## Note

This is an educational project that I am building as a learning experience. It may contain bugs, and some features are still under development.

The goal is to keep learning, improve the prototype, and eventually make Study Sathi AI a useful study tool for students.

---

**Made as a learning project by a student, with the goal of making studying a little easier.**
