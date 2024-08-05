import importlib
from typing import Callable, Dict, List, Optional, Union

from google.ai.generativelanguage_v1beta.types.safety import SafetyRating
from google.generativeai.types.generation_types import GenerateContentResponse

import weave
from weave.trace.op_extensions.accumulator import add_accumulator
from weave.trace.patcher import MultiPatcher, SymbolPatcher


def gemini_accumulator(
    acc: GenerateContentResponse, value: GenerateContentResponse
) -> GenerateContentResponse:
    for candidate_idx in range(len(value.candidates)):
        candidate = value.candidates[candidate_idx]
        for part_idx in range(len(candidate.content.parts)):
            acc.candidates[candidate_idx].content.parts[
                part_idx
            ].text += candidate.content.parts[part_idx].text
        if isinstance(acc.candidates[candidate_idx].safety_ratings[0], SafetyRating):
            acc.candidates[candidate_idx].safety_ratings = [
                value.candidates[candidate_idx].safety_ratings
            ]
        else:
            acc.candidates[candidate_idx].safety_ratings.append(
                value.candidates[candidate_idx].safety_ratings
            )
    return acc


def should_use_accumulator(inputs: Dict) -> bool:
    return isinstance(inputs, dict) and bool(inputs.get("stream"))


def gemini_wrapper(name: str) -> Callable[[Callable], Callable]:
    def wrapper(fn: Callable) -> Callable:
        op = weave.op()(fn)
        op.name = name  # type: ignore
        # return op
        return add_accumulator(
            op,  # type: ignore
            make_accumulator=lambda inputs: gemini_accumulator,
            should_accumulate=should_use_accumulator,
        )

    return wrapper


gemini_patcher = MultiPatcher(
    [
        SymbolPatcher(
            lambda: importlib.import_module("google.generativeai"),
            "GenerativeModel.generate_content",
            gemini_wrapper(name="google.generativeai.GenerativeModel.generate_content"),
        ),
    ]
)
