import typing
import dataclasses
import json
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

py_type = type

from ..api import op, weave_class, type, use, OpVarArgs
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
from . import _dict_utils


class ArrowArrayVectorizer:
    def __init__(self, arr):
        self.arr = arr

    def _get_col(self, key):
        col = self.arr._get_col(key)
        if isinstance(col, list):
            return col
        return ArrowArrayVectorizer(col)

    def items(self):
        for col_name in self.arr._arrow_data.column_names:
            yield col_name, self._get_col(col_name)

    def floor(self):
        return ArrowArrayVectorizer(pc.floor(self.arr))

    def __getattr__(self, attr):
        return self._get_col(attr)

    def __len__(self):
        return len(self.arr)

    def __getitem__(self, key):
        return ArrowArrayVectorizer(self.arr[key])

    def __add__(self, other):
        if isinstance(other, ArrowArrayVectorizer):
            other = other.arr
        return ArrowArrayVectorizer(pc.add(self.arr, other))

    def __sub__(self, other):
        if isinstance(other, ArrowArrayVectorizer):
            other = other.arr
        return ArrowArrayVectorizer(pc.subtract(self.arr, other))

    def __gt__(self, other):
        return ArrowArrayVectorizer(pc.greater(self.arr, other))

    def __mul__(self, other):
        if isinstance(other, ArrowArrayVectorizer):
            other = other.arr
        return ArrowArrayVectorizer(pc.multiply(self.arr, other))

    def __truediv__(self, other):
        if isinstance(other, ArrowArrayVectorizer):
            other = other.arr
        return ArrowArrayVectorizer(pc.divide(self.arr, other))

    def __pow__(self, other):
        if isinstance(other, ArrowArrayVectorizer):
            other = other.arr
        return ArrowArrayVectorizer(pc.power(self.arr, other))


def unzip_struct_array(arr: pa.ChunkedArray) -> pa.Table:
    flattened = arr.flatten()
    col_names = [field.name for field in arr.type]
    return pa.table(dict(zip(col_names, flattened)))


def mapped_fn_to_arrow(arrow_table, node):
    if isinstance(node, graph.ConstNode):
        return node.val
    elif isinstance(node, graph.OutputNode):
        op_name = graph.op_full_name(node.from_op)
        inputs = {
            k: mapped_fn_to_arrow(arrow_table, i)
            for k, i in node.from_op.inputs.items()
        }
        if op_name == "pick":
            return inputs["obj"]._get_col(inputs["key"])
        elif op_name == "typedDict-pick":
            return inputs["self"]._get_col(inputs["key"])
        elif op_name == "dict":
            for k, v in inputs.items():
                if isinstance(v, ArrowArrayVectorizer):
                    inputs[k] = v.arr
                if np.isscalar(v):
                    inputs[k] = [v] * len(arrow_table)
            return pa.table(inputs)
        elif op_name == "merge":
            lhs = inputs["lhs"]
            rhs = inputs["rhs"]
            t = rhs
            for col_name, column in zip(lhs.column_names, lhs.columns):
                t.append_column(col_name, column)
            return t
        op_def = registry_mem.memory_registry.get_op(op_name)
        if list(inputs.keys())[0] == "self" and isinstance(
            list(inputs.values())[0], list
        ):
            import copy

            row_inputs = copy.copy(inputs)
            res = []
            for row in list(inputs.values())[0]:
                row_inputs["self"] = row
                res.append(op_def.resolve_fn(**row_inputs))
            return ArrowArrayVectorizer(pa.array(res))
        result = op_def.resolve_fn(**inputs)
        if isinstance(node.type, types.ObjectType):
            cols = {}
            for k in node.type.property_types():
                cols[k] = getattr(result, k)
                if isinstance(cols[k], ArrowArrayVectorizer):
                    cols[k] = cols[k].arr
            return pa.table(cols)
        return result
    elif isinstance(node, graph.VarNode):
        if node.name == "row":
            if (
                isinstance(arrow_table, ArrowWeaveList)
                and not isinstance(arrow_table._arrow_data, pa.StructArray)
                and (
                    isinstance(arrow_table._arrow_data, pa.ChunkedArray)
                    or isinstance(arrow_table._arrow_data, pa.Array)
                )
            ):
                return ArrowArrayVectorizer(arrow_table._arrow_data)

            return ArrowArrayVectorizer(arrow_table)
        elif node.name == "index":
            return np.arange(arrow_table._count())
        raise Exception("unhandled var name", node.name)


