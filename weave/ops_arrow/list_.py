import typing
import dataclasses
import json
import numpy as np
import pandas as pd
import pyarrow as pa

py_type = type

from ..api import op, weave_class, type, use
from .. import weave_types as types
from .. import graph
from .. import errors
from .. import registry_mem
from .. import mappers_arrow
from .. import mappers_python_def
from .. import mappers_python
from .. import artifacts_local
from .. import storage
from .. import refs
from .. import dispatch
from .. import execute_fast
from .. import weave_internal
from .. import context
from .. import weavify

from . import arrow


FLATTEN_DELIMITER = "➡️"


def _recursively_flatten_structs_in_array(
    arr: pa.Array, prefix: str, _stack_depth=0
) -> dict[str, pa.Array]:
    if pa.types.is_struct(arr.type):
        result: dict[str, pa.Array] = {}
        for field in arr.type:
            new_prefix = (
                prefix + (FLATTEN_DELIMITER if _stack_depth > 0 else "") + field.name
            )
            result.update(
                _recursively_flatten_structs_in_array(
                    arr.field(field.name),
                    new_prefix,
                    _stack_depth=_stack_depth + 1,
                )
            )
        return result
    return {prefix: arr}


# TODO: make more efficient
def _unflatten_structs_in_flattened_table(table: pa.Table) -> pa.Table:
    """take a table with column names like {a.b.c: [1,2,3], a.b.d: [4,5,6], a.e: [7,8,9]}
    and return a struct array with the following structure:
    [ {a: {b: {c: 1, d: 4}, e: 7}}, {a: {b: {c: 2, d: 5}, e: 8}}, {a: {b: {c: 3, d: 6}, e: 9}} ]"""

    # get all columns in table
    column_names = list(
        map(lambda name: name.split(FLATTEN_DELIMITER), table.column_names)
    )
    multi_index = pd.MultiIndex.from_tuples(column_names)
    df = table.to_pandas()
    df.columns = multi_index
    records = df.to_dict(orient="records")

    # convert to arrow
    # records now looks like [{('a', 'b', 'c'): 1, ('a', 'b', 'd'): 2, ('a', 'e', nan): 3},
    # {('a', 'b', 'c'): 4, ('a', 'b', 'd'): 5, ('a', 'e', nan): 6},
    # {('a', 'b', 'c'): 7, ('a', 'b', 'd'): 8, ('a', 'e', nan): 9}]
    new_records = []
    for record in records:
        new_record: dict[str, typing.Any] = {}
        for entry in record:
            current_pointer = new_record
            filtered_entry = list(filter(lambda key: key is not np.nan, entry))
            for i, key in enumerate(filtered_entry):
                if key not in current_pointer and i != len(filtered_entry) - 1:
                    current_pointer[key] = {}
                elif i == len(filtered_entry) - 1:
                    current_pointer[key] = record[entry]
                current_pointer = current_pointer[key]
        new_records.append(new_record)
    rb = pa.RecordBatch.from_pylist(new_records)
    return pa.Table.from_batches([rb])


def unzip_struct_array(arr: pa.ChunkedArray) -> pa.Table:
    flattened = _recursively_flatten_structs_in_array(arr.combine_chunks(), "")
    return pa.table(flattened)


def _pick_output_type(input_types):
    if not isinstance(input_types["key"], types.Const):
        return types.UnknownType()
    key = input_types["key"].val
    prop_type = input_types["self"].object_type.property_types.get(key)
    if prop_type is None:
        return types.Invalid()
    return ArrowWeaveListType(prop_type)


