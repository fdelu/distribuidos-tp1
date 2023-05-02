from typing import TypeVar, Generic, get_args
from common.serde import serialize, deserialize

IN = TypeVar("IN")
OUT = TypeVar("OUT", contravariant=True)


class CommsSerializer(Generic[OUT]):
    def serialize_record(self, message: OUT) -> str:
        """
        Serializes the given message into a string
        """
        out_type = get_args(self.__orig_bases__[0])[1]  # type: ignore
        return serialize(message, set_type=out_type)


class Deserializer(Generic[IN]):
    def deserialize_record(self, message: str) -> IN:
        """
        Deserialize the given message into the input type
        """
        in_type = get_args(self.__orig_bases__[0])[0]  # type: ignore
        return deserialize(in_type, message)
