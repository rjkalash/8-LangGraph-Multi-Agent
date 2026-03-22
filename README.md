# LangGraph Multi-Agent RAG System

## Project Overview
I have built the requested Multi-Agent RAG system using an orchestrator-based LangGraph architecture with a FastAPI backend and a Next.js (React/Tailwind) frontend.

## Key Features Implemented

### 1. RAG Backbone
- **Vector DB:** Integrated with ChromaDB.
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` for semantic search.
- **Hybrid Search:** Combined semantic vector search with keyword/text search using `BM25`.
- **Reranker:** Integrated a HuggingFace Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) to re-rank the retrieved documents and boost relevance.
- **Ingestion:** Created a script (`backend/scripts/ingest.py`) with hierarchical-like recursive chunking and tested it with sample Markdown data (simulating Stack Exchange/Documentation).

### 2. Multi-Agent Workflow
We used `langgraph` to build a stateful sequence of agents:
- **Orchestrator Agent:** Analyzes the initial query. Defaults to determining if retrieval is needed or if it should reply directly. Formats the query for optimal searching.
- **Retriever Agent:** Executes the Hybrid Search mechanism.
- **Reranker Agent:** Grades retrieved context and keeps the top relevant chunks using the cross-encoder. 
- **Validator Agent:** An LLM-based agent that strictly evaluates if the context directly answers the user's question and checks for hallucinations. If invalid, triggers a retry loop back to the Orchestrator with a refined query.
- **Web Search Agent:** Uses DuckDuckGo search integration to fetch real-time facts from the public internet when the frontend toggle is activated. Bypasses internal Vector DB limits.
- **Summarizer Agent:** Generates the final, structured answer solely using the verified context.

### 3. Backend (FastAPI)
- Exposes `POST /query`, `GET /status/{query_id}`, and `GET /history/{user_id}` routes.
- Runs the LangGraph invocation as an asynchronous background task so long-running LLM inferences do not block the HTTP threads.
- Enables CORS for local frontend communication.

### 4. Frontend (Next.js)
- A modern UI built with Next.js App Router and Tailwind CSS.
- Implemented real-time polling to fetch intermediate `status` and display the **Reasoning Trace** of the agents.
- Shows dynamic loaders ("Agents are thinking...") while the backend calculates the response.

## Validation & Usage
1. Both the backend and frontend are currently running.
2. The frontend is accessible at: `http://localhost:3001`
3. You can submit queries such as *"Summarize all security audit findings related to 'OAuth token leakage incidents' and suggest mitigations."* using the sample data that was ingested, and watch the agents retrieve, rerank, and validate the context before answering.
