"""
Shared fixtures and configuration for deepeval LLM evaluation tests.
"""

import os

import pytest
from deepeval.metrics import GEval
from deepeval.models import OllamaModel
from deepeval.test_case import LLMTestCaseParams


# ---------------------------------------------------------------------------
# Reusable GEval metric factories
# ---------------------------------------------------------------------------


def ollama_evaluator_model():
    api_key = os.getenv("OLLAMA_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    return OllamaModel(
        model=os.getenv("OLLAMA_EVAL_MODEL", os.getenv("OLLAMA_MODEL", "gemma4:31b")),
        base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com"),
        temperature=0,
        headers=headers,
    )


def json_schema_metric(schema_description: str):
    """Creates a GEval metric that checks JSON schema compliance."""
    return GEval(
        name="JSON Schema Compliance",
        criteria=(
            "Evaluate whether the actual output is valid JSON that conforms to "
            "the required schema. Only check structure, key names, and data "
            "types — do NOT penalize for specific values. " + schema_description
        ),
        evaluation_steps=[
            "Check that the output is valid JSON.",
            "Check that the required keys and value types match the schema.",
        ],
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        model=ollama_evaluator_model(),
        threshold=0.5,
    )


def output_correctness_metric():
    """Creates a GEval metric that checks factual/logical correctness."""
    return GEval(
        name="Output Correctness",
        criteria=(
            "Determine whether the actual output is logically correct and "
            "reasonable given the input text. The analysis should make sense "
            "for the provided input."
        ),
        evaluation_steps=[
            "Compare the output with the input text.",
            "Judge whether the output is logically correct and reasonable.",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        model=ollama_evaluator_model(),
        threshold=0.5,
    )


def answer_relevancy_metric():
    """Creates a GEval metric that checks whether the output is topically
    relevant to the input.  Unlike AnswerRelevancyMetric (which assumes a
    Q&A format), this works for classification and analysis endpoints where
    the output is structured metadata about the input text."""
    return GEval(
        name="Answer Relevancy",
        criteria=(
            "Evaluate whether the actual output is topically relevant to the "
            "input text. The labels, categories, or analysis in the output "
            "should directly relate to the subject matter of the input. "
            "Structured metadata (labels, categories, confidence scores) that "
            "accurately describes the input text should be considered relevant."
        ),
        evaluation_steps=[
            "Identify the main topic of the input text.",
            "Check whether the output directly relates to that topic.",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        model=ollama_evaluator_model(),
        threshold=0.5,
    )
