# 🧠 Digital Persona — AI Profile Chatbot

An AI-powered chatbot that lets you explore anyone's professional digital footprint through natural conversation. Input a LinkedIn profile URL and chat with their career data using RAG (Retrieval-Augmented Generation).

---

## 🎥 Demo Video
[Link to demo video] ← add this after recording

## 🌐 Live Deployment
(https://digital-persona-f5el2cmczdp8k53cszh38k.streamlit.app/)

---

## 🏗️ Architecture
```
LinkedIn URL
     ↓
Apify Scraper (no cookies, no login)
     ↓
Structured Text (knowledge base)
     ↓
Chunking (RecursiveCharacterTextSplitter)
     ↓
Embeddings (SentenceTransformers: all-MiniLM-L6-v2)
     ↓
FAISS Vector Index
     ↓
User Query → Retrieve top-k chunks → Groq LLM (llama-3.3-70b-versatile)
     ↓
Data-driven Answer (no hallucination)
```

---

## 🧰 Tech Stack

| Component | Tool |
|---|---|
| Frontend/UI | Streamlit |
| LLM | Groq (llama-3.3-70b-versatile) |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS |
| LinkedIn Scraping | Apify (apimaestro/linkedin-profile-detail) |
| Text Splitting | LangChain RecursiveCharacterTextSplitter |

---

## ⚙️ Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/digital-persona.git
cd digital-persona
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:
```env
APIFY_API_TOKEN=your_apify_token_here
GROQ_API_KEY=your_groq_key_here
```

### 5. Run the app
```bash
python -m streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🔑 API Keys Required

| Key | Where to get it | Cost |
|---|---|---|
| `APIFY_API_TOKEN` | [apify.com](https://apify.com) → Settings → API Tokens | Free tier ($5 credits) |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys | Free |

---

## 📁 Project Structure
```
digital-persona/
├── app.py                  # Streamlit UI
├── scraper/
│   ├── linkedin_scraper.py # Apify-based LinkedIn scraper
│   └── twitter_scraper.py  # Twitter/X scraper (optional)
├── rag/
│   ├── chunker.py          # Text chunking
│   ├── embedder.py         # FAISS index builder
│   ├── retriever.py        # Semantic search
│   └── chain.py            # Groq LLM chain
├── utils/
│   └── validators.py       # URL + input validation
├── .env                    # API keys (not committed)
├── requirements.txt
└── README.md
```

---

## 🛡️ Error Handling

- Invalid LinkedIn URL → user-friendly error message
- Private profile → graceful fallback message
- Empty data returned → handled with ValueError
- API rate limits → timeout handling with retries
- LLM errors → caught and displayed in UI

---

## 💡 Design Decisions

**Why RAG instead of full context injection?**
RAG scales better with larger profiles and prevents token limit issues. It also ensures answers are grounded in retrieved data, reducing hallucination.

**Why FAISS?**
Local, zero-cost, fast for small-to-medium knowledge bases. No external vector DB service needed.

**Why Groq?**
Extremely fast inference, free tier available, and llama-3.3-70b produces high quality answers comparable to GPT-4.

**Why Apify?**
No LinkedIn credentials required — zero ban risk. Reliable structured output.