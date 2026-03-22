# Digital Persona — Project Write-up

## What I Built

A chatbot that lets you explore someone's professional profile through 
conversation. You paste a LinkedIn URL (and optionally a Twitter handle), 
and the system scrapes their public data, builds a knowledge base, and 
lets you ask questions about them in a multi-turn chat interface.

---

## Architecture
```
LinkedIn URL + Twitter Handle (optional)
          ↓
    Apify Scrapers
    (no credentials needed, zero ban risk)
          ↓
    Structured Text (knowledge base)
          ↓
    Chunking → Embeddings → FAISS Index
          ↓
    User Query → Retrieve relevant chunks
          ↓
    Groq LLM (llama-3.3-70b-versatile)
          ↓
    Grounded, data-driven answer
```

---

## Why RAG?

Two reasons. First, LinkedIn profiles can be verbose — experience, 
posts, education, skills all add up quickly. Stuffing everything into 
a single prompt risks hitting token limits and gets expensive. Second, 
and more importantly, RAG forces the model to answer from retrieved 
context rather than its training data. That's the difference between 
"what does GPT think Bill Gates does" and "what does Bill Gates' 
actual profile say." For a tool like this, that distinction matters a lot.

---

## Data Extraction — The Hard Part

Honestly, this was the trickiest piece. LinkedIn actively blocks 
scrapers — official APIs are too restrictive, and rolling your own 
Selenium scraper risks getting your account banned within hours.

After evaluating a few options, I landed on Apify's 
`apimaestro/linkedin-profile-detail` actor. The key reason: it 
requires no LinkedIn credentials at all. You just pass a profile URL 
and it returns structured JSON — name, headline, experience, education, 
featured posts, everything. Zero ban risk since your account is never 
in the picture.

For Twitter, I used Apify's `apidojo/tweet-scraper` with the profile 
URL as input, limiting to 10 recent tweets to keep costs minimal. 
The tweet data gets merged into the same knowledge base as LinkedIn, 
so the RAG pipeline doesn't need to change at all.

---

## Design Decisions

**FAISS over a hosted vector DB** — For a project at this scale, 
spinning up Pinecone or Weaviate would be overkill. FAISS runs 
locally, has zero cost, and is fast enough for knowledge bases of 
this size. If this were handling hundreds of profiles simultaneously, 
I'd reconsider.

**Groq over OpenAI** — Groq's inference speed is genuinely impressive. 
Answers come back in under a second, which makes the chat feel 
responsive rather than laggy. The free tier was also a practical 
consideration given the timeline.

**SentenceTransformers for embeddings** — `all-MiniLM-L6-v2` is small, 
fast, and good enough for semantic similarity over profile text. No API 
calls needed, no cost per embedding.

**Streamlit for UI** — Given a 2-day deadline, Streamlit was the right 
call. It handles session state, chat UI, and sidebar layout cleanly 
without needing to build a frontend from scratch.

---

## Error Handling

- Invalid LinkedIn URLs are caught before any API call is made
- Private profiles return a clear message rather than a silent failure
- Twitter errors are non-fatal — the app continues with LinkedIn only
- Rate limits and timeouts are handled with polling + fallback messages
- All LLM errors are caught at the UI level

---

## What I'd Add With More Time

User authentication and profile saving. Right now every session 
starts fresh — you paste a URL, wait for scraping, and lose 
everything on refresh. With auth, you could save profiles, build 
a library of personas, and return to previous conversations. That 
would make this genuinely useful beyond a demo.

I'd also improve the chunking strategy. Right now it's a flat 
recursive split. Smarter chunking — keeping experience entries 
together, not splitting mid-sentence — would improve retrieval 
quality noticeably.

---

## Stack Summary

| Component | Tool |
|---|---|
| UI | Streamlit |
| LLM | Groq (llama-3.3-70b-versatile) |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| Vector Store | FAISS |
| LinkedIn Scraping | Apify (apimaestro/linkedin-profile-detail) |
| Twitter Scraping | Apify (apidojo/tweet-scraper) |
| Text Splitting | LangChain RecursiveCharacterTextSplitter |