def rewrite_weavelist_refs(arrow_data, object_type, artifact):
    # TODO: Handle unions

    if isinstance(object_type, types.TypedDict) or isinstance(
        object_type, types.ObjectType
    ):
        prop_types = object_type.property_types
        if callable(prop_types):
            prop_types = prop_types()
        if isinstance(arrow_data, pa.Table):
            arrays = {}
            for col_name, col_type in prop_types.items():
                column = arrow_data[col_name]
                arrays[col_name] = rewrite_weavelist_refs(column, col_type, artifact)
            return pa.table(arrays)
        elif isinstance(arrow_data, pa.ChunkedArray):
            arrays = {}
            unchunked = arrow_data.combine_chunks()
            for col_name, col_type in prop_types.items():
                column = unchunked.field(col_name)
                arrays[col_name] = rewrite_weavelist_refs(column, col_type, artifact)
            return pa.StructArray.from_arrays(arrays.values(), names=arrays.keys())
        elif isinstance(arrow_data, pa.StructArray):
            arrays = {}
            for col_name, col_type in prop_types.items():
                column = arrow_data.field(col_name)
                arrays[col_name] = rewrite_weavelist_refs(column, col_type, artifact)
            return pa.StructArray.from_arrays(arrays.values(), names=arrays.keys())
        else:
            raise errors.WeaveTypeError('Unhandled type "%s"' % type(arrow_data))
    elif isinstance(object_type, types.UnionType):
        non_none_members = [
            m for m in object_type.members if not isinstance(m, types.NoneType)
        ]
        if len(non_none_members) > 1:
            raise errors.WeaveInternalError(
                "Unions not fully supported yet in Weave arrow"
            )
        return rewrite_weavelist_refs(arrow_data, types.non_none(object_type), artifact)
    elif isinstance(object_type, types.BasicType) or (
        isinstance(object_type, types.Const)
        and isinstance(object_type.val_type, types.BasicType)
    ):
        return arrow_data
    elif isinstance(object_type, types.List):
        return pa.array(rewrite_weavelist_refs(item.as_py(), object_type.object_type, artifact) for item in arrow_data)  # type: ignore

    else:
        # We have a column of refs
        new_refs = []
        for ref_str in arrow_data:
            ref_str = ref_str.as_py()
            if ":" in ref_str:
                new_refs.append(ref_str)
            else:
                ref = refs.Ref.from_local_ref(artifact, ref_str, object_type)
                new_refs.append(str(ref.uri))
        return pa.array(new_refs)


def rewrite_groupby_refs(arrow_data, group_keys, object_type, artifact):
    # TODO: Handle unions

    # hmm... we should just iterate over table columns instead!
    # This would be a nested iterate
    if isinstance(object_type, types.TypedDict) or isinstance(
        object_type, types.ObjectType
    ):
        prop_types = object_type.property_types
        if callable(prop_types):
            prop_types = prop_types()
        arrays = {}
        for group_key in group_keys:
            arrays[group_key] = arrow_data[group_key]
        for col_name, col_type in prop_types.items():
            col_name = col_name + "_list"
            column = arrow_data[col_name]
            arrays[col_name] = rewrite_groupby_refs(
                column, group_keys, col_type, artifact
            )
        return pa.table(arrays)
    elif isinstance(object_type, types.UnionType):
        if any(types.is_custom_type(m) for m in object_type.members):
            raise errors.WeaveInternalError(
                "Unions of custom types not yet support in Weave arrow"
            )
        return arrow_data
    else:
        if isinstance(object_type, types.BasicType):
            return arrow_data

        # We have a column of refs

        new_refs = []
        for ref_str_list in arrow_data:
            ref_str_list = ref_str_list.as_py()
            new_ref_str_list = []
            for ref_str in ref_str_list:
                if ":" in ref_str:
                    new_ref_str_list.append(ref_str)
                else:
                    ref = refs.LocalArtifactRef.from_local_ref(
                        artifact, ref_str, object_type
                    )
                    new_ref_str_list.append(str(ref.uri))
            new_refs.append(new_ref_str_list)
        return pa.array(new_refs)


