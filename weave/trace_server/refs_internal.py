# This file contains the definition for "Internal" weave refs. These should never be
# exposed to the user and should only be used internally by the weave-trace service.
# Specifically, the user-space operates on plain-text `entity/project` scopes. While
# internally, we operate on internal `project_id`s scopes. At rest, and in the database,
# we store the internal `project_id`. However, over the wire, we use the plain-text. Practically,
# the trace interface should only ever operate on internal refs.
import dataclasses
import urllib
from typing import Union

WEAVE_INTERNAL_SCHEME = "weave-trace-internal"
WEAVE_SCHEME = "weave"
WEAVE_PRIVATE_SCHEME = "weave-private"

DICT_KEY_EDGE_NAME = "key"
LIST_INDEX_EDGE_NAME = "index"
OBJECT_ATTR_EDGE_NAME = "attr"
TABLE_ROW_ID_EDGE_NAME = "id"

valid_edge_names = (
    DICT_KEY_EDGE_NAME,
    LIST_INDEX_EDGE_NAME,
    OBJECT_ATTR_EDGE_NAME,
    TABLE_ROW_ID_EDGE_NAME,
)


class InvalidInternalRef(ValueError):
    pass


def ref_part_quoter(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def ref_part_unquoter(s: str) -> str:
    return urllib.parse.unquote(s)


def validate_extra(extra: list[str]) -> None:
    """The `extra` path is always a series of `edge_name`/`edge_value` pairs.
    For example: `attr/attr_name/index/0`. The `edge_name` is one of the
    following: `key`, `index`, `attr`, `id`. The `edge_value` is a string
    that corresponds to the edge name. In the case of `attr` and `key`, the
    edge value is purely user-defined and can be any string.
    """
    if len(extra) % 2 != 0:
        raise InvalidInternalRef("Extra fields must be key-value pairs.")

    for i, e in enumerate(extra):
        if i % 2 == 0:
            # Here we are in the edge name position
            if e not in (
                DICT_KEY_EDGE_NAME,
                LIST_INDEX_EDGE_NAME,
                OBJECT_ATTR_EDGE_NAME,
                TABLE_ROW_ID_EDGE_NAME,
            ):
                raise InvalidInternalRef(
                    f"Invalid extra edge name at index {i}: {extra}"
                )
        else:
            # Here we are in the edge value position
            # There is only a single rule here:
            if extra[i - 1] == LIST_INDEX_EDGE_NAME:
                try:
                    int(e)
                except ValueError:
                    raise InvalidInternalRef(
                        f"Invalid list edge value at index {i}: {extra}"
                    )
            pass


def validate_no_slashes(s: str, field_name: str) -> None:
    if "/" in s:
        raise InvalidInternalRef(f"{field_name} cannot contain '/'")


def validate_no_colons(s: str, field_name: str) -> None:
    if ":" in s:
        raise InvalidInternalRef(f"{field_name} cannot contain ':'")


@dataclasses.dataclass(frozen=True)
class InternalTableRef:
    project_id: str
    digest: str

    def __post_init__(self) -> None:
        validate_no_slashes(self.project_id, "project_id")
        validate_no_slashes(self.digest, "digest")

    def uri(self) -> str:
        return f"{WEAVE_INTERNAL_SCHEME}:///{self.project_id}/table/{self.digest}"


@dataclasses.dataclass(frozen=True)
class InternalObjectRef:
    project_id: str
    name: str
    version: str
    extra: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        validate_no_slashes(self.project_id, "project_id")
        validate_no_slashes(self.version, "version")
        validate_no_colons(self.version, "version")
        validate_extra(self.extra)

    def uri(self) -> str:
        u = f"{WEAVE_INTERNAL_SCHEME}:///{self.project_id}/object/{ref_part_quoter(self.name)}:{self.version}"
        if self.extra:
            u += "/" + "/".join(ref_part_quoter(e) for e in self.extra)
        return u


@dataclasses.dataclass(frozen=True)
class InternalOpRef(InternalObjectRef):
    def uri(self) -> str:
        u = f"{WEAVE_INTERNAL_SCHEME}:///{self.project_id}/op/{ref_part_quoter(self.name)}:{self.version}"
        if self.extra:
            u += "/" + "/".join(ref_part_quoter(e) for e in self.extra)
        return u


@dataclasses.dataclass(frozen=True)
class InternalCallRef:
    project_id: str
    id: str
    extra: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        validate_no_slashes(self.project_id, "project_id")
        validate_no_slashes(self.id, "id")
        # Note: we don't actually support extra fields for calls, but when
        # we do, we need to add edge names to the known list
        validate_extra(self.extra)

    def uri(self) -> str:
        u = f"{WEAVE_INTERNAL_SCHEME}:///{self.project_id}/call/{self.id}"
        if self.extra:
            u += "/" + "/".join(ref_part_quoter(e) for e in self.extra)
        return u


def parse_internal_uri(uri: str) -> Union[InternalObjectRef, InternalTableRef]:
    if uri.startswith(f"{WEAVE_INTERNAL_SCHEME}:///"):
        path = uri[len(f"{WEAVE_INTERNAL_SCHEME}:///") :]
        parts = path.split("/")
        if len(parts) < 2:
            raise InvalidInternalRef(f"Invalid URI: {uri}. Must have at least 2 parts")
        project_id, kind = parts[:2]
        remaining = parts[2:]
    elif uri.startswith(f"{WEAVE_SCHEME}:///"):
        path = uri[len(f"{WEAVE_SCHEME}:///") :]
        parts = path.split("/")
        if len(parts) < 3:
            raise InvalidInternalRef(f"Invalid URI: {uri}. Must have at least 3 parts")
        quoted_entity, quoted_project, kind = parts[:3]
        entity = ref_part_unquoter(quoted_entity)
        project = ref_part_unquoter(quoted_project)
        project_id = f"{entity}/{project}"
        remaining = parts[3:]
    else:
        raise InvalidInternalRef(
            f"Invalid URI: {uri}. Must start with {WEAVE_INTERNAL_SCHEME}:/// or {WEAVE_SCHEME}:///"
        )
    if kind == "table":
        return InternalTableRef(project_id=project_id, digest=remaining[0])
    elif kind == "object":
        name, version, extra = _parse_remaining(remaining)
        return InternalObjectRef(
            project_id=project_id,
            name=name,
            version=version,
            extra=extra,
        )
    elif kind == "op":
        name, version, extra = _parse_remaining(remaining)
        return InternalOpRef(
            project_id=project_id,
            name=name,
            version=version,
            extra=extra,
        )
    else:
        raise InvalidInternalRef(f"Unknown ref kind: {kind}")


def _parse_remaining(remaining: list[str]) -> tuple[str, str, list[str]]:
    """`remaining` refers to everything after `object` or `op` in the ref.
    It is expected to be pre-split by slashes into parts. The return
    is a tuple of name, version, and extra parts, properly unquoted.
    """
    name_encoded, version = remaining[0].split(":")
    name = ref_part_unquoter(name_encoded)
    extra = remaining[1:]
    if len(extra) == 1 and extra[0] == "":
        extra = []
    else:
        extra = [ref_part_unquoter(r) for r in extra]

    return name, version, extra


def string_will_be_interpreted_as_ref(s: str) -> bool:
    return s.startswith(f"{WEAVE_INTERNAL_SCHEME}:///") or s.startswith(
        f"{WEAVE_SCHEME}:///"
    )
