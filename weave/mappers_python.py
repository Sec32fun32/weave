import math

from . import mappers
from . import mappers_weave
from . import mappers_numpy
from . import weave_types as types
from . import types_numpy
from . import graph
from . import errors


class TypedDictToPyDict(mappers_weave.TypedDictMapper):
    def result_type(self):
        property_types = {}
        for k, v in self._property_serializers.items():
            property_types[k] = v.result_type()
        return types.TypedDict(property_types)

    def apply(self, obj):
        result = {}
        for k, v in obj.items():
            v = self._property_serializers[k].apply(v)
            result[k] = v
        return result


class DictToPyDict(mappers_weave.DictMapper):
    def result_type(self):
        return types.Dict(
            self.key_serializer.result_type(), self.value_serializer.result_type()
        )

    def apply(self, obj):
        result = {}
        for k, v in obj.items():
            k = self.key_serializer.apply(k)
            v = self.value_serializer.apply(v)
            result[k] = v
        return result


class ObjectToPyDict(mappers_weave.ObjectMapper):
    def result_type(self):
        property_types = {}
        for k, type_var_type in self._obj_type.variable_property_types().items():
            property_serializer = self._property_serializers[k]
            if property_serializer is None:
                property_types[k] = type_var_type
            else:
                property_types[k] = property_serializer.result_type()
        return self._obj_type.__class__(**property_types)

    def apply(self, obj):
        try:
            obj.save_to_artifact(self._artifact)
        except AttributeError:
            pass
        result = {}
        for prop_name, prop_serializer in self._property_serializers.items():
            if prop_serializer is not None:
                v = prop_serializer.apply(getattr(obj, prop_name))
                result[prop_name] = v
        return result


class ObjectDictToObject(mappers_weave.ObjectMapper):
    def result_type(self):
        property_types = {}
        for k, type_var_type in self._obj_type.variable_property_types().items():
            property_serializer = self._property_serializers[k]
            if property_serializer is None:
                property_types[k] = type_var_type
            else:
                property_types[k] = property_serializer.result_type()
        return self._obj_type.__class__(**property_types)

    def apply(self, obj):
        result = obj
        for k, serializer in self._property_serializers.items():
            v = serializer.apply(obj[k])
            result[k] = v
        result_type = self.result_type()
        for prop_name, prop_type in result_type.variable_property_types().items():
            if isinstance(prop_type, types.Const):
                result[prop_name] = prop_type.val
        return self.result_type().instance_class(**result)


class ListToPyList(mappers_weave.ListMapper):
    def result_type(self):
        return types.List(self._object_type.result_type())

    def apply(self, obj):
        return [self._object_type.apply(item) for item in obj]


class UnionToPyUnion(mappers_weave.UnionMapper):
    def result_type(self):
        return types.UnionType(
            *[mem_mapper.result_type() for mem_mapper in self._member_mappers]
        )

    def apply(self, obj):
        obj_type = types.TypeRegistry.type_of(obj)
        for i, (member_type, member_mapper) in enumerate(
            zip(self.type.members, self._member_mappers)
        ):
            if member_type.assign_type(obj_type) != types.Invalid():
                result = member_mapper.apply(obj)
                if isinstance(result, dict):
                    result["_union_id"] = i
                else:
                    result = {"_union_id": i, "_val": result}
                return result
        raise Exception("invalid %s" % obj)


class PyUnionToUnion(mappers_weave.UnionMapper):
    def result_type(self):
        return types.UnionType(
            *[mem_mapper.result_type() for mem_mapper in self._member_mappers]
        )

    def apply(self, obj):
        member_index = obj["_union_id"]
        if "_val" in obj:
            obj = obj["_val"]
        else:
            obj.pop("_union_id")
        return self._member_mappers[member_index].apply(obj)


class IntToPyInt(mappers_weave.IntMapper):
    def result_type(self):
        return types.Int()

    def apply(self, obj):
        return obj


class FloatToPyFloat(mappers_weave.FloatMapper):
    def result_type(self):
        return types.Float()

    def apply(self, obj):
        if math.isnan(obj):
            return "nan"
        return obj


class PyFloatToFloat(mappers_weave.FloatMapper):
    def result_type(self):
        return types.Float()

    def apply(self, obj):
        if isinstance(obj, str):
            if obj == "nan":
                return float("nan")
        return obj


class StringToPyString(mappers_weave.StringMapper):
    def result_type(self):
        return types.String()

    def apply(self, obj):
        return obj


class NoneToPyNone(mappers_weave.NoneMapper):
    def result_type(self):
        return types.none_type

    def apply(self, obj):
        return None


class UnknownToPyUnknown(mappers_weave.NoneMapper):
    def result_type(self):
        return types.UnknownType()

    def apply(self, obj):
        # This should never be called. Unknown for the object type
        # of empty lists
        raise Exception("invalid")


class FunctionToPyFunction(mappers_weave.FunctionMapper):
    def result_type(self):
        return types.String()

    def apply(self, obj):
        # Obj is graph.Node
        return obj.to_json()


class PyFunctionToFunction(mappers_weave.FunctionMapper):
    def result_type(self):
        # TODO: seems wrong to have Any() here
        return types.Function(types.Any(), types.Any())

    def apply(self, obj):
        # Obj is graph.Node
        return graph.Node.node_from_json(obj)


