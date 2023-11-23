"""
author: Etienne Wallet

This module contains the functions to serialize and deserialize basic types
"""
import re

from typing import Tuple


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
        int.from_bytes(data[:type_bytes_length], byteorder="big", signed=signed),
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
    raise ValueError(f"Unkown basic type {type_name}")
