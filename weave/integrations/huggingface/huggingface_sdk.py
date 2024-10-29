import importlib
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

import weave
from weave.trace.op_extensions.accumulator import add_accumulator
from weave.trace.patcher import MultiPatcher, SymbolPatcher

if TYPE_CHECKING:
    from huggingface_hub.inference._generated.types.chat_completion import (
        ChatCompletionOutput,
        ChatCompletionStreamOutput,
    )


def huggingface_accumulator(
    acc: Optional[Union["ChatCompletionStreamOutput", "ChatCompletionOutput"]],
    value: "ChatCompletionStreamOutput",
) -> "ChatCompletionOutput":
    from huggingface_hub.inference._generated.types.chat_completion import (
        ChatCompletionOutput,
        ChatCompletionOutputComplete,
        ChatCompletionOutputMessage,
        ChatCompletionOutputUsage,
    )

    if acc is None:
        acc = ChatCompletionOutput(
            choices=[
                ChatCompletionOutputComplete(
                    index=choice.index,
                    message=ChatCompletionOutputMessage(
                        content=choice.delta.content or "",
                        role=choice.delta.role or "assistant",
                    ),
                    finish_reason=None,
                )
                for choice in value.choices
            ],
            created=value.created,
            id=value.id,
            model=value.model,
            system_fingerprint=value.system_fingerprint,
            usage=value.usage,
        )
        return acc

    # Accumulate subsequent chunks
    for idx, value_choice in enumerate(value.choices):
        acc.choices[idx].message.content += value_choice.delta.content or ""

    if acc.usage is None:
        acc.usage = ChatCompletionOutputUsage(
            completion_tokens=0, prompt_tokens=0, total_tokens=0
        )
    # # For some reason, value.usage is always coming `None`
    # # Might be a bug in `huggingface_hub.InferenceClient`
    # if value.usage is not None:
    #     acc.usage.completion_tokens += value.usage.completion_tokens
    #     acc.usage.prompt_tokens += value.usage.prompt_tokens
    #     acc.usage.total_tokens += value.usage.total_tokens
    return acc


def huggingface_wrapper_sync(name: str) -> Callable[[Callable], Callable]:
    def wrapper(fn: Callable) -> Callable:
        op = weave.op()(fn)
        op.name = name
        return add_accumulator(
            op,  # type: ignore
            make_accumulator=lambda inputs: huggingface_accumulator,
            should_accumulate=lambda inputs: isinstance(inputs, dict)
            and bool(inputs.get("stream")),
        )

    return wrapper


def huggingface_wrapper_async(name: str) -> Callable[[Callable], Callable]:
    def wrapper(fn: Callable) -> Callable:
        def _fn_wrapper(fn: Callable) -> Callable:
            @wraps(fn)
            async def _async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await fn(*args, **kwargs)

            return _async_wrapper

        "We need to do this so we can check if `stream` is used"
        op = weave.op()(_fn_wrapper(fn))
        op.name = name  # type: ignore
        return add_accumulator(
            op,  # type: ignore
            make_accumulator=lambda inputs: huggingface_accumulator,
            should_accumulate=lambda inputs: isinstance(inputs, dict)
            and bool(inputs.get("stream")),
        )

    return wrapper


huggingface_patcher = MultiPatcher(
    [
        SymbolPatcher(
            lambda: importlib.import_module("huggingface_hub"),
            "InferenceClient.chat_completion",
            huggingface_wrapper_sync(
                name="huggingface_hub.InferenceClient.chat_completion"
            ),
        ),
        SymbolPatcher(
            lambda: importlib.import_module("huggingface_hub"),
            "AsyncInferenceClient.chat_completion",
            huggingface_wrapper_async(
                name="huggingface_hub.AsyncInferenceClient.chat_completion"
            ),
        ),
        SymbolPatcher(
            lambda: importlib.import_module("huggingface_hub"),
            "InferenceClient.document_question_answering",
            huggingface_wrapper_sync(
                name="huggingface_hub.InferenceClient.document_question_answering"
            ),
        ),
        SymbolPatcher(
            lambda: importlib.import_module("huggingface_hub"),
            "AsyncInferenceClient.document_question_answering",
            huggingface_wrapper_sync(
                name="huggingface_hub.AsyncInferenceClient.document_question_answering"
            ),
        ),
        SymbolPatcher(
            lambda: importlib.import_module("huggingface_hub"),
            "InferenceClient.visual_question_answering",
            huggingface_wrapper_sync(
                name="huggingface_hub.InferenceClient.visual_question_answering"
            ),
        ),
        SymbolPatcher(
            lambda: importlib.import_module("huggingface_hub"),
            "AsyncInferenceClient.visual_question_answering",
            huggingface_wrapper_sync(
                name="huggingface_hub.AsyncInferenceClient.visual_question_answering"
            ),
        ),
        SymbolPatcher(
            lambda: importlib.import_module("huggingface_hub"),
            "InferenceClient.fill_mask",
            huggingface_wrapper_sync(
                name="huggingface_hub.InferenceClient.fill_mask"
            ),
        ),
        SymbolPatcher(
            lambda: importlib.import_module("huggingface_hub"),
            "AsyncInferenceClient.fill_mask",
            huggingface_wrapper_sync(
                name="huggingface_hub.AsyncInferenceClient.fill_mask"
            ),
        ),
    ]
)
