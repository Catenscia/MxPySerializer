"""
author: Etienne Wallet

This module contains the function to deserialize the data stored in a smart-contract
"""

from typing import Any, List, Optional, Tuple
from mxpyserializer.abi_serializer import AbiSerializer
from mxpyserializer.basic_type import nested_encode_basic, top_encode_basic


def build_storage_bytes_key_from_name(storage_name: str) -> bytes:
    """
    Construct the storage key from the name of the storage

    :param storage_name: name of the storage to get the key of
    :type storage_name: str
    :return: storage key as bytes
    :rtype: bytes
    """
    return top_encode_basic("utf-8 string", storage_name)


def build_storage_bytes_key_for_vec_item(storage_name: str, index: int) -> bytes:
    """
    Construct the storage key from the name of the storage and the index of the
    value to get, assuming the storage is a vector

    :param storage_name: name of the storage to get the key of
    :type storage_name: str
    :param index: index of the value to get in the vector
    :type index: int
    :return: storage key of the value of the vector
    :rtype: bytes
    """
    if index < 1:
        raise ValueError("Index for contract storage starts at 1")
    item_storage_name = storage_name + ".item"
    return build_storage_bytes_key_from_name(item_storage_name) + nested_encode_basic(
        "u32", index
    )


def build_nested_storage_bytes_key(
    storage_name: str,
    sub_keys: List[Tuple[str, Any]],
    serializer: Optional[AbiSerializer] = None,
) -> bytes:
    """
    Construct the storage key from the name of the nested storage and the nested values

    :param storage_name: name of the storage to get the key of
    :type storage_name: str
    :param sub_keys: ide the list of sub keys with the type names and their values
    :type sub_keys: List[Tuple[str, Any]]
    :param serializer: serializer to use if needed (in case of custom struct
        for example)
    :type serializer: Optional[AbiSerializer]
    :return: storage key of the value of the vector
    :rtype: bytes
    """
    if serializer is None:
        serializer = AbiSerializer()
    key = build_storage_bytes_key_from_name(storage_name)
    for type_name, value in sub_keys:
        key += serializer.nested_encode(type_name, value)
    return key