@dataclasses.dataclass(frozen=True)
class ArrowTableGroupByType(types.Type):
    name = "ArrowTableGroupBy"

    object_type: types.Type = types.Any()
    key: types.String = types.String()

    @classmethod
    def type_of_instance(cls, obj):
        return cls(obj.object_type, obj.key_type)

    def save_instance(self, obj, artifact, name):
        if obj._artifact == artifact:
            raise errors.WeaveInternalError("not yet implemented")
        table = rewrite_weavelist_refs(obj._table, obj.object_type, obj._artifact)
        d = {
            "_table": table,
            "_groups": obj._groups,
            "_group_keys": obj._group_keys,
            "object_type": obj.object_type,
            "key_type": obj.key_type,
        }
        type_of_d = types.TypedDict(
            {
                "_table": types.union(arrow.ArrowTableType(), arrow.ArrowArrayType()),
                "_groups": types.union(arrow.ArrowTableType(), arrow.ArrowArrayType()),
                "_group_keys": types.List(types.String()),
                "object_type": types.Type(),
                "key_type": types.Type(),
            }
        )
        serializer = mappers_python.map_to_python(type_of_d, artifact)
        result_d = serializer.apply(d)

        with artifact.new_file(f"{name}.ArrowTableGroupBy.json") as f:
            json.dump(result_d, f)

    def load_instance(self, artifact, name, extra=None):
        with artifact.open(f"{name}.ArrowTableGroupBy.json") as f:
            result = json.load(f)
        type_of_d = types.TypedDict(
            {
                "_table": types.union(arrow.ArrowTableType(), arrow.ArrowArrayType()),
                "_groups": types.union(arrow.ArrowTableType(), arrow.ArrowArrayType()),
                "_group_keys": types.List(types.String()),
                "object_type": types.Type(),
                "key_type": types.Type(),
            }
        )

        mapper = mappers_python.map_from_python(type_of_d, artifact)
        res = mapper.apply(result)
        return ArrowTableGroupBy(
            res["_table"],
            res["_groups"],
            res["_group_keys"],
            res["object_type"],
            res["key_type"],
            artifact,
        )


@weave_class(weave_type=ArrowTableGroupByType)
class ArrowTableGroupBy:
    def __init__(self, _table, _groups, _group_keys, object_type, key_type, artifact):
        self._table = _table
        self._groups = _groups
        self._group_keys = _group_keys
        self.object_type = object_type
        self.key_type = key_type
        # if self.object_type is None:
        #     self.object_type = types.TypeRegistry.type_of(self._table).object_type
        self._artifact = artifact
        self._mapper = mappers_arrow.map_from_arrow(self.object_type, self._artifact)

    @op()
    def count(self) -> int:
        return len(self._groups)

    def __len__(self):
        return len(self._groups)

    @op(
        output_type=lambda input_types: ArrowTableGroupResultType(
            input_types["self"].object_type,
            input_types["self"].key,
        )
    )
    def __getitem__(self, index: int):
        try:
            row = self._groups.slice(index, 1)
        except pa.ArrowIndexError:
            return None

        if len(row) == 0:
            return None

        if self._group_keys == ["group_key"]:
            group_key = row["group_key"][0]
        else:
            row_key = row.select(self._group_keys)
            key = {}
            for col_name, column in zip(row_key.column_names, row_key.columns):
                key[col_name.removeprefix("group_key_")] = column.combine_chunks()
            group_key = pa.StructArray.from_arrays(key.values(), key.keys())[0]

        group_indexes = row["_index_list"].combine_chunks()[0].values
        group_table = self._table.take(group_indexes)

        return ArrowTableGroupResult(
            # TODO: remove as_py() from group_key. Stay in arrow!
            group_table,
            group_key.as_py(),
            self.object_type,
            self._artifact,
        )

    @op(
        input_type={
            "self": ArrowTableGroupByType(),
            "map_fn": lambda input_types: types.Function(
                {
                    "row": ArrowTableGroupResultType(
                        input_types["self"].object_type,
                        input_types["self"].key,
                    )
                },
                types.Any(),
            ),
        },
        output_type=lambda input_types: types.List(input_types["map_fn"].output_type),
    )
    def map(self, map_fn):
        return execute_fast.fast_map_fn(self, map_fn)


