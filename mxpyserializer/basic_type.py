"""
author: Etienne Wallet

This module contains the functions to serialize and deserialize basic types
"""
import re

from typing import Tuple

BASIC_TYPES = (
    "bytes",
    "bool",
    "usize",
    "u8",
    "u16",
    "u32",
    "u64",
    "isize",
    "i8",
    "i16",
    "i32",
    "i64",
    "BigInt",
    "BigUint",
    "Address",
    "TokenIdentifier",
    "utf-8 string",
)


def get_bytes_element_from_size(data: bytes) -> Tuple[bytes, bytes]:
    """
    Extract an element from the data by assuming that the first part of the data
    is the encoded size (usize) of the element we are looking for.
    (data = <size><element><left_over>)

    :param data: bytes data to extract a part from
    :type data: bytes
    :return: extracted part and the left over part
    :rtype: Tuple[bytes, bytes]
    """
    element_size, data = nested_decode_basic("u32", data)
    return data[:element_size], data[element_size:]


def nested_decode_integer(
    data: bytes, type_bytes_length: int, signed: bool
) -> Tuple[int, bytes]:
    """
    Decodes a part of the input data into an unsigned integer value assuming big endian format,
    nested-encoded format. Returns the left over

    :param data: bytes to decode
    :type data: bytes
    :param type_bytes_length: bytes length of the wanted result type
    :type type_bytes_length: int
    :param signed: if the encoded data is signed or not
    :type signed: bool
    :return: decoded value and the left over bytes
    :rtype: Tuple[int, bytes]
    """
    if len(data) < type_bytes_length:
        raise ValueError(
            f"Not enough data to decode {data} into an integer of length {type_bytes_length}"
        )

    return (
        int.from_bytes(data[:type_bytes_length], signed=signed),
        data[type_bytes_length:],
    )


def nested_decode_basic(type_name: str, data: bytes) -> Tuple[int, bytes]:
    """
    Decodes a part of the input data into a basic type assuming a nested-encoded
    format. Returns the left over.

    :param type_name: name of the type of the value to extract from the data
    :type type_name: str
    :param data: data containing the value to extract
    :type data: bytes
    :return: decoded value and the left over bytes
    :rtype: Tuple[int, bytes]
    """

    integer_pattern = re.match(r"^([ui])(\d+)$", type_name.replace("size", "8"))
    if integer_pattern is not None:
        groups = integer_pattern.groups()
        signed = groups[0] == "i"
        type_number = int(groups[1])
        if type_number % 8 != 0:
            raise ValueError(f"Invalid integer type: {type_number}")
        type_bytes_length = type_number // 8
        return nested_decode_integer(data, type_bytes_length, signed)
    if type_name == "BigUint":
        element, data = get_bytes_element_from_size(data)
        return int.from_bytes(element), data
    if type_name == "BigInt":
        element, data = get_bytes_element_from_size(data)
        return int.from_bytes(element, signed=True), data
    raise ValueError(f"Unkown basic type {type_name}")
