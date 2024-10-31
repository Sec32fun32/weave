import asyncio
import os

import pytest

from weave.integrations.integration_utilities import op_name_from_ref


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_chat_completion(client):
    from huggingface_hub import InferenceClient

    huggingface_client = InferenceClient(
        api_key=os.environ.get("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
    )
    image_url = "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
    huggingface_client.chat_completion(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": "Describe this image in one sentence."},
                ],
            }
        ],
        max_tokens=500,
        seed=42,
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.InferenceClient.chat_completion"
    )
    output = call.output
    assert output.choices[0].finish_reason == "stop"
    assert output.choices[0].index == 0
    assert "statue of liberty" in output.choices[0].message.content.lower()
    assert output.choices[0].message.role == "assistant"
    assert output.model == "meta-llama/Llama-3.2-11B-Vision-Instruct"
    assert output.usage.prompt_tokens == 44


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_chat_completion_stream(client):
    from huggingface_hub import InferenceClient

    huggingface_client = InferenceClient(
        api_key=os.environ.get("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
    )
    image_url = "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
    [
        r
        for r in huggingface_client.chat_completion(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {
                            "type": "text",
                            "text": "Describe this image in one sentence.",
                        },
                    ],
                }
            ],
            max_tokens=500,
            seed=42,
            stream=True,
        )
    ]

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.InferenceClient.chat_completion"
    )
    output = call.output
    assert output.choices[0].index == 0
    assert "statue of liberty" in output.choices[0].message.content.lower()
    assert output.choices[0].message.role == "assistant"
    assert output.model == "meta-llama/Llama-3.2-11B-Vision-Instruct"


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_chat_completion_async(client):
    from huggingface_hub import AsyncInferenceClient

    huggingface_client = AsyncInferenceClient(
        api_key=os.environ.get("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
    )
    image_url = "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
    asyncio.run(
        huggingface_client.chat_completion(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {
                            "type": "text",
                            "text": "Describe this image in one sentence.",
                        },
                    ],
                }
            ],
            max_tokens=500,
            seed=42,
        )
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.AsyncInferenceClient.chat_completion"
    )
    output = call.output
    assert output.choices[0].finish_reason == "stop"
    assert output.choices[0].index == 0
    assert "statue of liberty" in output.choices[0].message.content.lower()
    assert output.choices[0].message.role == "assistant"
    assert output.model == "meta-llama/Llama-3.2-11B-Vision-Instruct"
    assert output.usage.prompt_tokens == 44


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_document_question_answering(client):
    from huggingface_hub import InferenceClient

    image_url = "https://huggingface.co/spaces/impira/docquery/resolve/2359223c1837a7587402bda0f2643382a6eefeab/invoice.png"
    InferenceClient(
        api_key=os.environ.get("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
    ).document_question_answering(
        image=image_url,
        model="impira/layoutlm-document-qa",
        question="What is the invoice number?",
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.InferenceClient.document_question_answering"
    )
    output = call.output
    assert output[0].answer == "us-001"


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_document_question_answering_async(client):
    from huggingface_hub import AsyncInferenceClient

    image_url = "https://huggingface.co/spaces/impira/docquery/resolve/2359223c1837a7587402bda0f2643382a6eefeab/invoice.png"
    asyncio.run(
        AsyncInferenceClient(
            api_key=os.environ.get("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
        ).document_question_answering(
            image=image_url,
            model="impira/layoutlm-document-qa",
            question="What is the invoice number?",
        )
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.AsyncInferenceClient.document_question_answering"
    )
    output = call.output
    assert output[0].answer == "us-001"


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_visual_question_answering(client):
    from huggingface_hub import InferenceClient

    image_url = (
        "https://huggingface.co/datasets/mishig/sample_images/resolve/main/tiger.jpg"
    )
    InferenceClient(
        api_key=os.environ.get("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
    ).visual_question_answering(
        image=image_url,
        question="What is the animal doing?",
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.InferenceClient.visual_question_answering"
    )
    output = call.output
    assert output[0].answer == "laying down"


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_visual_question_answering_async(client):
    from huggingface_hub import AsyncInferenceClient

    image_url = (
        "https://huggingface.co/datasets/mishig/sample_images/resolve/main/tiger.jpg"
    )
    asyncio.run(
        AsyncInferenceClient(
            api_key=os.environ.get("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
        ).visual_question_answering(
            image=image_url,
            question="What is the animal doing?",
        )
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.AsyncInferenceClient.visual_question_answering"
    )
    output = call.output
    assert output[0].answer == "laying down"


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_fill_mask(client):
    from huggingface_hub import InferenceClient

    InferenceClient(
        api_key=os.getenv("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
    ).fill_mask("The goal of life is <mask>.")

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert op_name_from_ref(call.op_name) == "huggingface_hub.InferenceClient.fill_mask"
    output = call.output
    assert output[0].token_str in output[0].sequence
    assert output[0].score > 0


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_fill_mask_async(client):
    from huggingface_hub import AsyncInferenceClient

    asyncio.run(
        AsyncInferenceClient(
            api_key=os.getenv("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
        ).fill_mask("The goal of life is <mask>.")
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.AsyncInferenceClient.fill_mask"
    )
    output = call.output
    assert output[0].token_str in output[0].sequence
    assert output[0].score > 0


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_question_answering(client):
    from huggingface_hub import InferenceClient

    InferenceClient(
        api_key=os.getenv("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
    ).question_answering(
        question="What's my name?", context="My name is Clara and I live in Berkeley."
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.InferenceClient.question_answering"
    )
    output = call.output
    assert output.answer == "Clara"


@pytest.mark.skip_clickhouse_client
@pytest.mark.vcr(
    filter_headers=["authorization", "x-api-key"],
    allowed_hosts=["api.wandb.ai", "localhost", "trace.wandb.ai"],
)
def test_huggingface_question_answering_async(client):
    from huggingface_hub import AsyncInferenceClient

    asyncio.run(
        AsyncInferenceClient(
            api_key=os.getenv("HUGGINGFACE_API_KEY", "DUMMY_API_KEY")
        ).question_answering(
            question="What's my name?",
            context="My name is Clara and I live in Berkeley.",
        )
    )

    calls = list(client.calls())
    assert len(calls) == 1

    call = calls[0]
    assert call.started_at < call.ended_at
    assert (
        op_name_from_ref(call.op_name)
        == "huggingface_hub.AsyncInferenceClient.question_answering"
    )
    output = call.output
    assert output.answer == "Clara"