ArrowTableGroupByType.instance_classes = ArrowTableGroupBy
ArrowTableGroupByType.instance_class = ArrowTableGroupBy


@dataclasses.dataclass(frozen=True)
class ArrowWeaveListType(types.Type):
    name = "ArrowWeaveList"

    object_type: types.Type = types.Type()

    @classmethod
    def type_of_instance(cls, obj):
        return cls(obj.object_type)

    def save_instance(self, obj, artifact, name):
        # TODO: why do we need this check?
        if obj._artifact == artifact:
            arrow_data = obj._arrow_data
        else:
            # super().save_instance(obj, artifact, name)
            # return
            arrow_data = rewrite_weavelist_refs(
                obj._arrow_data, obj.object_type, obj._artifact
            )

        d = {"_arrow_data": arrow_data, "object_type": obj.object_type}
        type_of_d = types.TypedDict(
            {
                "_arrow_data": types.union(
                    arrow.ArrowTableType(), arrow.ArrowArrayType()
                ),
                "object_type": types.Type(),
            }
        )
        if hasattr(self, "_key"):
            d["_key"] = obj._key
            type_of_d.property_types["_key"] = self._key

        serializer = mappers_python.map_to_python(type_of_d, artifact)
        result_d = serializer.apply(d)

        with artifact.new_file(f"{name}.ArrowWeaveList.json") as f:
            json.dump(result_d, f)

    def load_instance(self, artifact, name, extra=None):
        with artifact.open(f"{name}.ArrowWeaveList.json") as f:
            result = json.load(f)
        type_of_d = types.TypedDict(
            {
                "_arrow_data": types.union(
                    arrow.ArrowTableType(), arrow.ArrowArrayType()
                ),
                "object_type": types.Type(),
            }
        )
        if hasattr(self, "_key"):
            type_of_d.property_types["_key"] = self._key

        mapper = mappers_python.map_from_python(type_of_d, artifact)
        res = mapper.apply(result)
        return self.instance_class(artifact=artifact, **res)


ArrowWeaveListObjectTypeVar = typing.TypeVar("ArrowWeaveListObjectTypeVar")


