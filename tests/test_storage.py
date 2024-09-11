from typing import Any, List, Tuple
import pytest

from mxpyserializer import storage_read


@pytest.mark.parametrize(
    "storage_name, expected_result",
    [
        ("my_bigint_key", b"my_bigint_key"),
        ("my_managed_address_key", b"my_managed_address_key"),
        ("my_vec_biguint_key", b"my_vec_biguint_key"),
    ],
)
def test_build_key_from_name(
    storage_name: str,
    expected_result: bytes,
):
    # Given
    # When
    result = storage_read.build_storage_bytes_key_from_name(storage_name)
    # Then
    assert expected_result == result


@pytest.mark.parametrize(
    "storage_name, item_index, expected_result",
    [
        ("my_bigint_key", 5, b"my_bigint_key.item\x00\x00\x00\x05"),
        (
            "my_managed_address_key",
            4026531850,
            b"my_managed_address_key.item\xf0\x00\x00\x0a",
        ),
        ("my_vec_biguint_key", 1, b"my_vec_biguint_key.item\x00\x00\x00\x01"),
    ],
)
def test_build_key_for_vec_item(
    storage_name: str,
    item_index: int,
    expected_result: bytes,
):
    # Given
    # When
    result = storage_read.build_storage_bytes_key_for_vec_item(storage_name, item_index)
    # Then
    assert expected_result == result


def test_build_key_for_vec_item_error():
    # Given
    # When
    try:
        storage_read.build_storage_bytes_key_for_vec_item("", 0)
        raise RuntimeError("Above line should throw a ValueError")
    except ValueError:
        # Then
        pass


@pytest.mark.parametrize(
    "storage_name, sub_keys, expected_result",
    [
        (
            "my_structs_with_args_key",
            [("BigUint", 8794), ("TokenIdentifier", "WEGLD-abcdef")],
            bytes.fromhex(
                "6d795f737472756374735f776974685f617267735f6b657900000002"
                "225a0000000c5745474c442d616263646566"
            ),
        ),
        (
            "my_structs_with_args_key",
            [("BigUint", 123456), ("TokenIdentifier", "MEX-abcdef")],
            bytes.fromhex(
                "6d795f737472756374735f776974685f617267735f6b657900000003"
                "01e2400000000a4d45582d616263646566"
            ),
        ),
    ],
)
def test_build_nested_storage_key_without_abi(
    storage_name: str,
    sub_keys: List[Tuple[str, Any]],
    expected_result: bytes,
):
    # Given
    # When
    result = storage_read.build_nested_storage_bytes_key(storage_name, sub_keys)
    # Then
    assert expected_result == result
