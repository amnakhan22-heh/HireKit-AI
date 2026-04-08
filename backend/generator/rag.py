import json
import os
from pathlib import Path

import chromadb
from openai import OpenAI


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

    Applies metadata filters for role_level and industry before running cosine
    similarity, so results are always contextually appropriate before ranking.
    Falls back to unfiltered search if no metadata matches are found.
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    query_text = f"{role_title} {role_level} {industry} {role_description}"
    query_embedding = _embed_texts(openai_client, [query_text])[0]

    metadata_filter = _build_metadata_filter(role_level, industry)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        where=metadata_filter if metadata_filter else None,
    )

    if not results["documents"][0]:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n,
        )
    return results["documents"][0]


def _build_metadata_filter(role_level: str, industry: str) -> dict:
    """Build a ChromaDB $and filter for role_level and industry when both are present."""
    conditions = []
    if role_level:
        conditions.append({"role_level": {"$eq": role_level}})
    if industry:
        conditions.append({"industry": {"$eq": industry}})

    if len(conditions) == 2:
        return {"$and": conditions}
    if len(conditions) == 1:
        return conditions[0]
    return {}


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


def _embed_texts(openai_client: OpenAI, texts: list) -> list:
    """Return a list of embedding vectors for the given texts using a single API call."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]