@weave_class(weave_type=ArrowWeaveListType)
class ArrowWeaveList(typing.Generic[ArrowWeaveListObjectTypeVar]):
    _arrow_data: typing.Union[pa.Table, pa.ChunkedArray, pa.Array]
    object_type: types.Type

    def __array__(self, dtype=None):
        return np.asarray(self.to_pylist())

    def __iter__(self):
        for item in self.to_pylist():
            yield self._mapper.apply(item)

    def to_pylist(self):
        if isinstance(self, graph.Node):
            return []
        return self._arrow_data.to_pylist()

    def __init__(self, _arrow_data, object_type=None, artifact=None):
        self._arrow_data = _arrow_data
        self.object_type = object_type
        if self.object_type is None:
            self.object_type = types.TypeRegistry.type_of(self._arrow_data).object_type
        self._artifact = artifact
        self._mapper = mappers_arrow.map_from_arrow(self.object_type, self._artifact)
        # TODO: construct mapper

    # TODO: doesn't belong here
    @op()
    def sum(self) -> float:
        return pa.compute.sum(self._arrow_data)

    def _count(self):
        return len(self._arrow_data)

    def __len__(self):
        return self._count()

    @op()
    def count(self) -> int:
        return self._count()

    def _get_col(self, name):
        if isinstance(self._arrow_data, pa.Table):
            col = self._arrow_data[name]
        elif isinstance(self._arrow_data, pa.ChunkedArray):
            raise NotImplementedError("TODO: implement this")
        elif isinstance(self._arrow_data, pa.StructArray):
            col = self._arrow_data.field(name)
        col_mapper = self._mapper._property_serializers[name]
        if isinstance(col_mapper, mappers_python_def.DefaultFromPy):
            return [col_mapper.apply(i.as_py()) for i in col]
        return col

    def _index(self, index):
        try:
            row = self._arrow_data.slice(index, 1)
        except IndexError:
            return None
        if not row:
            return None
        res = self._mapper.apply(row.to_pylist()[0])
        return res

    @op(output_type=lambda input_types: input_types["self"].object_type)
    def __getitem__(self, index: int):
        return self._index(index)

    @op(output_type=_pick_output_type, name="ArrowWeaveList-pickAux")
    def pick(self, key: str):
        object_type = self.object_type
        if isinstance(object_type, types.TypedDict):
            col_type = object_type.property_types[key]
        elif isinstance(object_type, types.ObjectType):
            col_type = object_type.property_types()[key]
        else:
            raise errors.WeaveInternalError(
                "unexpected type for pick: %s" % object_type
            )

        picked = (
            self._arrow_data[key]
            if not isinstance(self._arrow_data, pa.StructArray)
            else self._arrow_data.field(key)
        )
        return ArrowWeaveList(picked, col_type, self._artifact)

    @op(
        input_type={
            "self": ArrowWeaveListType(),
            "map_fn": lambda input_types: types.Function(
                {"row": input_types["self"].object_type, "index": types.Int()},
                types.Any(),
            ),
        },
        output_type=lambda input_types: ArrowWeaveListType(
            input_types["map_fn"].output_type
        ),
    )
    def map(self, map_fn):
        vectorized_map_fn = vectorize(map_fn)
        map_result_node = weave_internal.call_fn(
            vectorized_map_fn,
            {
                "row": weave_internal.make_const_node(
                    ArrowWeaveListType(self.object_type), self
                )
            },
        )

        with context.non_caching_execution_client():
            return use(map_result_node)

    def _append_column(self, name: str, data) -> "ArrowWeaveList":
        if not data:
            raise ValueError(f'Data for new column "{name}" must be nonnull.')

        new_data = self._arrow_data.append_column(name, [data])
        return ArrowWeaveList(new_data)

    def concatenate(self, other: "ArrowWeaveList") -> "ArrowWeaveList":
        arrow_data = [awl._arrow_data for awl in (self, other)]
        if (
            all([isinstance(ad, pa.ChunkedArray) for ad in arrow_data])
            and arrow_data[0].type == arrow_data[1].type
        ):
            return ArrowWeaveList(
                pa.chunked_array(arrow_data[0].chunks + arrow_data[1].chunks)
            )
        elif (
            all([isinstance(ad, pa.Table) for ad in arrow_data])
            and arrow_data[0].schema == arrow_data[1].schema
        ):
            return ArrowWeaveList(pa.concat_tables([arrow_data[0], arrow_data[1]]))
        else:
            raise ValueError(
                "Can only concatenate two ArrowWeaveLists that both contain "
                "ChunkedArrays of the same type or Tables of the same schema."
            )

    @op(
        input_type={
            "self": ArrowWeaveListType(arrow.ArrowTableType(types.Any())),
            "group_by_fn": lambda input_types: types.Function(
                {"row": input_types["self"].object_type}, types.Any()
            ),
        },
        output_type=lambda input_types: ArrowTableGroupByType(
            input_types["self"].object_type, input_types["group_by_fn"].output_type
        ),
    )
    def groupby(self, group_by_fn):
        vectorized_groupby_fn = vectorize(group_by_fn)
        group_table_node = weave_internal.call_fn(
            vectorized_groupby_fn,
            {
                "row": weave_internal.make_const_node(
                    ArrowWeaveListType(self.object_type), self
                )
            },
        )
        table = self._arrow_data

        with context.non_caching_execution_client():
            group_table = use(group_table_node)._arrow_data

        # pyarrow does not currently implement support for grouping / aggregations on keys that are
        # structs (typed Dicts). to get around this, we unzip struct columns into multiple columns, one for each
        # struct field. then we group on those columns.
        if isinstance(group_table, pa.Table):
            group_cols = []
            original_col_names = group_table.column_names
            original_group_table = group_table
            for i, colname in enumerate(group_table.column_names):
                if isinstance(group_table[colname].type, pa.StructType):
                    # convert struct columns to multiple destructured columns
                    replacement_table = unzip_struct_array(group_table[colname])
                    group_table = group_table.remove_column(i)
                    for newcol in replacement_table.column_names:
                        group_table = group_table.append_column(
                            newcol, replacement_table[newcol]
                        )
                        group_cols.append(newcol)

                else:
                    # if a column is not a struct then just use it
                    group_cols.append(colname)

        elif isinstance(group_table, (pa.ChunkedArray, pa.Array)):
            if isinstance(group_table, pa.ChunkedArray):
                group_table = group_table.combine_chunks()
            original_col_names = ["group_key"]
            group_table = pa.chunked_array(
                pa.StructArray.from_arrays([group_table], names=original_col_names)
            )
            group_table = unzip_struct_array(group_table)
            group_cols = group_table.column_names
        else:
            raise errors.WeaveInternalError(
                "Arrow groupby not yet support for map result: %s" % type(group_table)
            )

        # Serializing a large arrow table and then reading it back
        # causes it to come back with more than 1 chunk. It seems the aggregation
        # operations don't like this. It will raise a cryptic error about
        # ExecBatches need to have the same link without this combine_chunks line
        # But combine_chunks doesn't seem like the most efficient thing to do
        # either, since it'll have to concatenate everything together.
        # But this fixes the crash for now!
        # TODO: investigate this as we optimize the arrow implementation
        group_table = group_table.combine_chunks()

        group_table = group_table.append_column(
            "_index", pa.array(np.arange(len(group_table)))
        )
        grouped = group_table.group_by(group_cols)
        agged = grouped.aggregate([("_index", "list")])
        agged = _unflatten_structs_in_flattened_table(agged)

        return ArrowTableGroupBy(
            table,
            agged,
            original_col_names,
            self.object_type,
            group_by_fn.type,
            self._artifact,
        )

    @op(output_type=lambda input_types: input_types["self"])
    def offset(self, offset: int):
        return ArrowWeaveList(
            self._arrow_data.slice(offset), self.object_type, self._artifact
        )

    def _limit(self, limit: int):
        return ArrowWeaveList(
            self._arrow_data.slice(0, limit), self.object_type, self._artifact
        )

    @op(output_type=lambda input_types: input_types["self"])
    def limit(self, limit: int):
        return self._limit(limit)

    @op(
        input_type={"self": ArrowWeaveListType(types.TypedDict({}))},
        output_type=lambda input_types: ArrowWeaveListType(
            types.TypedDict(
                {
                    k: v
                    if not (types.is_list_like(v) or isinstance(v, ArrowWeaveListType))
                    else v.object_type
                    for (k, v) in input_types["self"].object_type.property_types.items()
                }
            )
        ),
    )
    def unnest(self):
        if not self or not isinstance(self.object_type, types.TypedDict):
            return self

        list_cols = []
        for k, v_type in self.object_type.property_types.items():
            if types.is_list_like(v_type):
                list_cols.append(k)
        if not list_cols:
            return self

        if isinstance(self._arrow_data, pa.StructArray):
            rb = pa.RecordBatch.from_struct_array(
                self._arrow_data
            )  # this pivots to columnar layout
            arrow_obj = pa.Table.from_batches([rb])
        else:
            arrow_obj = self._arrow_data

        # todo: make this more efficient. we shouldn't have to convert back and forth
        # from the arrow in-memory representation to pandas just to call the explode
        # function. but there is no native pyarrow implementation of this
        return pa.Table.from_pandas(
            df=arrow_obj.to_pandas().explode(list_cols), preserve_index=False
        )


