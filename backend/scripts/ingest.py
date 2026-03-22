import os
import sys
import time
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from langchain_community.document_loaders import WikipediaLoader, ArxivLoader, WebBaseLoader, YoutubeLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.vectorstore import get_vectorstore

def load_stack_exchange():
    print("Fetching from StackExchange API (Security)...")
    docs = []
    # Fetch top 5 questions tagged with 'oauth' from Information Security SE
    url = "https://api.stackexchange.com/2.3/questions?order=desc&sort=votes&tagged=oauth&site=security&filter=withbody"
    try:
        res = requests.get(url).json()
        for item in res.get("items", [])[:3]:
            content = item.get("body_markdown", item.get("body", ""))
            title = item.get("title", "")
            docs.append(Document(page_content=f"Title: {title}\n\n{content}", metadata={"source": "StackExchange", "title": title}))
        time.sleep(1)
    except Exception as e:
        print(f"StackExchange failed: {e}")
    return docs

def load_git_repos():
    print("Cloning and processing Git repositories...")
    import os
    from pathlib import Path
    
    repos = {
        "langchain": "https://github.com/langchain-ai/langchain",
        "fastapi": "https://github.com/tiangolo/fastapi",
        "qdrant": "https://github.com/qdrant/qdrant"
    }
    
    docs = []
    os.makedirs("docs", exist_ok=True)
    
    for name, url in repos.items():
        repo_path = f"docs/{name}"
        if not os.path.exists(repo_path):
            print(f"Cloning {name}...")
            os.system(f"git clone --depth 1 {url} {repo_path}")
            
    print("Extracting markdown from repos...")
    for md_file in Path("docs").rglob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            docs.append(Document(page_content=content, metadata={"source": f"GitHub", "repo": name, "file": str(md_file)}))
        except Exception:
            pass
    return docs

def load_arxiv_advanced():
    print("Fetching advanced papers from ArXiv...")
    docs = []
    try:
        import arxiv
        client = arxiv.Client()
        search = arxiv.Search(
            query="cat:cs.CR OR cat:cs.LG OR (RAG AND security)",
            max_results=50, # Limited from 5000 to 50 for realistic embedding times
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        for paper in client.results(search):
            content = f"Title: {paper.title}\nAuthors: {', '.join(a.name for a in paper.authors)}\nAbstract:\n{paper.summary}"
            docs.append(Document(page_content=content, metadata={"source": "ArXiv", "id": paper.entry_id}))
    except Exception as e:
        print(f"ArXiv advanced failed: {e}")
    return docs

def load_wikipedia_security():
    print("Fetching Wikipedia Security Categories...")
    docs = []
    security_categories = [
        "Cybersecurity",
        "OAuth",
        "General Data Protection Regulation",
        "Data breach",
        "Information security"
    ]
    for topic in security_categories:
        try:
            loader = WikipediaLoader(query=topic, load_max_docs=1)
            docs.extend(loader.load())
            time.sleep(1)
        except Exception as e:
            print(f"Failed to load Wiki {topic}: {e}")
    return docs

def load_youtube():
    print("Fetching YouTube Transcripts...")
    from langchain_community.document_loaders import YoutubeLoader
    docs = []
    video_urls = [
        "https://www.youtube.com/watch?v=zjkBMFhNj_g" # GPT Intro - Karpathy
    ]
    for url in video_urls:
        try:
            loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
            docs.extend(loader.load())
        except Exception as e:
            print(f"YouTube failed for {url}: {e}")
    return docs

def load_web_docs():
    print("Fetching Open Source Documentation...")
    from langchain_community.document_loaders import WebBaseLoader
    try:
        # LangGraph docs
        loader = WebBaseLoader("https://python.langchain.com/docs/langgraph")
        return loader.load()
    except Exception as e:
        print(f"Web docs failed: {e}")
        return []

def load_sample_docs():
    print("Fetching local sample_docs.md...")
    import json
    docs = []
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_docs.md")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return docs
        
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(" | ")
        if len(parts) >= 5:
            doc_id, doc_type, title, content, meta_str = parts[0], parts[1], parts[2], parts[3], parts[4]
            try:
                metadata = json.loads(meta_str)
            except:
                metadata = {}
            metadata["source"] = "sample_docs"
            metadata["doc_type"] = doc_type
            metadata["title"] = title
            
            full_content = f"Title: {title}\n\n{content}"
            docs.append(Document(page_content=full_content, metadata=metadata))
            
    return docs

def ingest():
    all_docs = []
    
    # 0. Local Sample Docs
    all_docs.extend(load_sample_docs())
    
    # 1. Stack Exchange
    all_docs.extend(load_stack_exchange())
    
    # 2. Advanced ArXiv Search
    all_docs.extend(load_arxiv_advanced())
    
    # 3. YouTube Transcripts
    all_docs.extend(load_youtube())
    
    # 4. Open Source Docs
    all_docs.extend(load_web_docs())
    
    # 5. Wikipedia Security Categories
    all_docs.extend(load_wikipedia_security())
    
    # 6. GitHub Repos (Langchain, FastAPI, Qdrant)
    all_docs.extend(load_git_repos())

    print(f"Total RAW documents gathered: {len(all_docs)}")
    
    # Split
    print("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(all_docs)
    
    # Clean metadatas and assign IDs
    for i, split in enumerate(splits):
        split.metadata["id"] = f"mixed_{i}"
        safe_meta = {}
        for k, v in split.metadata.items():
             if isinstance(v, (str, int, float, bool)):
                 safe_meta[k] = v
             else:
                 safe_meta[k] = str(v)
        split.metadata = safe_meta
    
    # Store
    print(f"Ingesting {len(splits)} chunks into ChromaDB...")
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents=splits)
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest()
