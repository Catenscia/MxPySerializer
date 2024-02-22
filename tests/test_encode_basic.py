from typing import Any
from multiversx_sdk_core import Address
import pytest
from mxpyserializer import basic_type


@pytest.mark.parametrize(
    "value, type_bytes_length, signed, expected_result",
    [
        (10, 4, False, b"\x00\x00\x00\x0A"),
        (4026531850, 4, False, b"\xF0\x00\x00\x0A"),
        (0, 1, False, b"\x00"),
        (260, 2, False, b"\x01\x04"),
        (10, 4, True, b"\x00\x00\x00\x0A"),
        (-268435446, 4, True, b"\xF0\x00\x00\x0A"),
        (0, 1, True, b"\x00"),
        (260, 2, True, b"\x01\x04"),
    ],
)
def test_nested_encode_integer(
    value: int,
    type_bytes_length: int,
    signed: bool,
    expected_result: bytes,
):
    # Given
    # When
    result = basic_type.nested_encode_integer(value, type_bytes_length, signed)
    # Then
    assert expected_result == result


@pytest.mark.parametrize(
    "type_name, value, expected_result",
    [
        ("u32", 10, b"\x00\x00\x00\x0A"),
        ("u32", 4026531850, b"\xF0\x00\x00\x0A"),
        ("u8", 0, b"\x00"),
        ("usize", 8, b"\x00\x00\x00\x08"),
        ("u16", 260, b"\x01\x04"),
        ("i32", 10, b"\x00\x00\x00\x0A"),
        ("i32", -268435446, b"\xF0\x00\x00\x0A"),
        ("i8", 0, b"\x00"),
        ("isize", 15, b"\x00\x00\x00\x0F"),
        ("i16", 260, b"\x01\x04"),
        ("BigUint", 418, b"\x00\x00\x00\x02\x01\xa2"),
        ("BigInt", -32350, b"\x00\x00\x00\x02\x81\xa2"),
        ("bool", True, b"\x01"),
        ("bool", 1, b"\x01"),
        ("bool", "0", b"\x00"),
        (
            "utf-8 string",
            "heythisisastring",
            b"\x00\x00\x00\x10heythisisastring",
        ),
        (
            "utf-8string",
            "heythisisastring",
            b"\x00\x00\x00\x10heythisisastring",
        ),
        (
            "TokenIdentifier",
            "TKN-abcdef",
            b"\x00\x00\x00\x0ATKN-abcdef",
        ),
        (
            "EgldOrEsdtTokenIdentifier",
            "EGLD",
            b"\x00\x00\x00\x04EGLD",
        ),
        (
            "Address",
            "erd1qqqqqqqqqqqqqpgqahfmv4apudlzgawgcvp2zr65dtufqfmy6avsazkewu",
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\xed\xd3\xb6W\xa1"
            b"\xe3~$u\xc8\xc3\x02\xa1\x0fTj\xf8\x90'd\xd7Y",
        ),
        (
            "Address",
            Address.from_bech32(
                "erd1qqqqqqqqqqqqqpgqahfmv4apudlzgawgcvp2zr65dtufqfmy6avsazkewu"
            ),
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\xed\xd3\xb6W\xa1"
            b"\xe3~$u\xc8\xc3\x02\xa1\x0fTj\xf8\x90'd\xd7Y",
        ),
    ],
)
def test_nested_encode_basic(type_name: str, value: Any, expected_result: bytes):
    # Given
    # When
    result = basic_type.nested_encode_basic(type_name, value)

    # Then
    assert expected_result == result


@pytest.mark.parametrize(
    "type_name, value, expected_result",
    [
        ("u32", 10, b"\x0A"),
        ("u32", 4026531850, b"\xF0\x00\x00\x0A"),
        ("u8", 0, b""),
        ("usize", 8, b"\x08"),
        ("u16", 260, b"\x01\x04"),
        ("i32", 10, b"\x0A"),
        ("i32", -268435446, b"\xF0\x00\x00\x0A"),
        ("i8", 0, b""),
        ("isize", 15, b"\x0F"),
        ("i16", 260, b"\x01\x04"),
        ("BigUint", 418, b"\x01\xa2"),
        ("BigInt", -32350, b"\x81\xa2"),
        ("bool", True, b"\x01"),
        ("bool", False, b""),
        ("utf-8 string", "heythisisastring", b"heythisisastring"),
        ("utf-8string", "heythisisastring", b"heythisisastring"),
        (
            "TokenIdentifier",
            "TKN-abcdef",
            b"TKN-abcdef",
        ),
        (
            "EgldOrEsdtTokenIdentifier",
            "EGLD",
            b"EGLD",
        ),
        (
            "Address",
            "erd1qqqqqqqqqqqqqpgqahfmv4apudlzgawgcvp2zr65dtufqfmy6avsazkewu",
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\xed\xd3\xb6W\xa1"
            b"\xe3~$u\xc8\xc3\x02\xa1\x0fTj\xf8\x90'd\xd7Y",
        ),
        (
            "Address",
            Address.from_bech32(
                "erd1qqqqqqqqqqqqqpgqahfmv4apudlzgawgcvp2zr65dtufqfmy6avsazkewu"
            ),
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\xed\xd3\xb6W\xa1"
            b"\xe3~$u\xc8\xc3\x02\xa1\x0fTj\xf8\x90'd\xd7Y",
        ),
    ],
)
def test_top_encode_basic(type_name: str, value: Any, expected_result: bytes):
    # Given
    # When
    result = basic_type.top_encode_basic(type_name, value)

    # Then
    assert expected_result == result