ArrowWeaveListType.instance_classes = ArrowWeaveList
ArrowWeaveListType.instance_class = ArrowWeaveList


@dataclasses.dataclass(frozen=True)
class ArrowTableGroupResultType(ArrowWeaveListType):
    name = "ArrowTableGroupResult"

    _key: types.Type = types.Any()

    @classmethod
    def type_of_instance(cls, obj):
        return cls(
            obj.object_type,
            types.TypeRegistry.type_of(obj._key),
        )

    # def property_types(self):
    #     return {
    #         "_arrow_data": types.union(ArrowTableType(), ArrowArrayType()),
    #         "object_type": types.Type(),
    #         "_key": self.key,
    #     }


@weave_class(weave_type=ArrowTableGroupResultType)
class ArrowTableGroupResult(ArrowWeaveList):
    def __init__(self, _arrow_data, _key, object_type=None, artifact=None):
        self._arrow_data = _arrow_data
        self._key = _key
        self.object_type = object_type
        if self.object_type is None:
            self.object_type = types.TypeRegistry.type_of(self._table).object_type
        self._artifact = artifact
        self._mapper = mappers_arrow.map_from_arrow(self.object_type, self._artifact)

    @op(output_type=lambda input_types: input_types["self"]._key)
    def key(self):
        return self._key