class RefToPyRef(mappers_weave.RefMapper):
    def result_type(self):
        return types.LocalArtifactRefType(self._object_type.result_type())

    def apply(self, obj):
        return str(obj.uri)


class PyRefToRef(mappers_weave.RefMapper):
    def result_type(self):
        return types.LocalArtifactRefType(self._object_type.result_type())

    def apply(self, obj):
        from . import storage

        return storage.LocalArtifactRef(
            self._object_type.result_type(), storage.LocalArtifactUri.from_str(obj)
        )


class TypeToPyType(mappers_weave.TypeMapper):
    def result_type(self):
        return types.Type()

    def apply(self, obj):
        return obj.to_dict()


class PyTypeToType(mappers_weave.TypeMapper):
    def result_type(self):
        return types.Type()

    def apply(self, obj):
        return types.TypeRegistry.type_from_dict(obj)


class ConstToPyConst(mappers_weave.ConstMapper):
    def result_type(self):
        return self._type

    def apply(self, obj):
        return obj


py_type = type


def map_to_python_(type, mapper, artifact, path=[]):
    if py_type(type) == types.Type:
        # If we're actually serializing a type itself
        return TypeToPyType(type, mapper, artifact, path)
    elif isinstance(type, types.TypedDict):
        return TypedDictToPyDict(type, mapper, artifact, path)
    elif isinstance(type, types.Dict):
        return DictToPyDict(type, mapper, artifact, path)
    elif isinstance(type, types.List):
        return ListToPyList(type, mapper, artifact, path)
    elif isinstance(type, types.UnionType):
        return UnionToPyUnion(type, mapper, artifact, path)
    elif isinstance(type, types.ObjectType):
        return ObjectToPyDict(type, mapper, artifact, path)
    elif isinstance(type, types_numpy.NumpyArrayType):
        return mappers_numpy.NumpyArraySaver(type, mapper, artifact, path)
    elif isinstance(type, types.Int):
        return IntToPyInt(type, mapper, artifact, path)
    elif isinstance(type, types.Float):
        return FloatToPyFloat(type, mapper, artifact, path)
    elif isinstance(type, types.Number):
        return IntToPyInt(type, mapper, artifact, path)
    elif isinstance(type, types.String):
        return StringToPyString(type, mapper, artifact, path)
    elif isinstance(type, types.Const):
        return ConstToPyConst(type, mapper, artifact, path)
    elif isinstance(type, types.NoneType):
        return NoneToPyNone(type, mapper, artifact, path)
    elif isinstance(type, types.UnknownType):
        return UnknownToPyUnknown(type, mapper, artifact, path)
    elif isinstance(type, types.Function):
        return FunctionToPyFunction(type, mapper, artifact, path)
    elif isinstance(type, types.LocalArtifactRefType):
        return RefToPyRef(type, mapper, artifact, path)
    else:
        raise errors.WeaveSerializeError("not implemented %s" % type)


def map_from_python_(type, mapper, artifact, path=[]):
    if py_type(type) == types.Type:
        # If we're actually serializing a type itself
        return PyTypeToType(type, mapper, artifact, path)
    elif isinstance(type, types_numpy.NumpyArrayType):
        return None
    elif isinstance(type, types_numpy.NumpyArrayRefType):
        mapper1 = ObjectDictToObject(type, mapper, artifact, path)
        mapper2 = mappers_numpy.NumpyArrayLoader(
            mapper1.result_type(), mapper, artifact, path
        )
        return mappers.ChainMapper((mapper1, mapper2))
    elif isinstance(type, types.ObjectType):
        return ObjectDictToObject(type, mapper, artifact, path)
    # elif isinstance(type, dict):
    #     if arrow_type.metadata is not None and b'weave_type' in arrow_type.metadata:
    #         return ArrowWeaveFieldToObject(arrow_type, mapper, artifact, path)
    #     else:
    #         return mapper(arrow_type.type, artifact, path)
    elif isinstance(type, types.TypedDict):
        return TypedDictToPyDict(type, mapper, artifact, path)
    elif isinstance(type, types.Dict):
        return DictToPyDict(type, mapper, artifact, path)
    elif isinstance(type, types.List):
        return ListToPyList(type, mapper, artifact, path)
    elif isinstance(type, types.UnionType):
        return PyUnionToUnion(type, mapper, artifact, path)
    elif isinstance(type, types.Int):
        return IntToPyInt(type, mapper, artifact, path)
    elif isinstance(type, types.Float):
        return PyFloatToFloat(type, mapper, artifact, path)
    elif isinstance(type, types.Number):
        return IntToPyInt(type, mapper, artifact, path)
    elif isinstance(type, types.String):
        return StringToPyString(type, mapper, artifact, path)
    elif isinstance(type, types.Const):
        return ConstToPyConst(type, mapper, artifact, path)
    elif isinstance(type, types.NoneType):
        return NoneToPyNone(type, mapper, artifact, path)
    elif isinstance(type, types.UnknownType):
        return UnknownToPyUnknown(type, mapper, artifact, path)
    elif isinstance(type, types.Function):
        return PyFunctionToFunction(type, mapper, artifact, path)
    elif isinstance(type, types.LocalArtifactRefType):
        return PyRefToRef(type, mapper, artifact, path)
    else:
        raise Exception("not implemented", type)


map_to_python = mappers.make_mapper(map_to_python_)
map_from_python = mappers.make_mapper(map_from_python_)
