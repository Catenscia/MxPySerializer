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


def build_storage_bytes_key_for_map_item(
    storage_name: str,
    mapping_key_type: str,
    mapping_key: Any,
    serializer: Optional[AbiSerializer] = None,
) -> bytes:
    """
    Construct the storage key from the name of the storage and the key of the
    value to get, assuming the storage is a map

    :param storage_name: name of the storage to get the key of
    :type storage_name: str
    :param mapping_key_type: type of the mapping key
    :type mapping_key_type: str
    :param mapping_key: key mapped to the wanted value
    :type mapping_key: Any
    :param serializer: serializer to use if needed (in case of custom struct
        for example)
    :type serializer: Optional[AbiSerializer]
    :return: storage key of the value of the map
    :rtype: bytes
    """
    if serializer is None:
        serializer = AbiSerializer()
    item_storage_name = storage_name + ".mapped"
    return build_storage_bytes_key_from_name(
        item_storage_name
    ) + serializer.nested_encode(mapping_key_type, mapping_key)


def build_storage_bytes_key_for_set_item(storage_name: str, index: int) -> bytes:
    """
    Construct the storage key from the name of the storage and the index of the
    value to get, assuming the storage is a set

    :param storage_name: name of the storage to get the key of
    :type storage_name: str
    :param index: index of the value to get in the set
    :type index: int
    :return: storage key of the value of the set
    :rtype: bytes
    """
    if index < 1:
        raise ValueError("Index for contract storage starts at 1")
    item_storage_name = storage_name + ".value"
    return build_storage_bytes_key_from_name(item_storage_name) + nested_encode_basic(
        "u32", index
    )


def build_storage_bytes_key_for_unordered_set_item(
    storage_name: str, index: int
) -> bytes:
    """
    Construct the storage key from the name of the storage and the index of the
    value to get, assuming the storage is an unordered set

    :param storage_name: name of the storage to get the key of
    :type storage_name: str
    :param index: index of the value to get in the unordered set
    :type index: int
    :return: storage key of the value of the unordered set
    :rtype: bytes
    """
    return build_storage_bytes_key_for_vec_item(storage_name, index)


def build_storage_bytes_key_for_linked_list_item(
    storage_name: str, index: int
) -> bytes:
    """
    Construct the storage key from the name of the storage and the index of the
    value to get, assuming the storage is a linked list

    :param storage_name: name of the storage to get the key of
    :type storage_name: str
    :param index: index of the value to get in the linked list
    :type index: int
    :return: storage key of the value of the linked list
    :rtype: bytes
    """
    if index < 1:
        raise ValueError("Index for contract storage starts at 1")
    item_storage_name = storage_name + ".node"
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
