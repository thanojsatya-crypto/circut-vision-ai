# CircuitVision AI — Decoupled Edition

CircuitVision AI is an Electronics and Communication Engineering (ECE) assistant that operates as a **Design Engineer, Circuit Analyst, Lab Assistant, Troubleshooting Engineer, and Project Guide**. 

This repository is split into a **Streamlit Frontend Client** and a **FastAPI Backend RAG Server**.

---

## 🛠️ API Key Acquisition Tutorial

To run CircuitVision AI, you will need an API key from at least one of the supported providers: **Google Gemini**, **OpenRouter**, or **OpenAI**. Here is how to obtain them:

### 1. Google Gemini API Key (Direct)
This connects you directly to Google's official Gemini API.
1. Visit the **[Google AI Studio Platform](https://aistudio.google.com/)**.
2. Sign in using your standard Google/Gmail account.
3. Click the blue **"Create API key"** button in the left sidebar.
4. Click **"Create API key in new project"** (or select an existing Google Cloud project if you have one).
5. Copy the generated key. It will start with: **`AIzaSy...`**
6. *Note: Google AI Studio offers a free tier with rate limits, perfect for personal testing.*

### 2. OpenRouter API Key (Recommended for Multi-Model Access)
OpenRouter acts as a single gateway to access multiple LLMs (including Gemini, Llama, and GPT models).
1. Visit **[openrouter.ai](https://openrouter.ai/)**.
2. Sign up or log in (you can use your Google or GitHub account).
3. Click on your profile icon in the top right and select **"Keys"** (or go to `https://openrouter.ai/keys`).
4. Click **"Create Key"**.
5. Give the key a friendly name (e.g., `CircuitVision`) and click **"Create"**.
6. Copy the generated key. It will start with: **`sk-or-...`**
7. *Note: OpenRouter provides access to various free models (like `openrouter/free`), but paid models will require adding credits to your account.*

### 3. OpenAI API Key
This connects you to OpenAI's GPT models.
1. Visit the **[OpenAI Platform Dashboard](https://platform.openai.com/)**.
2. Create an account or log in.
3. In the left navigation bar, click on the **"API Keys"** icon (or go to `https://platform.openai.com/api-keys`).
4. Click **"Create new secret key"**.
5. Name your key (e.g., `CircuitVision`) and click **"Create secret key"**.
6. Copy the generated key. It will start with: **`sk-proj-...`** or **`sk-...`**
7. *Note: OpenAI requires pre-funding/adding credits to your account to use their API keys.*

---

## 🚀 Quick Local Launch

### Step 1: Start the Backend API (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Start the Frontend Client (Streamlit)
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## ☁️ Deployment Reference

* **Backend:** Deploy the `backend/` folder to **Railway** or **Render**. Ensure the start command is configured as:
  `uvicorn main:app --host 0.0.0.0 --port $PORT`
* **Frontend:** Deploy the `frontend/` folder to **Streamlit Community Cloud** pointing to `frontend/app.py` as the entry file.