def arrow_type_to_weave_type(pa_type) -> types.Type:
    if pa_type == pa.string():
        return types.String()
    elif pa_type == pa.int64() or pa_type == pa.int32():
        return types.Int()
    elif pa_type == pa.float64():
        return types.Float()
    elif pa_type == pa.bool_():
        return types.Boolean()
    elif pa.types.is_list(pa_type):
        return types.List(arrow_type_to_weave_type(pa_type.value_field.type))
    elif pa.types.is_struct(pa_type):
        return types.TypedDict(
            {f.name: arrow_type_to_weave_type(f.type) for f in pa_type}
        )
    raise errors.WeaveTypeError(
        "Type conversion not implemented for arrow type: %s" % pa_type
    )


@dataclasses.dataclass(frozen=True)
class ArrowArrayType(types.Type):
    instance_classes = [pa.ChunkedArray, pa.ExtensionArray, pa.Array]
    name = "ArrowArray"

    object_type: types.Type = types.Any()

    @classmethod
    def type_of_instance(cls, obj: pa.Array):
        return cls(arrow_type_to_weave_type(obj.type))

    def save_instance(self, obj, artifact, name):
        # Could use the arrow format instead. I think it supports memory
        # mapped random access, but is probably larger.
        # See here: https://arrow.apache.org/cookbook/py/io.html#saving-arrow-arrays-to-disk
        # TODO: what do we want?
        table = pa.table({"arr": obj})
        with artifact.new_file(f"{name}.parquet", binary=True) as f:
            pq.write_table(table, f)

    def load_instance(self, artifact, name, extra=None):
        with artifact.open(f"{name}.parquet", binary=True) as f:
            return pq.read_table(f)["arr"].combine_chunks()


@dataclasses.dataclass(frozen=True)
class ArrowTableType(types.Type):
    instance_classes = pa.Table
    name = "ArrowTable"

    object_type: types.Type = types.Any()

    @classmethod
    def type_of_instance(cls, obj: pa.Table):
        obj_prop_types = {}
        for field in obj.schema:
            obj_prop_types[field.name] = arrow_type_to_weave_type(field.type)
        return cls(types.TypedDict(obj_prop_types))

    def save_instance(self, obj, artifact, name):
        with artifact.new_file(f"{name}.parquet", binary=True) as f:
            pq.write_table(obj, f)

    def load_instance(self, artifact, name, extra=None):
        with artifact.open(f"{name}.parquet", binary=True) as f:
            return pq.read_table(f)


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
                "_table": types.union(ArrowTableType(), ArrowArrayType()),
                "_groups": types.union(ArrowTableType(), ArrowArrayType()),
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
                "_table": types.union(ArrowTableType(), ArrowArrayType()),
                "_groups": types.union(ArrowTableType(), ArrowArrayType()),
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


# It seems like this should inherit from types.ListType...

# Alright. The issue is...
#   we're saving ArrowWeaveList inside of a Table object.
#   so we're using mappers to save ArrowWeaveList instead of the custom
#   save_instance implementation below.
#
# What we actually want here:
#   - ArrowWeaveList can be represented as a TypedDict, so we want to
#     convert to that so it can be nested (like ObjectType)
#   - But we want to provide custom saving logic so we can convert inner refs
#     in a totally custom way.
#   - We have custom type_of_instance logic


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
                "_arrow_data": types.union(ArrowTableType(), ArrowArrayType()),
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
                "_arrow_data": types.union(ArrowTableType(), ArrowArrayType()),
                "object_type": types.Type(),
            }
        )
        if hasattr(self, "_key"):
            type_of_d.property_types["_key"] = self._key

        mapper = mappers_python.map_from_python(type_of_d, artifact)
        res = mapper.apply(result)
        # TODO: This won't work for Grouped result!
        return ArrowWeaveList(res["_arrow_data"], res["object_type"], artifact)


ArrowWeaveListObjectTypeVar = typing.TypeVar("ArrowWeaveListObjectTypeVar")


