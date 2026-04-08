import json
import os
from pathlib import Path

import chromadb
from openai import OpenAI

from .prompts import QUERY_EXPANSION_PROMPT


KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge_base.json"
CHROMA_DB_PATH = str(Path(__file__).parent.parent / "chroma_db")
COLLECTION_NAME = "interview_questions"


def initialize_knowledge_base() -> None:
    """Embed all knowledge base questions and store them in ChromaDB.

    Skips initialization silently if the collection already contains data,
    so it is safe to call on every server startup.
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    if collection.count() > 0:
        return
    _populate_collection(collection)


def retrieve_relevant_questions(
    role_title: str,
    role_description: str,
    role_level: str,
    industry: str,
    n: int = 10,
) -> list:
    """Return the n most semantically relevant questions for the given role.

    Uses pure cosine similarity against the expanded query — no metadata
    filters. The knowledge base is organized by industry domain (e.g. Finance
    = accounting questions), not by role function (e.g. Product Manager). Hard
    filtering by industry or role_level would exclude competency-based questions
    (prioritization, stakeholder management) that are relevant to any role but
    happen to be tagged under a different industry. Semantic search handles
    relevance; the LLM adapts the retrieved questions to the specific role.
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    expanded_query = _expand_query(openai_client, role_title, role_description, role_level, industry)
    query_embedding = _embed_texts(openai_client, [expanded_query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
    )
    return results["documents"][0]


def _populate_collection(collection) -> None:
    """Load knowledge_base.json, embed all questions, and upsert into the collection."""
    with open(KNOWLEDGE_BASE_PATH, "r") as knowledge_file:
        questions = json.load(knowledge_file)

    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    ids, embeddings, documents, metadatas = _build_collection_data(
        openai_client, questions
    )
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )


def _build_collection_data(openai_client, questions: list) -> tuple:
    """Return (ids, embeddings, documents, metadatas) tuples ready for ChromaDB."""
    texts = [item["question"] for item in questions]
    embeddings = _embed_texts(openai_client, texts)
    ids = [str(index) for index in range(len(questions))]
    metadatas = [
        {
            "industry": item["industry"],
            "role_level": item["role_level"],
            "type": item["type"],
            "tags": ",".join(item["tags"]),
        }
        for item in questions
    ]
    return ids, embeddings, texts, metadatas


def _expand_query(
    openai_client: OpenAI,
    role_title: str,
    role_description: str,
    role_level: str,
    industry: str,
) -> str:
    """Use gpt-4o-mini to expand the role context into a keyword-rich search query."""
    prompt = QUERY_EXPANSION_PROMPT.format(
        role_level=role_level or "Not specified",
        industry=industry or "Not specified",
        role_description=f"{role_title} {role_description}".strip(),
    )
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def _embed_texts(openai_client: OpenAI, texts: list) -> list:
    """Return a list of embedding vectors for the given texts using a single API call."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]
