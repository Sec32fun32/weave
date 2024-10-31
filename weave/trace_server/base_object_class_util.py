from typing import Any, Optional, Tuple

from pydantic import BaseModel

from weave.trace_server.interface.base_object_classes.base_object_registry import (
    BASE_OBJECT_REGISTRY,
)

base_object_class_names = ["BaseObject", "Object"]


def get_base_object_class(val: Any) -> Optional[str]:
    if isinstance(val, dict):
        if "_bases" in val:
            if isinstance(val["_bases"], list):
                if len(val["_bases"]) >= 2:
                    if val["_bases"][-1] == "BaseModel":
                        if val["_bases"][-2] in base_object_class_names:
                            if len(val["_bases"]) > 2:
                                return val["_bases"][-3]
                            elif "_class_name" in val:
                                return val["_class_name"]
    return None


def process_incoming_object(
    dict_val: dict, req_base_object_class: Optional[str] = None
) -> Tuple[dict, Optional[str]]:
    dict_val = dict_val.copy()
    val_base_object_class = get_base_object_class(dict_val)

    if (
        val_base_object_class != None
        and req_base_object_class != None
        and val_base_object_class != req_base_object_class
    ):
        raise ValueError(
            f"set_base_object_class must match base_object_class: {val_base_object_class} != {req_base_object_class}"
        )

    if val_base_object_class is not None:
        # In this case, we simply validate if the match is found
        if base_object_class_type := BASE_OBJECT_REGISTRY.get(val_base_object_class):
            base_object_class_type.model_validate(dict_val)
    elif req_base_object_class is not None:
        # In this case, we require that the base object class is registered
        if base_object_class_type := BASE_OBJECT_REGISTRY.get(req_base_object_class):
            dict_val = dump_base_object(base_object_class_type.model_validate(dict_val))
        else:
            raise ValueError(f"Unknown base object class: {req_base_object_class}")

    base_object_class = val_base_object_class or req_base_object_class

    return dict_val, base_object_class


# Server-side version of `pydantic_object_record`
def dump_base_object(val: BaseModel) -> dict:
    cls = val.__class__
    cls_name = val.__class__.__name__
    bases = [c.__name__ for c in cls.mro()[1:-1]]

    dump = {}
    # Order matters here due to the way we calculate the digest!
    # This matches the client
    dump["_type"] = cls_name
    for k in val.model_fields:
        dump[k] = _general_dump(getattr(val, k))
    # yes, this is done twice, to match the client
    dump["_class_name"] = cls_name
    dump["_bases"] = bases
    return dump


def _general_dump(val: Any) -> Any:
    if isinstance(val, BaseModel):
        return dump_base_object(val)
    elif isinstance(val, dict):
        return {k: _general_dump(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [_general_dump(v) for v in val]
    else:
        return val
