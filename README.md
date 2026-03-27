# 🧠 LangGraph Multi-Agent RAG System

> 🚀 Production-grade Retrieval-Augmented Generation (RAG) system powered by multi-agent orchestration, hybrid search, and real-time validation

---

## 🌟 Key Highlights

* 🤖 **Multi-Agent Architecture** using LangGraph for reasoning workflows
* 🔍 **Hybrid Retrieval** (Vector + BM25) for high recall
* 🎯 **Cross-Encoder Reranking** for precision improvement
* 🔁 **Self-Healing Loop** with validation + query refinement
* 🌐 **Web Search Integration** for real-time knowledge
* ⚡ **Async FastAPI Backend** with non-blocking execution
* 💻 **Next.js Frontend** with live reasoning trace

---

## 🧠 Problem Statement

Traditional RAG systems:

* Retrieve irrelevant chunks
* Hallucinate when context is weak
* Lack validation mechanisms

👉 This system solves:

* Retrieval accuracy
* Context validation
* Multi-step reasoning

---

## 🏗️ System Architecture

```text
User Query
    ↓
Orchestrator Agent
    ↓
Retriever Agent (Hybrid Search: Vector + BM25)
    ↓
Reranker Agent (Cross-Encoder)
    ↓
Validator Agent (LLM-based evaluation)
    ├── Invalid → Query Refinement Loop
    └── Valid → Summarizer Agent
            ↓
        Final Answer

(Optional)
    ↓
Web Search Agent (DuckDuckGo)
```

---

## 🔍 RAG Pipeline

### Retrieval Layer

* **Vector DB:** ChromaDB
* **Embeddings:** all-MiniLM-L6-v2
* **Keyword Search:** BM25
* **Chunking:** Recursive + hierarchical strategy

### Ranking Layer

* **Cross-Encoder:** `ms-marco-MiniLM-L-6-v2`
* Improves semantic relevance significantly

### Validation Layer

* LLM-based context validation
* Detects hallucination risk
* Triggers retry loop with refined query

---

## 🤖 Multi-Agent Workflow

| Agent        | Responsibility                |
| ------------ | ----------------------------- |
| Orchestrator | Query planning + routing      |
| Retriever    | Hybrid document retrieval     |
| Reranker     | Context scoring               |
| Validator    | Quality + hallucination check |
| Web Search   | External knowledge retrieval  |
| Summarizer   | Final answer generation       |

---

## ⚙️ Tech Stack

| Layer         | Technology         |
| ------------- | ------------------ |
| Orchestration | LangGraph          |
| Backend       | FastAPI (Async)    |
| Frontend      | Next.js + Tailwind |
| Vector DB     | ChromaDB           |
| Embeddings    | HuggingFace        |
| Reranker      | Cross-Encoder      |
| Search        | BM25 + DuckDuckGo  |

---

## 🚀 Backend Features

* `POST /query` → Execute RAG pipeline
* `GET /status/{query_id}` → Real-time progress
* `GET /history/{user_id}` → Query history

👉 Uses async background tasks for scalability

---

## 💻 Frontend Features

* Real-time **Reasoning Trace**
* Agent-level visibility
* Dynamic loading states
* Toggle for web search

---

## 📊 Performance & Optimizations

* Hybrid search improves recall
* Reranking improves precision
* Validation reduces hallucination
* Async execution avoids blocking

---

## 🧪 Example Query

```text
Summarize all security audit findings related to OAuth token leakage and suggest mitigations
```

---

## 🔮 Future Improvements

* Add **vector DB scaling (Pinecone / Weaviate)**
* Implement **semantic caching (Redis)**
* Add **evaluation metrics (RAGAS / TruLens)**
* Streaming responses
* Multi-user session memory

---

## 📂 Project Structure

```text
project/
├── backend/
│   ├── agents/
│   ├── scripts/
│   ├── api/
├── frontend/
│   ├── app/
│   ├── components/
```

---

## 👤 Author

**Raj Kalash Tiwari**
GitHub: https://github.com/rjkalash

---

## 📈 Status

✅ Advanced RAG system with multi-agent reasoning
⚡ Designed for scalable AI applications

---

⭐ Star this repo if you found it useful!