ArrowTableGroupResultType.instance_classes = ArrowTableGroupResult
ArrowTableGroupResultType.instance_class = ArrowTableGroupResult


class VectorizeError(errors.WeaveBaseError):
    pass


def make_vectorized_object_constructor(constructor_op_name: str) -> None:
    constructor_op = registry_mem.memory_registry.get_op(constructor_op_name)
    if callable(constructor_op.raw_output_type):
        raise errors.WeaveInternalError(
            "Unexpected. All object type constructors have fixed return types."
        )

    type_name = constructor_op.raw_output_type.name
    vectorized_constructor_op_name = f'ArrowWeaveList-{type_name.replace("-", "_")}'
    if registry_mem.memory_registry.have_op(vectorized_constructor_op_name):
        return

    output_type = ArrowWeaveListType(constructor_op.raw_output_type)

    @op(
        name=vectorized_constructor_op_name,
        input_type={
            "attributes": ArrowWeaveListType(
                constructor_op.input_type.weave_type().property_types["attributes"]  # type: ignore
            )
        },
        output_type=output_type,
        render_info={"type": "function"},
    )
    def vectorized_constructor(attributes):
        if callable(output_type):
            ot = output_type({"attributes": types.TypeRegistry.type_of(attributes)})
        else:
            ot = output_type
        return ArrowWeaveList(attributes._arrow_data, ot.object_type)


