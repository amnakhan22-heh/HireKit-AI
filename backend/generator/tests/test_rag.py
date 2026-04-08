"""Tests for the RAG (Retrieval-Augmented Generation) module.

All ChromaDB and OpenAI calls are mocked — no real API calls are made.
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from generator.rag import (
    _build_collection_data,
    _build_metadata_filter,
    _embed_texts,
    _populate_collection,
    initialize_knowledge_base,
    retrieve_relevant_questions,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_QUESTIONS = [
    {
        "question": "Tell me about a time you debugged a critical production issue.",
        "industry": "Tech",
        "role_level": "Mid-level",
        "type": "behavioral",
        "tags": ["debugging", "ownership"],
    },
    {
        "question": "How would you design a rate-limiting system at scale?",
        "industry": "Tech",
        "role_level": "Senior",
        "type": "technical",
        "tags": ["system design", "scalability"],
    },
]


def _make_mock_openai_client(embedding_vector=None):
    """Return a mock OpenAI client whose embeddings.create returns predictable data."""
    if embedding_vector is None:
        embedding_vector = [0.1, 0.2, 0.3]

    mock_embedding = MagicMock()
    mock_embedding.embedding = embedding_vector

    mock_response = MagicMock()
    mock_response.data = [mock_embedding, mock_embedding]

    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = mock_response
    return mock_client


# ---------------------------------------------------------------------------
# _embed_texts
# ---------------------------------------------------------------------------

class TestEmbedTexts:
    def test_returns_list_of_embeddings(self):
        mock_client = _make_mock_openai_client([0.5, 0.6, 0.7])
        result = _embed_texts(mock_client, ["hello", "world"])
        assert result == [[0.5, 0.6, 0.7], [0.5, 0.6, 0.7]]

    def test_calls_embeddings_create_with_correct_model(self):
        mock_client = _make_mock_openai_client()
        _embed_texts(mock_client, ["test text"])
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input=["test text"],
        )


# ---------------------------------------------------------------------------
# _build_collection_data
# ---------------------------------------------------------------------------

class TestBuildCollectionData:
    def test_returns_correct_structure(self):
        mock_client = _make_mock_openai_client([0.1, 0.2])
        ids, embeddings, documents, metadatas = _build_collection_data(
            mock_client, SAMPLE_QUESTIONS
        )
        assert ids == ["0", "1"]
        assert len(embeddings) == 2
        assert documents == [q["question"] for q in SAMPLE_QUESTIONS]
        assert metadatas[0]["industry"] == "Tech"
        assert metadatas[0]["role_level"] == "Mid-level"
        assert metadatas[0]["type"] == "behavioral"
        assert metadatas[0]["tags"] == "debugging,ownership"

    def test_tags_joined_as_comma_string(self):
        mock_client = _make_mock_openai_client()
        _, _, _, metadatas = _build_collection_data(mock_client, SAMPLE_QUESTIONS)
        assert "," in metadatas[1]["tags"]


# ---------------------------------------------------------------------------
# _populate_collection
# ---------------------------------------------------------------------------

class TestPopulateCollection:
    def test_calls_collection_add_with_correct_args(self, tmp_path):
        kb_path = tmp_path / "knowledge_base.json"
        kb_path.write_text(json.dumps(SAMPLE_QUESTIONS))

        mock_collection = MagicMock()
        mock_client = _make_mock_openai_client()

        with (
            patch("generator.rag.KNOWLEDGE_BASE_PATH", kb_path),
            patch("generator.rag.OpenAI", return_value=mock_client),
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
        ):
            _populate_collection(mock_collection)

        mock_collection.add.assert_called_once()
        call_kwargs = mock_collection.add.call_args.kwargs
        assert call_kwargs["ids"] == ["0", "1"]
        assert len(call_kwargs["embeddings"]) == 2
        assert len(call_kwargs["documents"]) == 2


# ---------------------------------------------------------------------------
# initialize_knowledge_base
# ---------------------------------------------------------------------------

class TestInitializeKnowledgeBase:
    def test_skips_population_when_collection_already_has_items(self):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 80

        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        with (
            patch("generator.rag.chromadb.PersistentClient", return_value=mock_chroma_client),
            patch("generator.rag._populate_collection") as mock_populate,
        ):
            initialize_knowledge_base()

        mock_populate.assert_not_called()

    def test_populates_collection_when_empty(self, tmp_path):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0

        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        with (
            patch("generator.rag.chromadb.PersistentClient", return_value=mock_chroma_client),
            patch("generator.rag._populate_collection") as mock_populate,
        ):
            initialize_knowledge_base()

        mock_populate.assert_called_once_with(mock_collection)

    def test_creates_collection_with_cosine_space(self):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 5

        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        with (
            patch("generator.rag.chromadb.PersistentClient", return_value=mock_chroma_client),
            patch("generator.rag._populate_collection"),
        ):
            initialize_knowledge_base()

        mock_chroma_client.get_or_create_collection.assert_called_once_with(
            name="interview_questions",
            metadata={"hnsw:space": "cosine"},
        )


# ---------------------------------------------------------------------------
# retrieve_relevant_questions
# ---------------------------------------------------------------------------

class TestRetrieveRelevantQuestions:
    def test_returns_list_of_question_strings(self):
        expected_questions = [
            "Tell me about a time you debugged a production issue.",
            "How would you design a scalable API?",
        ]
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [expected_questions]}

        mock_chroma_client = MagicMock()
        mock_chroma_client.get_collection.return_value = mock_collection

        mock_openai_client = _make_mock_openai_client([0.1, 0.2, 0.3])
        # query calls embed_texts with a single text — response.data must have one item
        single_embedding = MagicMock()
        single_embedding.embedding = [0.1, 0.2, 0.3]
        single_response = MagicMock()
        single_response.data = [single_embedding]
        mock_openai_client.embeddings.create.return_value = single_response

        with (
            patch("generator.rag.chromadb.PersistentClient", return_value=mock_chroma_client),
            patch("generator.rag.OpenAI", return_value=mock_openai_client),
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
        ):
            result = retrieve_relevant_questions(
                role_title="Software Engineer",
                role_description="Build backend services",
                role_level="Senior",
                industry="Tech",
                n=2,
            )

        assert result == expected_questions

    def test_passes_n_results_to_collection_query(self):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [["q1", "q2", "q3"]]}

        mock_chroma_client = MagicMock()
        mock_chroma_client.get_collection.return_value = mock_collection

        single_embedding = MagicMock()
        single_embedding.embedding = [0.1]
        single_response = MagicMock()
        single_response.data = [single_embedding]

        mock_openai_client = MagicMock()
        mock_openai_client.embeddings.create.return_value = single_response

        with (
            patch("generator.rag.chromadb.PersistentClient", return_value=mock_chroma_client),
            patch("generator.rag.OpenAI", return_value=mock_openai_client),
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
        ):
            retrieve_relevant_questions(
                role_title="",
                role_description="Finance analyst",
                role_level="Junior",
                industry="Finance",
                n=3,
            )

        mock_collection.query.assert_called_once()
        call_kwargs = mock_collection.query.call_args.kwargs
        assert call_kwargs["n_results"] == 3

    def test_builds_query_from_all_role_fields(self):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]]}

        mock_chroma_client = MagicMock()
        mock_chroma_client.get_collection.return_value = mock_collection

        single_embedding = MagicMock()
        single_embedding.embedding = [0.0]
        single_response = MagicMock()
        single_response.data = [single_embedding]

        mock_openai_client = MagicMock()
        mock_openai_client.embeddings.create.return_value = single_response

        with (
            patch("generator.rag.chromadb.PersistentClient", return_value=mock_chroma_client),
            patch("generator.rag.OpenAI", return_value=mock_openai_client),
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
        ):
            retrieve_relevant_questions(
                role_title="Data Analyst",
                role_description="Analyse financial reports",
                role_level="Mid-level",
                industry="Finance",
            )

        create_call = mock_openai_client.embeddings.create.call_args
        query_text = create_call.kwargs["input"][0]
        assert "Data Analyst" in query_text
        assert "Finance" in query_text
        assert "Mid-level" in query_text
        assert "Analyse financial reports" in query_text


# ---------------------------------------------------------------------------
# _format_reference_questions (lives in services.py but tested here for cohesion)
# ---------------------------------------------------------------------------

class TestFormatReferenceQuestions:
    def test_numbers_questions_correctly(self):
        from generator.services import _format_reference_questions

        result = _format_reference_questions(["Question A", "Question B"])
        assert result == "1. Question A\n2. Question B"

    def test_returns_fallback_for_empty_list(self):
        from generator.services import _format_reference_questions

        result = _format_reference_questions([])
        assert result == "No reference questions available."


# ---------------------------------------------------------------------------
# _build_metadata_filter
# ---------------------------------------------------------------------------

class TestBuildMetadataFilter:
    def test_returns_and_filter_when_both_fields_provided(self):
        result = _build_metadata_filter("Senior", "Tech")
        assert result == {
            "$and": [
                {"role_level": {"$eq": "Senior"}},
                {"industry": {"$eq": "Tech"}},
            ]
        }

    def test_returns_single_condition_when_only_role_level_provided(self):
        result = _build_metadata_filter("Senior", "")
        assert result == {"role_level": {"$eq": "Senior"}}

    def test_returns_single_condition_when_only_industry_provided(self):
        result = _build_metadata_filter("", "Finance")
        assert result == {"industry": {"$eq": "Finance"}}

    def test_returns_empty_dict_when_both_fields_empty(self):
        result = _build_metadata_filter("", "")
        assert result == {}


# ---------------------------------------------------------------------------
# _fetch_reference_questions (fallback behaviour lives in services.py)
# ---------------------------------------------------------------------------

class TestFetchReferenceQuestions:
    def test_returns_questions_on_success(self):
        from generator.services import _fetch_reference_questions

        with patch(
            "generator.services.retrieve_relevant_questions",
            return_value=["Q1", "Q2"],
        ):
            result = _fetch_reference_questions(
                role_description="Build APIs",
                role_level="Senior",
                industry="Tech",
            )

        assert result == ["Q1", "Q2"]

    def test_returns_empty_list_when_retrieval_raises(self):
        from generator.services import _fetch_reference_questions

        with patch(
            "generator.services.retrieve_relevant_questions",
            side_effect=Exception("ChromaDB unavailable"),
        ):
            result = _fetch_reference_questions(
                role_description="Build APIs",
                role_level="Senior",
                industry="Tech",
            )

        assert result == []

    def test_passes_empty_string_for_role_title(self):
        from generator.services import _fetch_reference_questions

        with patch(
            "generator.services.retrieve_relevant_questions",
            return_value=[],
        ) as mock_retrieve:
            _fetch_reference_questions(
                role_description="Some description",
                role_level="",
                industry="",
            )

        call_kwargs = mock_retrieve.call_args.kwargs
        assert call_kwargs["role_title"] == ""
