import json
import os
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from .prompts import CV_EXTRACT_PROMPT, CV_MATCH_PROMPT


class CVMatchState(TypedDict):
    cv_text: str
    role_title: str
    role_level: str
    job_description_summary: str
    required_qualifications: str
    preferred_qualifications: str
    candidate_profile: dict
    match_result: dict


def _extract_candidate_profile(state: CVMatchState) -> dict:
    """Node 1: Extract structured candidate information from raw CV text."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.environ["OPENAI_API_KEY"],
    )
    prompt = CV_EXTRACT_PROMPT.format(cv_text=state["cv_text"])
    response = llm.invoke(prompt)
    candidate_profile = json.loads(response.content)
    return {"candidate_profile": candidate_profile}


def _score_candidate(state: CVMatchState) -> dict:
    """Node 2: Score candidate profile against job requirements."""
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        api_key=os.environ["OPENAI_API_KEY"],
    )
    prompt = CV_MATCH_PROMPT.format(
        role_title=state["role_title"],
        role_level=state["role_level"],
        job_description_summary=state["job_description_summary"],
        required_qualifications=state["required_qualifications"],
        preferred_qualifications=state["preferred_qualifications"],
        candidate_profile=json.dumps(state["candidate_profile"], indent=2),
    )
    response = llm.invoke(prompt)
    match_result = json.loads(response.content)
    return {"match_result": match_result}


def build_cv_match_graph():
    """Build and compile the 2-node CV matching LangGraph pipeline."""
    graph = StateGraph(CVMatchState)
    graph.add_node("extract_candidate_profile", _extract_candidate_profile)
    graph.add_node("score_candidate", _score_candidate)
    graph.set_entry_point("extract_candidate_profile")
    graph.add_edge("extract_candidate_profile", "score_candidate")
    graph.add_edge("score_candidate", END)
    return graph.compile()
