import json
import pyarrow as pa

from . import mappers
from . import mappers_python
from . import arrow_util
from . import weave_types as types
from . import storage


class TypedDictToArrowStruct(mappers_python.TypedDictToPyDict):
    def result_type(self):
        fields = []
        for property_key, property_serializer in self._property_serializers.items():
            prop_result_type = property_serializer.result_type()
            fields.append(arrow_util.arrow_field(property_key, prop_result_type))
        return pa.struct(fields)


class ObjectToArrowStruct(mappers_python.ObjectToPyDict):
    def result_type(self):
        fields = []
        for property_key, property_serializer in self._property_serializers.items():
            if property_serializer is not None:
                prop_result_type = property_serializer.result_type()
                fields.append(arrow_util.arrow_field(property_key, prop_result_type))
        return pa.struct(fields)


class ListToArrowArr(mappers_python.ListToPyList):
    def result_type(self):
        return pa.list_(arrow_util.arrow_field("x", self._object_type.result_type()))


class IntToArrowInt(mappers_python.IntToPyInt):
    def result_type(self):
        return pa.int64()


class FloatToArrowFloat(mappers.Mapper):
    def result_type(self):
        return pa.float64()

    def apply(self, obj):
        return obj


class ArrowFloatToFloat(mappers.Mapper):
    def result_type(self):
        return types.Float()

    def apply(self, obj):
        return obj


class StringToArrowString(mappers_python.StringToPyString):
    def result_type(self):
        return pa.string()


class NoneToArrowNone(mappers.Mapper):
    def result_type(self):
        return pa.null()


class UnknownToArrowNone(mappers_python.UnknownToPyUnknown):
    def result_type(self):
        return pa.null()


class DefaultToArrow(mappers.Mapper):
    def __init__(self, type_: types.Type, mapper, artifact, path=[]):
        self.type = type_
        self._artifact = artifact
        self._path = path

    def result_type(self):
        return pa.string()

    def apply(self, obj):
        name = "-".join(self._path)
        ref = storage.save_to_artifact(
            obj, artifact=self._artifact, name=name, type_=self.type
        )
        local_ref_str = ref.local_ref_str()
        return local_ref_str


def map_to_arrow_(type, mapper, artifact, path=[]):
    if isinstance(type, types.TypedDict):
        return TypedDictToArrowStruct(type, mapper, artifact, path)
    elif isinstance(type, types.List):
        return ListToArrowArr(type, mapper, artifact, path)
    elif isinstance(type, types.ObjectType):
        return ObjectToArrowStruct(type, mapper, artifact, path)
    elif isinstance(type, types.Int):
        return IntToArrowInt(type, mapper, artifact, path)
    elif isinstance(type, types.Float):
        return FloatToArrowFloat(type, mapper, artifact, path)
    elif isinstance(type, types.String):
        return StringToArrowString(type, mapper, artifact, path)
    elif isinstance(type, types.NoneType):
        return NoneToArrowNone(type, mapper, artifact, path)
    elif isinstance(type, types.UnknownType):
        return UnknownToArrowNone(type, mapper, artifact, path)
    else:
        return DefaultToArrow(type, mapper, artifact, path)


def map_from_arrow_(type, mapper, artifact, path=[]):
    if isinstance(type, types.TypedDict):
        return mappers_python.TypedDictToPyDict(type, mapper, artifact, path)
    elif isinstance(type, types.List):
        return mappers_python.ListToPyList(type, mapper, artifact, path)
    elif isinstance(type, types.ObjectType):
        return mappers_python.ObjectDictToObject(type, mapper, artifact, path)
    elif isinstance(type, types.Int):
        return mappers_python.IntToPyInt(type, mapper, artifact, path)
    elif isinstance(type, types.Float):
        return ArrowFloatToFloat(type, mapper, artifact, path)
    elif isinstance(type, types.String):
        return mappers_python.StringToPyString(type, mapper, artifact, path)
    elif isinstance(type, types.NoneType):
        return mappers_python.NoneToPyNone(type, mapper, artifact, path)
    elif isinstance(type, types.UnknownType):
        return UnknownToArrowNone(type, mapper, artifact, path)
    else:
        return mappers_python.DefaultFromPy(type, mapper, artifact, path)


map_to_arrow = mappers.make_mapper(map_to_arrow_)
map_from_arrow = mappers.make_mapper(map_from_arrow_)
