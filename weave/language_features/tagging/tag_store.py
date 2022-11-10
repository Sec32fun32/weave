"""
This file contains the data structures and methods used to manage the in-memory
state of tagged objects. Crticailly, it relies on two private global objects:

* `_OBJ_TAGS_MEM_MAP` - used to map the python id of an object to a dictionary of
    tags. This is used to store the tags for an object.
* `_VISITED_OBJ_IDS` - used to keep track of the python ids of objects that are
    currently being visited. This is used to prevent infinite recursion when
    determing the type of tagged objects.

The primary user-facing functions are:

* `add_tags` - used to add tags to an object
* `find_tag` - used to recursively lookup the tag for a given object

"""

import contextvars
from contextlib import contextmanager
import typing

from ... import box
from ... import weave_types as types

from collections import defaultdict

# Private global objects used to store the tags for objects
_OBJ_TAGS_MEM_MAP: contextvars.ContextVar[
    defaultdict[
        int, dict[int, dict[str, typing.Any]]
    ]  # shape: {node_id: {obj_id: {tag_key: tag_value}}}
] = contextvars.ContextVar("obj_tags_mem_map", default=defaultdict(dict))

# Current node id for scoping tags
_OBJ_TAGS_CURR_NODE_ID: contextvars.ContextVar[int] = contextvars.ContextVar(
    "obj_tags_curr_node", default=-1
)

# gets the current tag memory map for the current node
def _current_obj_tag_mem_map() -> dict[int, dict[str, typing.Any]]:
    return _OBJ_TAGS_MEM_MAP.get()[_OBJ_TAGS_CURR_NODE_ID.get()]


# sets the current node with optionally merged in parent tags
@contextmanager
def set_curr_node(node_id: int, parent_node_ids: list[int]) -> typing.Iterator[None]:
    token = _OBJ_TAGS_CURR_NODE_ID.set(node_id)
    for parent_id in parent_node_ids:
        _OBJ_TAGS_MEM_MAP.get()[node_id].update(_OBJ_TAGS_MEM_MAP.get()[parent_id])
    try:
        yield None
    finally:
        _OBJ_TAGS_CURR_NODE_ID.reset(token)


# Private global objects used to keep track of the python ids of objects that are
# currently being visited.
_VISITED_OBJ_IDS: contextvars.ContextVar[set[int]] = contextvars.ContextVar(
    "visited_obj_ids", default=set()
)

# Callers can create an isolated tagging context by using this context manager
# This is primarily used by the executor to prevent tags from leaking between
# different executions. See execute.py for it's usage.
@contextmanager
def isolated_tagging_context() -> typing.Iterator[None]:
    token = _OBJ_TAGS_MEM_MAP.set(defaultdict(dict))
    try:
        yield None
    finally:
        _OBJ_TAGS_MEM_MAP.reset(token)


# Callers can indicate that an object is being visited by using this context manager
# This is primarily used by the TaggedValueType::type_of_instance method to prevent
# infinite recursion when determining the type of tagged objects.
@contextmanager
def with_visited_obj(obj: typing.Any) -> typing.Iterator[None]:
    id_val = id(obj)
    assert id_val == id(box.box(obj)), "Can only tag boxed objects"
    visited_obj_ids = _VISITED_OBJ_IDS.get()
    visited_obj_ids.add(id_val)
    try:
        yield None
    finally:
        visited_obj_ids.remove(id_val)


# Adds a dictionary of tags to an object
def add_tags(obj: typing.Any, tags: dict[str, typing.Any]) -> typing.Any:
    id_val = id(obj)
    assert box.is_boxed(obj), "Can only tag boxed objects"
    existing_tags = get_tags(obj) if is_tagged(obj) else {}
    _current_obj_tag_mem_map()[id_val] = {**existing_tags, **tags}


# Gets the dictionary of tags assocaited with the given object
# Note: this is not recursive, it only returns the tags directly assocaited with
# the given object
def get_tags(obj: typing.Any) -> dict[str, typing.Any]:
    id_val = id(obj)
    if id_val in _VISITED_OBJ_IDS.get():
        raise ValueError("Cannot get tags for an object that is being visited")
    current_mem_map = _current_obj_tag_mem_map()
    if id_val not in current_mem_map:
        raise ValueError("Object is not tagged")
    return current_mem_map[id_val]


# Recursively looks up the tag for the object, given a key and target tag_type.
def find_tag(
    obj: typing.Any, key: str, tag_type: types.Type = types.Any()
) -> typing.Any:
    # TODO: Implement tag type filtering using tag_type
    cur_tags = get_tags(obj)
    if key in cur_tags:
        return cur_tags[key]
    else:
        for parent in cur_tags.values():
            if is_tagged(parent):
                par_tag = find_tag(parent, key)
                if par_tag is not None:
                    return par_tag
    raise ValueError(f"Could not find tag {key} in {obj}")


# Returns true if the given object has been tagged
def is_tagged(obj: typing.Any) -> bool:
    id_val = id(obj)
    return id_val not in _VISITED_OBJ_IDS.get() and id_val in _current_obj_tag_mem_map()