def vectorize(
    weave_fn,
    with_respect_to: typing.Optional[typing.Iterable[graph.VarNode]] = None,
    stack_depth: int = 0,
):
    """Convert a Weave Function of T to a Weave Function of ArrowWeaveList[T]

    We walk the DAG represented by weave_fn, starting from its roots. Replace
    with_respect_to VarNodes of Type T with ArrowWeaveList[T]. Then as we
    walk up the DAG, replace OutputNodes with new op calls to whatever ops
    exist that can handle the changed input types.
    """

    # TODO: handle with_respect_to, it doesn't do anything right now.

    if stack_depth > 10:
        raise VectorizeError("Vectorize recursion depth exceeded")

    def ensure_object_constructors_created(node: graph.Node) -> graph.Node:
        if isinstance(node, graph.OutputNode):
            if node.from_op.name.startswith("objectConstructor-"):
                make_vectorized_object_constructor(node.from_op.name)
        return node

    def expand_nodes(node: graph.Node) -> graph.Node:
        if isinstance(node, graph.OutputNode):
            inputs = node.from_op.inputs
            if node.from_op.name == "number-pybin":
                bin_fn = weave_internal.use(inputs["bin_fn"])
                in_ = inputs["in_"]
                return weave_internal.call_fn(bin_fn, {"row": in_})  # type: ignore
        return node

    def convert_node(node):
        if isinstance(node, graph.OutputNode):
            inputs = node.from_op.inputs
            # since dict takes OpVarArgs(typing.Any()) as input, it will always show up
            # as a candidate for vectorizing itself. We don't want to do that, so we
            # explicitly force using ArrowWeaveList-dict instead.
            if node.from_op.name == "dict":
                op = registry_mem.memory_registry.get_op(
                    "ArrowWeaveList-vectorizedDict"
                )
                return op.lazy_call(**inputs)
            elif node.from_op.name == "Object-__getattr__":
                op = registry_mem.memory_registry.get_op(
                    "ArrowWeaveListObject-__vectorizedGetattr__"
                )
                return op.lazy_call(**inputs)
            else:
                # Get a version of op that can handle vectorized (ArrowWeaveList) inputs
                op = dispatch.get_op_for_input_types(
                    node.from_op.name, [], {k: v.type for k, v in inputs.items()}
                )
                if op:
                    # We have a vectorized implementation of this op already.
                    final_inputs = {
                        k: v for k, v in zip(op.input_type.arg_types, inputs.values())
                    }
                    return op.lazy_call(**final_inputs)
                else:
                    # see if weave function can be expanded and vectorized
                    op_def = registry_mem.memory_registry.get_op(node.from_op.name)
                    if op_def.weave_fn is None:
                        # this could raise
                        op_def.weave_fn = weavify.op_to_weave_fn(op_def)
                    vectorized = vectorize(op_def.weave_fn, stack_depth=stack_depth + 1)
                    return weave_internal.call_fn(vectorized, inputs)
        elif isinstance(node, graph.VarNode):
            # Vectorize variable
            # NOTE: This is the only line that is specific to the arrow
            #     implementation (uses ArrowWeaveListType). Everything
            #     else will work for other List types, as long as there is
            #     a set of ops declared that can handle the new types.
            if with_respect_to is None or any(
                node is wrt_node for wrt_node in with_respect_to
            ):
                return graph.VarNode(ArrowWeaveListType(node.type), node.name)
            return node
        elif isinstance(node, graph.ConstNode):
            return node

    weave_fn = graph.map_nodes(weave_fn, ensure_object_constructors_created)
    weave_fn = graph.map_nodes(weave_fn, expand_nodes)
    return graph.map_nodes(weave_fn, convert_node)


def dataframe_to_arrow(df):
    return ArrowWeaveList(pa.Table.from_pandas(df))


# This will be a faster version fo to_arrow (below). Its
# used in op file-table, to convert from a wandb Table to Weave
# (that code is very experimental and not totally working yet)
def to_arrow_from_list_and_artifact(obj, object_type, artifact):
    # Get what the parquet type will be.
    mapper = mappers_arrow.map_to_arrow(object_type, artifact)
    pyarrow_type = mapper.result_type()

    if pa.types.is_struct(pyarrow_type):
        fields = list(pyarrow_type)
        schema = pa.schema(fields)
        arrow_obj = pa.Table.from_pylist(obj, schema=schema)
    else:
        arrow_obj = pa.array(obj, pyarrow_type)
    weave_obj = ArrowWeaveList(arrow_obj, object_type, artifact)
    return weave_obj


def to_arrow(obj, wb_type=None):
    if wb_type is None:
        wb_type = types.TypeRegistry.type_of(obj)
    artifact = artifacts_local.LocalArtifact("to-arrow-%s" % wb_type.name)
    if isinstance(wb_type, types.List):
        object_type = wb_type.object_type

        # Convert to arrow, serializing Custom objects to the artifact
        mapper = mappers_arrow.map_to_arrow(object_type, artifact)
        pyarrow_type = mapper.result_type()
        py_objs = (mapper.apply(o) for o in obj)

        # TODO: do I need this branch? Does it work now?
        # if isinstance(wb_type.object_type, types.ObjectType):
        #     arrow_obj = pa.array(py_objs, pyarrow_type)
        arrow_obj = pa.array(py_objs, pyarrow_type)
        weave_obj = ArrowWeaveList(arrow_obj, object_type, artifact)

        # Save the weave object to the artifact
        ref = storage.save(weave_obj, artifact=artifact)

        return ref.obj

    raise errors.WeaveInternalError("to_arrow not implemented for: %s" % obj)
