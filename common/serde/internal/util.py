import types
from typing import Callable, Concatenate, ParamSpec, Type, TypeVar, get_type_hints

"""
Type alias for the types that can be serialized and deserialized.
"""
Translated = (
    dict[str, "Translated"]
    | list["Translated"]
    | set["Translated"]
    | str
    | int
    | float
    | None
)

SIMPLE_TYPES = [str, int, float, types.NoneType]

P = ParamSpec("P")
Serializer = Callable[Concatenate[Translated, P], str]
Deserializer = Callable[Concatenate[str, P], Translated]


def verify_type(item: object, expected_type: type):
    """
    Verifies that the given item is of the expected type.

    Does not verify generic types, only the base type.
    """
    if type(expected_type) == types.UnionType:
        for t in get_union_types(expected_type):
            try:
                verify_type(item, t)
                return
            except:
                pass

    if type(expected_type) == types.GenericAlias:
        base_type = get_generic_types(expected_type)[0]
        if base_type == type(item):
            return

    if type(item) == expected_type:
        return

    raise Exception(
        f"Expected type {expected_type} but got {type(item)} (value: {item}))"
    )


def get_union_types(type_info: types.UnionType) -> tuple[type, ...]:
    """
    Returns the possible types of an Union type.
    """
    return type_info.__args__


def get_generic_types(type_info: types.GenericAlias) -> tuple[type, tuple[type, ...]]:
    """
    Returns the base type and the generic types of a Generic type.
    """
    return type_info.__origin__, type_info.__args__
