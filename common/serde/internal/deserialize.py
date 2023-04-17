import json
import types
from typing import Any, Type, TypeVar, get_args, get_origin, get_type_hints

from .util import (
    SIMPLE_TYPES,
    SerializationError,
    Translated,
    get_type_name,
    verify_type,
)

T = TypeVar("T")


def deserialize_item(data_type: Any, data: Translated) -> Any:
    if data_type in SIMPLE_TYPES:
        verify_type(data, data_type)
        return data
    if isinstance(data_type, types.GenericAlias):
        return deserialize_generic(data_type, data)
    if isinstance(data_type, types.UnionType):
        return deserialize_union(data_type, data)
    return deserialize_object(data_type, data)


def deserialize_union(type_info: types.UnionType, data: Any) -> Any:
    if type(data) != list or len(data) != 2:
        raise SerializationError(
            f"Can't deserialize Union type {type_info}: Invalid format.\nData:\n{data}"
        )

    for t in get_args(type_info):
        if data[0] == get_type_name(t):
            item = deserialize_item(t, data[1])
            verify_type(item, t)
            return item
    raise SerializationError(
        f"Union type {type_info} has failed to deserialize as any of its types"
    )


def deserialize_generic(type_info: types.GenericAlias, data: Any) -> Any:
    expected_type: Any = get_origin(type_info)
    verify_type(data, list)  # We use lists to represent lists, sets and dicts
    if expected_type in (list, set):
        item_type = get_args(type_info)[0]
        values = expected_type(deserialize_item(item_type, i) for i in data)
        for i in values:
            verify_type(i, item_type)
        return values
    if expected_type == dict:
        key_type, value_type = get_args(type_info)
        values = {
            deserialize_item(key_type, k): deserialize_item(value_type, v)
            for k, v in data
        }
        for k, v in values.items():
            verify_type(k, key_type)
            verify_type(v, value_type)
        return values
    raise SerializationError(f"Generic type {expected_type} is not supported")


def deserialize_object(data_type: Type[T], data: Any) -> T:
    type_hints = get_type_hints(data_type)
    out = data_type.__new__(data_type)
    for i, (name, item_type) in enumerate(type_hints.items()):
        item = deserialize_item(item_type, data[i])
        verify_type(item, item_type)
        object.__setattr__(out, name, item)
    return out


def deserialize(data_type: Any, data: str) -> Any:
    return deserialize_item(data_type, json.loads(data))