@weave_class(weave_type=ArrowWeaveListType)
class ArrowWeaveList(typing.Generic[ArrowWeaveListObjectTypeVar]):
    _arrow_data: typing.Union[pa.Table, pa.ChunkedArray, pa.Array]
    object_type: types.Type

    def __array__(self, dtype=None):
        return np.asarray(self.to_pylist())

    def __iter__(self):
        return iter(self.to_pylist())

    def to_pylist(self):
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
        res = mapped_fn_to_arrow(self, map_fn)
        if isinstance(res, ArrowArrayVectorizer):
            res = res.arr
        return ArrowWeaveList(res, map_fn.type, self._artifact)

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
            "self": ArrowWeaveListType(ArrowTableType(types.Any())),
            "group_by_fn": lambda input_types: types.Function(
                {"row": input_types["self"].object_type}, types.Any()
            ),
        },
        output_type=lambda input_types: ArrowTableGroupByType(
            input_types["self"].object_type, input_types["group_by_fn"].output_type
        ),
    )
    def groupby(self, group_by_fn):
        if isinstance(self._arrow_data, pa.ChunkedArray):
            return self._groupby_table(
                pa.table({"self": self._arrow_data}), group_by_fn
            )
        else:
            return self._groupby_table(self._arrow_data, group_by_fn)

    def _groupby_table(self, table, group_by_fn):
        group_table = mapped_fn_to_arrow(self, group_by_fn)
        if isinstance(group_table, ArrowArrayVectorizer):
            group_table = group_table.arr

        has_struct = False

        # pyarrow does not currently implement support for grouping / aggregations on keys that are
        # structs (typed Dicts). to get around this, we unzip struct columns into multiple columns, one for each
        # struct field. then we group on those columns.
        if isinstance(group_table, pa.Table):
            group_cols = []
            original_col_names = group_table.column_names
            original_group_table = group_table
            for i, colname in enumerate(group_table.column_names):
                if isinstance(group_table[colname].type, pa.StructType):
                    has_struct = True
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
            if isinstance(group_table, pa.Array):
                group_table = pa.chunked_array([group_table])
            original_group_table = pa.table({"group_key": group_table})
            original_col_names = ["group_key"]
            if isinstance(group_table.type, pa.StructType):
                has_struct = True
                group_table = unzip_struct_array(group_table)
                group_cols = group_table.column_names
            else:
                group_table = original_group_table
                group_cols = original_col_names
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

        if has_struct:
            # after grouping, re-create the grouped table using the correct key
            index_list = agged["_index_list"]
            cols = {}
            for colname in original_col_names:
                if isinstance(original_group_table[colname].type, pa.StructType):
                    col = pa.array(
                        [
                            {
                                struct_key.name: agged[struct_key.name][i].as_py()
                                for struct_key in original_group_table[colname].type
                            }
                            for i in range(len(index_list))
                        ]
                    )
                else:
                    col = agged[colname]
                cols[colname] = col
            agged = pa.table({"_index_list": index_list, **cols})

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
                    k: v if not types.is_list_like(v) else v.object_type
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


@op(
    name="ArrowWeaveList-vectorizedDict",
    input_type=OpVarArgs(types.List(types.Any())),
    output_type=lambda input_types: ArrowWeaveListType(
        types.TypedDict(
            {p_name: p_type.object_type for (p_name, p_type) in input_types.items()}
        )
    ),
)
def arrow_dict_(**d):
    names, arrays = list(zip(*d.items()))
    arrays = [
        a._arrow_data.combine_chunks()
        if isinstance(a._arrow_data, pa.ChunkedArray)
        else a._arrow_data
        for a in arrays
    ]  # convert from ArrowWeaveList -> arrow
    arrow_obj = pa.StructArray.from_arrays(arrays=arrays, names=names)
    return ArrowWeaveList(arrow_obj)


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


@dataclasses.dataclass(frozen=True)
class ArrowWeaveListNumberType(ArrowWeaveListType):
    # TODO: This should not be assignable via constructor. It should be
    #    a static property type at this point.
    name = "ArrowWeaveListNumber"
    object_type: types.Type = types.Number()


