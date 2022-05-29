import typing
import dataclasses
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from .. import weave_internal

from ..api import op, weave_class
from .. import weave_types as types
from .. import graph
from .. import errors
from .. import registry_mem


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

    def __mult__(self, other):
        if isinstance(other, ArrowArrayVectorizer):
            other = other.arr
        return ArrowArrayVectorizer(pc.divide(self.arr, other))

    def __truediv__(self, other):
        if isinstance(other, ArrowArrayVectorizer):
            other = other.arr
        return ArrowArrayVectorizer(pc.divide(self.arr, other))

    def __pow__(self, other):
        if isinstance(other, ArrowArrayVectorizer):
            other = other.arr
        return ArrowArrayVectorizer(pc.power(self.arr, other))


def mapped_fn_to_arrow(arrow_table, node):
    if isinstance(node, graph.ConstNode):
        return node.val
    elif isinstance(node, graph.OutputNode):
        op_name = graph.opname_without_version(node.from_op)
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
            if isinstance(arrow_table, ArrowWeaveList) and isinstance(
                arrow_table._arrow_data, pa.ChunkedArray
            ):
                return ArrowArrayVectorizer(arrow_table._arrow_data)

            return ArrowArrayVectorizer(arrow_table)
        elif node.name == "index":
            return np.arange(len(arrow_table))
        raise Exception("unhandled var name", node.name)


def arrow_type_to_weave_type(pa_type) -> types.Type:
    if pa_type == pa.string():
        return types.String()
    elif pa_type == pa.int64():
        return types.Int()
    elif pa_type == pa.float64():
        return types.Float()
    # elif pa.types.is_list(field.type):
    #     return types.List(arrow_field_weave_type(field.type.value_field))
    raise errors.WeaveTypeError(
        "Type conversion not implemented for arrow type: %s" % pa_type
    )


@dataclasses.dataclass
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
            return pq.read_table(f)["arr"]


@dataclasses.dataclass
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


def index_output_type(input_types):
    # THIS IS NO GOOD
    # TODO: need to fix Const type so we don't need this.
    self_type = input_types["self"]
    if isinstance(self_type, types.Const):
        return self_type.val_type.object_type
    else:
        return self_type.object_type


def pick_output_type(input_types):
    if not isinstance(input_types["key"], types.Const):
        return types.UnknownType()
    key = input_types["key"].val
    prop_type = input_types["self"].object_type.property_types.get(key)
    if prop_type is None:
        return types.Invalid()
    return ArrowWeaveListType(prop_type)


def map_output_type(input_types):
    object_type = input_types["map_fn"].output_type
    return ArrowWeaveListType(object_type)


@dataclasses.dataclass
class ArrowTableGroupByType(types.ObjectType):
    name = "ArrowTableGroupBy"

    object_type: types.Type = types.Any()
    key: types.String = types.String()

    @classmethod
    def type_of_instance(cls, obj):
        table_object_type = types.TypeRegistry.type_of(obj._table).object_type
        key_prop_types = {}
        group_prop_types = {}
        for k, t in table_object_type.property_types.items():
            if k in obj._group_keys:
                key_prop_types[k] = t
            else:
                group_prop_types[k] = t
        return cls(types.TypedDict(group_prop_types), types.TypedDict(key_prop_types))

    def property_types(self):
        return {
            "_table": ArrowTableType(self.object_type),
            "_group_keys": types.List(types.String()),
        }


