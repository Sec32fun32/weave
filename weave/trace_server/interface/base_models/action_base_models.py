import typing

from pydantic import BaseModel

LLM_JUDGE_ACTION_NAME = "llm_judge"


class _BuiltinAction(BaseModel):
    action_type: typing.Literal["builtin"] = "builtin"
    name: str


class ConfiguredAction(BaseModel):
    name: str
    action: _BuiltinAction
    config: dict


class ActionDispatchFilter(BaseModel):
    op_name: str
    sample_rate: float
    configured_action_ref: str
    disabled: typing.Optional[bool] = None