@weave_class(weave_type=ArrowWeaveListNumberType)
class ArrowWeaveListNumber(ArrowWeaveList):
    object_type = types.Number()

    # TODO: weirdly need to name this "<something>-add" since that's what the base
    # Number op does. But we'd like to get rid of that requirement so we don't
    # need name= for any ops!
    @op(name="ArrowWeaveListNumber-add")
    def __add__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[float]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.add(self._arrow_data, other), types.Number())

    @op(name="ArrowWeaveListNumber-mult")
    def __mul__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[float]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.multiply(self._arrow_data, other), types.Number())

    @op(name="ArrowWeaveListNumber-div")
    def __truediv__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[float]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.divide(self._arrow_data, other), types.Number())

    @op(name="ArrowWeaveListNumber-sub")
    def __sub__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[float]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.subtract(self._arrow_data, other), types.Number())

    @op(name="ArrowWeaveListNumber-powBinary")
    def __pow__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[float]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.power(self._arrow_data, other), types.Number())

    @op(name="ArrowWeaveListNumber-notEqual")
    def __ne__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.not_equal(self._arrow_data, other), types.Boolean())

    @op(name="ArrowWeaveListNumber-equal")
    def __eq__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.equal(self._arrow_data, other), types.Boolean())

    @op(name="ArrowWeaveListNumber-greater")
    def __gt__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.greater(self._arrow_data, other), types.Boolean())

    @op(name="ArrowWeaveListNumber-greaterEqual")
    def __ge__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(
            pc.greater_equal(self._arrow_data, other), types.Boolean()
        )

    @op(name="ArrowWeaveListNumber-less")
    def __lt__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.less(self._arrow_data, other), types.Boolean())

    @op(name="ArrowWeaveListNumber-lessEqual")
    def __le__(
        self, other: typing.Union[float, ArrowWeaveList[float]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.less_equal(self._arrow_data, other), types.Boolean())

    @op(name="ArrowWeaveListNumber-negate")
    def __neg__(self) -> ArrowWeaveList[float]:
        return ArrowWeaveList(pc.negate(self._arrow_data), types.Number())

    # todo: fix op decorator to not require name here,
    # these names are needed because the base class also has an op called floor.
    # also true for ceil below
    @op(name="ArrowWeaveListNumber-floor")
    def floor(self) -> ArrowWeaveList[float]:
        return ArrowWeaveList(pc.floor(self._arrow_data), types.Number())

    @op(name="ArrowWeaveListNumber-ceil")
    def ceil(self) -> ArrowWeaveList[float]:
        return ArrowWeaveList(pc.ceil(self._arrow_data), types.Number())


@dataclasses.dataclass(frozen=True)
class ArrowWeaveListStringType(ArrowWeaveListType):
    # TODO: This should not be assignable via constructor. It should be
    #    a static property type at this point.
    object_type: types.Type = types.String()
    name = "ArrowWeaveListString"


def _concatenate_strings(
    left: ArrowWeaveList[str], right: typing.Union[str, ArrowWeaveList[str]]
) -> ArrowWeaveList[str]:
    if isinstance(right, ArrowWeaveList):
        right = right._arrow_data
    return ArrowWeaveList(
        pc.binary_join_element_wise(left._arrow_data, right, ""), types.String()
    )


@weave_class(weave_type=ArrowWeaveListStringType)
class ArrowWeaveListString(ArrowWeaveList):
    object_type = types.String()

    @op(name="ArrowWeaveListString-equal")
    def __eq__(
        self, other: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.equal(self._arrow_data, other), types.Boolean())

    @op(name="ArrowWeaveListString-notEqual")
    def __ne__(
        self, other: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            other = other._arrow_data
        return ArrowWeaveList(pc.not_equal(self._arrow_data, other), types.Boolean())

    @op(name="ArrowWeaveListString-contains")
    def __contains__(
        self, other: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            return ArrowWeaveList(
                pa.array(
                    other_item.as_py() in my_item.as_py()
                    for my_item, other_item in zip(self._arrow_data, other._arrow_data)
                )
            )
        return ArrowWeaveList(
            pc.match_substring(self._arrow_data, other), types.Boolean()
        )

    # TODO: fix
    @op(name="ArrowWeaveListString-in")
    def in_(
        self, other: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(other, ArrowWeaveList):
            return ArrowWeaveList(
                pa.array(
                    my_item.as_py() in other_item.as_py()
                    for my_item, other_item in zip(self._arrow_data, other._arrow_data)
                )
            )
        return ArrowWeaveList(
            # this has to be a python loop because the second argument to match_substring has to be a scalar string
            pa.array(item.as_py() in other for item in self._arrow_data),
            types.Boolean(),
        )

    @op(name="ArrowWeaveListString-len")
    def len(self) -> ArrowWeaveList[int]:
        return ArrowWeaveList(pc.binary_length(self._arrow_data), types.Int())

    @op(name="ArrowWeaveListString-add")
    def __add__(
        self, other: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[str]:
        return _concatenate_strings(self, other)

    # todo: remove this explicit name, it shouldn't be needed
    @op(name="ArrowWeaveListString-append")
    def append(
        self, other: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[str]:
        return _concatenate_strings(self, other)

    @op(name="ArrowWeaveListString-prepend")
    def prepend(
        self, other: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[str]:
        if isinstance(other, str):
            other = ArrowWeaveList(
                pa.array([other] * len(self._arrow_data)), types.String()
            )
        return _concatenate_strings(other, self)

    @op(name="ArrowWeaveListString-split")
    def split(
        self, pattern: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[list[str]]:
        if isinstance(pattern, str):
            return ArrowWeaveList(
                pc.split_pattern(self._arrow_data, pattern), types.List(types.String())
            )
        return ArrowWeaveList(
            pa.array(
                self._arrow_data[i].as_py().split(pattern._arrow_data[i].as_py())
                for i in range(len(self._arrow_data))
            ),
            types.List(types.String()),
        )

    @op(name="ArrowWeaveListString-partition")
    def partition(
        self, sep: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[list[str]]:
        return ArrowWeaveList(
            pa.array(
                self._arrow_data[i]
                .as_py()
                .partition(sep if isinstance(sep, str) else sep._arrow_data[i].as_py())
                for i in range(len(self._arrow_data))
            ),
            types.List(types.String()),
        )

    @op(name="ArrowWeaveListString-startsWith")
    def startswith(
        self, prefix: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(prefix, str):
            return ArrowWeaveList(
                pc.starts_with(self._arrow_data, prefix),
                types.Boolean(),
            )
        return ArrowWeaveList(
            pa.array(
                s.as_py().startswith(p.as_py())
                for s, p in zip(self._arrow_data, prefix._arrow_data)
            ),
            types.Boolean(),
        )

    @op(name="ArrowWeaveListString-endsWith")
    def endswith(
        self, suffix: typing.Union[str, ArrowWeaveList[str]]
    ) -> ArrowWeaveList[bool]:
        if isinstance(suffix, str):
            return ArrowWeaveList(
                pc.ends_with(self._arrow_data, suffix),
                types.Boolean(),
            )
        return ArrowWeaveList(
            pa.array(
                s.as_py().endswith(p.as_py())
                for s, p in zip(self._arrow_data, suffix._arrow_data)
            ),
            types.Boolean(),
        )

    @op(name="ArrowWeaveListString-isAlpha")
    def isalpha(self) -> ArrowWeaveList[bool]:
        return ArrowWeaveList(pc.ascii_is_alpha(self._arrow_data), types.Boolean())

    @op(name="ArrowWeaveListString-isNumeric")
    def isnumeric(self) -> ArrowWeaveList[bool]:
        return ArrowWeaveList(pc.ascii_is_decimal(self._arrow_data), types.Boolean())

    @op(name="ArrowWeaveListString-isAlnum")
    def isalnum(self) -> ArrowWeaveList[bool]:
        return ArrowWeaveList(pc.ascii_is_alnum(self._arrow_data), types.Boolean())

    @op(name="ArrowWeaveListString-lower")
    def lower(self) -> ArrowWeaveList[str]:
        return ArrowWeaveList(pc.ascii_lower(self._arrow_data), types.String())

    @op(name="ArrowWeaveListString-upper")
    def upper(self) -> ArrowWeaveList[str]:
        return ArrowWeaveList(pc.ascii_upper(self._arrow_data), types.String())

    @op(name="ArrowWeaveListString-slice")
    def slice(self, begin: int, end: int) -> ArrowWeaveList[str]:
        return ArrowWeaveList(
            pc.utf8_slice_codeunits(self._arrow_data, begin, end), types.String()
        )

    @op(name="ArrowWeaveListString-replace")
    def replace(self, pattern: str, replacement: str) -> ArrowWeaveList[str]:
        return ArrowWeaveList(
            pc.replace_substring(self._arrow_data, pattern, replacement),
            types.String(),
        )

    # @op(name="string-findAll")
    # def findAll(str: str, sub: str) -> list[int]:  # type: ignore
    #     return str.find(sub)

    @op(name="ArrowWeaveListString-strip")
    def strip(self) -> ArrowWeaveList[str]:
        return ArrowWeaveList(pc.utf8_trim_whitespace(self._arrow_data), types.String())

    @op(name="ArrowWeaveListString-lStrip")
    def lstrip(self) -> ArrowWeaveList[str]:
        return ArrowWeaveList(
            pc.utf8_ltrim_whitespace(self._arrow_data), types.String()
        )

    @op(name="ArrowWeaveListString-rStrip")
    def rstrip(self) -> ArrowWeaveList[str]:
        return ArrowWeaveList(
            pc.utf8_rtrim_whitespace(self._arrow_data), types.String()
        )


class VectorizeError(errors.WeaveBaseError):
    pass


@dataclasses.dataclass(frozen=True)
class ArrowWeaveListTypedDictType(ArrowWeaveListType):
    # TODO: This should not be assignable via constructor. It should be
    #    a static property type at this point.
    object_type: types.Type = types.TypedDict({})


@weave_class(weave_type=ArrowWeaveListTypedDictType)
class ArrowWeaveListTypedDict(ArrowWeaveList):
    object_type = types.TypedDict({})
    _arrow_data: pa.StructArray

    @op(
        name="ArrowWeaveListTypedDict-pick",
        output_type=lambda input_types: ArrowWeaveListType(
            _dict_utils.typeddict_pick_output_type(
                {"self": input_types["self"].object_type, "key": input_types["key"]}
            )
        ),
    )
    def pick(self, key: str):
        object_type = _dict_utils.typeddict_pick_output_type(
            {"self": self.object_type, "key": types.Const(types.String(), key)}
        )
        return ArrowWeaveList(self._arrow_data.field(key), object_type, self._artifact)

    @op(
        name="ArrowWeaveListTypedDict-merge",
        input_type={
            "self": ArrowWeaveListTypedDictType(),
            "other": ArrowWeaveListTypedDictType(),
        },
        output_type=lambda input_types: ArrowWeaveListType(
            _dict_utils.typeddict_merge_output_type(
                {
                    "self": input_types["self"].object_type,
                    "other": input_types["other"].object_type,
                }
            )
        ),
    )
    def merge(self, other):
        self_keys = set(self.object_type.property_types.keys())
        other_keys = set(other.object_type.property_types.keys())
        common_keys = self_keys.intersection(other_keys)

        field_names_to_arrays: dict[str, pa.Array] = {
            key: arrow_weave_list._arrow_data.field(key)
            for arrow_weave_list in (self, other)
            for key in arrow_weave_list.object_type.property_types
        }

        # update field names and arrays with merged dicts

        for key in common_keys:
            if isinstance(self.object_type.property_types[key], types.TypedDict):
                self_sub_awl = ArrowWeaveList(
                    self._arrow_data.field(key), self.object_type.property_types[key]
                )
                other_sub_awl = ArrowWeaveList(
                    other._arrow_data.field(key), other.object_type.property_types[key]
                )
                merged = use(ArrowWeaveListTypedDict.merge(self_sub_awl, other_sub_awl))._arrow_data  # type: ignore
                field_names_to_arrays[key] = merged

        field_names, arrays = tuple(zip(*field_names_to_arrays.items()))

        return ArrowWeaveList(
            pa.StructArray.from_arrays(arrays=arrays, names=field_names),  # type: ignore
            _dict_utils.typeddict_merge_output_type(
                {"self": self.object_type, "other": other.object_type}
            ),
            self._artifact,
        )


def vectorize(weave_fn, with_respect_to=None):
    """Convert a Weave Function of T to a Weave Function of ArrowWeaveList[T]

    We walk the DAG represented by weave_fn, starting from its roots. Replace
    with_respect_to VarNodes of Type T with ArrowWeaveList[T]. Then as we
    walk up the DAG, replace OutputNodes with new op calls to whatever ops
    exist that can handle the changed input types.
    """

    # TODO: handle with_respect_to, it doesn't do anything right now.

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
            else:
                op = dispatch.get_op_for_input_types(
                    node.from_op.name, [], {k: v.type for k, v in inputs.items()}
                )
                if op:
                    # Rename inputs to match op, ie, call by position...
                    # Hmm, need to centralize this behavior
                    # TODO
                    final_inputs = {
                        k: v for k, v in zip(op.input_type.arg_types, inputs.values())
                    }
                    return op.lazy_call(**final_inputs)
            raise VectorizeError(
                "Can't vectorize, no op for: %s %s" % (node.from_op.name, inputs)
            )
        elif isinstance(node, graph.VarNode):
            # Vectorize variable
            # TODO: currently replaces all Var Nodes blindly!
            # NOTE: This is the only line that is specific to the arrow
            #     implementation (uses ArrowWeaveListType). Everything
            #     else will work for other List types, as long as there is
            #     a set of ops declared that can handle the new types.
            return graph.VarNode(ArrowWeaveListType(node.type), node.name)
        elif isinstance(node, graph.ConstNode):
            return node

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