@weave_class(weave_type=ArrowTableGroupByType)
class ArrowTableGroupBy:
    def __init__(self, _table, _group_keys, object_type, artifact):
        self._table = _table
        self._group_keys = _group_keys
        self.object_type = object_type
        if self.object_type is None:
            self.object_type = types.TypeRegistry.type_of(self._table).object_type
        self._artifact = artifact

    @op()
    def count(self) -> int:
        return len(self._table)

    @op(
        output_type=lambda input_types: ArrowTableGroupResultType(
            input_types["self"].object_type,
            input_types["self"].key,
        )
    )
    def __getitem__(self, index: int):
        try:
            row = self._table.slice(index, 1)
        except pa.ArrowIndexError:
            return None

        if self._group_keys == ["group_key"]:
            group_key = row["group_key"][0]
        else:
            row_key = row.select(self._group_keys)
            key = {}
            for col_name, column in zip(row_key.column_names, row_key.columns):
                key[col_name.removeprefix("group_key_")] = column.combine_chunks()
            group_key = pa.StructArray.from_arrays(key.values(), key.keys())[0]
        # key_struct = pa.scalar(key)  # , pa.struct(key_type))

        row_group = row.drop(self._group_keys)
        group = {}
        for col_name, column in zip(row_group.column_names, row_group.columns):
            group[col_name.removesuffix("_list")] = column[0].values
        group_table = pa.table(group)

        return ArrowTableGroupResult(
            group_table, group_key, self.object_type, self._artifact
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
        calls = []
        for i in range(self.count.resolve_fn(self)):
            row = self.__getitem__.resolve_fn(self, i)
            calls.append(
                weave_internal.call_fn(
                    map_fn,
                    {
                        "row": graph.ConstNode(types.Any(), row),
                        "index": graph.ConstNode(types.Number(), i),
                    },
                )
            )
        result = weave_internal.use_internal(calls)
        return result


ArrowTableGroupByType.instance_classes = ArrowTableGroupBy
ArrowTableGroupByType.instance_class = ArrowTableGroupBy


# It seems like this should inherit from types.ListType...
@dataclasses.dataclass
class ArrowWeaveListType(types.ObjectType):
    name = "ArrowWeaveList"

    object_type: types.Type = types.Type()

    @classmethod
    def type_of_instance(cls, obj):
        return cls(obj.object_type)

    def property_types(self):
        return {
            "_arrow_data": types.union(ArrowTableType(), ArrowArrayType()),
            "object_type": types.Type(),
        }

    # def save_instance(self, obj, artifact, name):
    #     super().save_instance(obj, artifact, name)
    #     mapper = mappers_arrow.map_to_arrow(self.object_type, artifact)
    #     if obj._artifact._version:
    #         for i in range(obj._count()):
    #             mapper.apply(ArrowArrayVectorizer(obj._index(i)))


@weave_class(weave_type=ArrowWeaveListType)
class ArrowWeaveList:
    _arrow_data: typing.Union[pa.Table, pa.ChunkedArray]

    def to_pylist(self):
        return self._arrow_data.to_pylist()

    def __init__(self, _arrow_data, object_type=None, artifact=None):
        self._arrow_data = _arrow_data
        self.object_type = object_type
        if self.object_type is None:
            self.object_type = types.TypeRegistry.type_of(self._arrow_data).object_type
        self._artifact = artifact
        from .. import mappers_arrow

        self._mapper = mappers_arrow.map_from_arrow(self.object_type, self._artifact)
        # TODO: construct mapper

    # TODO: doesn't belong here
    @op()
    def sum(self) -> float:
        return pa.compute.sum(self._arrow_data)

    def _count(self):
        return len(self._arrow_data)

    @op()
    def count(self) -> int:
        return self._count()

    def _get_col(self, name):
        from .. import mappers_python

        col = self._arrow_data[name]
        if isinstance(
            self._mapper._property_serializers[name], mappers_python.DefaultFromPy
        ):
            return [
                self._mapper._property_serializers[name].apply(i.as_py()) for i in col
            ]
        return self._mapper._property_serializers[name].apply(col)

    def _index(self, index):
        try:
            row = self._arrow_data.slice(index, 1)
        except IndexError:
            return None
        return self._mapper.apply(row.to_pylist()[0])

    @op(output_type=index_output_type)
    def __getitem__(self, index: int):
        return self._index(index)

    @op(output_type=pick_output_type)
    def pick(self, key: str):
        # return self._table[key]
        # TODO: Don't do to_pylist() here! Stay in arrow til as late
        #     as possible
        object_type = self.object_type
        return ArrowWeaveList(
            self._arrow_data[key], object_type.property_types[key], self._artifact
        )

    @op(
        input_type={
            "self": types.List(types.Any()),
            "map_fn": lambda input_types: types.Function(
                {"row": input_types["self"].object_type}, types.Any()
            ),
        },
        output_type=map_output_type,
    )
    def map(self, map_fn):
        res = mapped_fn_to_arrow(self, map_fn)
        if isinstance(res, ArrowArrayVectorizer):
            res = res.arr
        return ArrowWeaveList(res)

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
        # replace_schema_metadata does a shallow copy
        mapped = mapped_fn_to_arrow(self, group_by_fn)
        group_cols = []
        if isinstance(mapped, ArrowArrayVectorizer):
            mapped = mapped.arr
        if isinstance(mapped, pa.Table):
            for name, column in zip(mapped.column_names, mapped.columns):
                group_col_name = "group_key_" + name
                table = table.append_column(group_col_name, column)
                group_cols.append(group_col_name)
        elif isinstance(mapped, pa.ChunkedArray):
            group_col_name = "group_key"
            table = table.append_column(group_col_name, mapped)
            group_cols.append(group_col_name)
        else:
            raise errors.WeaveInternalError(
                "Arrow groupby not yet support for map result: %s" % type(mapped)
            )
        grouped = table.group_by(group_cols)
        aggs = []
        for column_name in table.column_names:
            aggs.append((column_name, "list"))
        agged = grouped.aggregate(aggs)
        return ArrowTableGroupBy(agged, group_cols, self.object_type, self._artifact)


ArrowWeaveListType.instance_classes = ArrowWeaveList
ArrowWeaveListType.instance_class = ArrowWeaveList


@dataclasses.dataclass
class ArrowTableGroupResultType(ArrowWeaveListType):
    name = "ArrowTableGroupResult"

    key: types.Type = types.Any()

    @classmethod
    def type_of_instance(cls, obj):
        return cls(
            types.TypeRegistry.type_of(obj._arrow_data).object_type,
            types.TypeRegistry.type_of(obj._key),
        )

    def property_types(self):
        return {"_arrow_data": ArrowWeaveListType(self.object_type), "key": self.key}


def key_result_type(input_types):
    return input_types["self"].key


@weave_class(weave_type=ArrowTableGroupResultType)
class ArrowTableGroupResult(ArrowWeaveList):
    def __init__(self, _arrow_data, _key, object_type=None, artifact=None):
        self._arrow_data = _arrow_data
        self._key = _key
        self.object_type = object_type
        if self.object_type is None:
            self.object_type = types.TypeRegistry.type_of(self._table).object_type
        self._artifact = artifact
        from .. import mappers_arrow

        self._mapper = mappers_arrow.map_from_arrow(self.object_type, self._artifact)

    @op(output_type=key_result_type)
    def key(self):
        return self._key.as_py()


ArrowTableGroupResultType.instance_classes = ArrowTableGroupResult
ArrowTableGroupResultType.instance_class = ArrowTableGroupResult
