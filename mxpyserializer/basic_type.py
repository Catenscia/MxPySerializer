"""
author: Etienne Wallet

This module contains the functions to serialize and deserialize basic types
"""
import re
from typing import Tuple, Union

from multiversx_sdk_core.address import Address

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
    "EgldOrEsdtTokenIdentifier",
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
    Decodes a part of the input data into an unsigned integer value assuming big endian
    and nested-encoded format. Returns the left over

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
            f"Not enough data to decode {data} into an integer "
            f"of length {type_bytes_length}"
        )

    return (
        int.from_bytes(data[:type_bytes_length], signed=signed),
        data[type_bytes_length:],
    )


def nested_decode_basic(
    type_name: str, data: bytes
) -> Tuple[Union[int, str, bool, Address], bytes]:
    """
    Decodes a part of the input data into a basic type assuming a nested-encoded
    format. Returns the left over.

    :param type_name: name of the type of the value to extract from the data
    :type type_name: str
    :param data: data containing the value to extract
    :type data: bytes
    :return: decoded value and the left over bytes
    :rtype: Tuple[Union[int, str, bool], bytes]
    """
    if type_name == "bool":
        value, data = nested_decode_basic("u8", data)
        if value not in (0, 1):
            raise ValueError(f"Expected a boolean but found the value {value}")
        return bool(value), data

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

    if type_name == "Address":
        hex_address, data = data[:32].hex(), data[32:]
        return Address.from_hex(hex_address, "erd"), data

    if type_name in ("TokenIdentifier", "EgldOrEsdtTokenIdentifier", "utf-8 string"):
        element, data = get_bytes_element_from_size(data)
        return element.decode("utf-8"), data

    raise ValueError(f"Unkown basic type {type_name}")


def top_decode_basic(type_name: str, data: bytes) -> Union[int, str, bool, Address]:
    """
    Decodes the input data into a basic type assuming a top-encoded
    format.
    In contrast to the function nested_decode_basic, all the provided data is
    converted, there are no left-over bytes.

    :param type_name: name of the type of the value to extract from the data
    :type type_name: str
    :param data: data containing the value to extract
    :type data: bytes
    :return: decoded value
    :rtype: Union[int, str, bool]
    """
    if type_name == "bool":
        value = int.from_bytes(data)
        if value not in (0, 1):
            raise ValueError(f"Expected a boolean but found the value {value}")
        return bool(value)

    if type_name in ("usize", "u8", "u16", "u32", "u64", "BigUint"):
        return int.from_bytes(data)

    if type_name in ("isize", "i8", "i16", "i32", "i64", "BigInt"):
        return int.from_bytes(data, signed=True)

    if type_name == "Address":
        return Address.from_hex(data.hex(), "erd")

    if type_name in ("TokenIdentifier", "EgldOrEsdtTokenIdentifier", "utf-8 string"):
        return data.decode("utf-8")

    raise ValueError(f"Unkown basic type {type_name}")
