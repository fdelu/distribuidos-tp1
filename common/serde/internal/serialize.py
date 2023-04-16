import json
import types
from typing import Any, Callable, get_type_hints

from .util import SIMPLE_TYPES, Translated, verify_type


def serialize_item(item: Any, expected_type: Any) -> Translated:
    if type(expected_type) == type and expected_type in SIMPLE_TYPES:
        verify_type(item, expected_type)
        return item

    if isinstance(expected_type, types.GenericAlias):
        return serialize_generic(item, expected_type)

    if isinstance(expected_type, types.UnionType):
        return serialize_union(item, expected_type)

    return serialize_object(item, expected_type)


def serialize_union(item: Any, type_info: types.UnionType) -> Translated:
    if type(item) not in type_info.__args__:
        raise Exception(
            f"Union type {type_info} has failed to serialize: {type(item)} not in union"
            " type"
        )

    return {"type": type(item).__name__, "value": serialize_item(item, type(item))}


def serialize_generic(collection: Any, type_info: types.GenericAlias) -> Translated:
    expected_type: Any = type_info.__origin__
    verify_type(collection, expected_type)
    if expected_type in (list, set):
        item_type = type_info.__args__[0]
        return [serialize_item(i, item_type) for i in collection]
    if expected_type == dict:
        key_type, value_type = type_info.__args__
        return [
            [serialize_item(k, key_type), serialize_item(v, value_type)]
            for k, v in collection.items()
        ]
    raise Exception(f"Generic type {expected_type} is not supported")


def serialize_object(data: object, expected_type: type) -> Translated:
    verify_type(data, expected_type)
    type_hints = get_type_hints(data)
    out = {}
    for name, t in type_hints.items():
        out[name] = serialize_item(getattr(data, name), t)
    return out


def serialize(
    data: object,
    serializer: Callable[[Translated], str] = json.dumps,
    set_type: Any | None = None,
) -> str:
    if set_type is not None:
        return serializer(serialize_item(data, set_type))
    return serializer(serialize_item(data, type(data)))
