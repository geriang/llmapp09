"""
Shared fixtures and configuration for deepeval LLM evaluation tests.
"""

import os
import re
from typing import Optional

import ollama
import pytest
from deepeval.metrics import GEval
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCaseParams


class OllamaJudgeModel(DeepEvalBaseLLM):
    """DeepEval Ollama judge that accepts fenced JSON responses."""

    def __init__(self, model: str, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        super().__init__(model)

    def load_model(self):
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        return ollama.Client(host=self.base_url, headers=headers)

    @staticmethod
    def _clean_response(content: str) -> str:
        return re.sub(
            r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE
        )

    def generate(self, prompt: str, schema: Optional[type] = None):
        response = self.model.chat(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            format=schema.model_json_schema() if schema else None,
            options={"temperature": 0},
        )
        content = self._clean_response(response.message.content)
        return (schema.model_validate_json(content) if schema else content), 0

    async def a_generate(self, prompt: str, schema: Optional[type] = None):
        client = ollama.AsyncClient(
            host=self.base_url, headers=self.model._client.headers
        )
        response = await client.chat(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            format=schema.model_json_schema() if schema else None,
            options={"temperature": 0},
        )
        content = self._clean_response(response.message.content)
        return (schema.model_validate_json(content) if schema else content), 0

    def get_model_name(self):
        return f"{self.name} (Ollama)"


def ollama_judge() -> OllamaJudgeModel:
    api_key = os.getenv("OLLAMA_API_KEY", "")
    return OllamaJudgeModel(
        model=os.getenv("OLLAMA_EVAL_MODEL", "gemma4:31b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com"),
        api_key=api_key,
    )


judge_model = ollama_judge()


# ---------------------------------------------------------------------------
# Reusable GEval metric factories
# ---------------------------------------------------------------------------


def json_schema_metric(schema_description: str):
    """Creates a GEval metric that checks JSON schema compliance."""
    return GEval(
        name="JSON Schema Compliance",
        criteria=(
            "Evaluate whether the actual output is valid JSON that conforms to "
            "the required schema. Only check structure, key names, and data "
            "types — do NOT penalize for specific values. " + schema_description
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.5,
        model=judge_model,
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
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.5,
        model=judge_model,
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
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.5,
        model=judge_model,
    )
