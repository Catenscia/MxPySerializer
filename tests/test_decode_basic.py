from typing import Tuple
import pytest
from mxpyserializer import basic_type, errors


@pytest.mark.parametrize(
    "data, type_bytes_length, signed, expected_result",
    [
        (b"\x00\x00\x00\x0A", 4, False, (10, b"")),
        (b"\xF0\x00\x00\x0A", 4, False, (4026531850, b"")),
        (b"\x00\x00\x00\x0A", 1, False, (0, b"\x00\x00\x0A")),
        (b"\x01\x04\xEF\x0A", 2, False, (260, b"\xEF\x0A")),
        (b"\x00\x00\x00\x0A", 4, True, (10, b"")),
        (b"\xF0\x00\x00\x0A", 4, True, (-268435446, b"")),
        (b"\x00\x00\x00\x0A", 1, True, (0, b"\x00\x00\x0A")),
        (b"\x01\x04\xEF\x0A", 2, True, (260, b"\xEF\x0A")),
    ],
)
def test_nested_decode_integer(
    data: bytes,
    type_bytes_length: int,
    signed: bool,
    expected_result: Tuple[int, bytes],
):
    # Given
    # When
    result = basic_type.nested_decode_integer(data, type_bytes_length, signed)
    # Then
    assert expected_result == result


def test_nested_decode_integer_data_too_small():
    # Given
    data = b"\x00\x00\x00\x0A"
    type_bytes_length = 8

    # When
    try:
        basic_type.nested_decode_integer(data, type_bytes_length, False)
        raise RuntimeError("Above line should raise an error")
    except ValueError as err:
        assert (
            err.args[0] == f"Not enough data to decode {data} into an "
            f"integer of length {type_bytes_length}"
        )


@pytest.mark.parametrize(
    "type_name, data, expected_result",
    [
        ("u32", b"\x00\x00\x00\x0A", (10, b"")),
        ("u32", b"\xF0\x00\x00\x0A", (4026531850, b"")),
        ("u8", b"\x00\x00\x00\x0A", (0, b"\x00\x00\x0A")),
        ("usize", b"\x08\x00\x00\x0A", (134217738, b"")),
        ("u16", b"\x01\x04\xEF\x0A", (260, b"\xEF\x0A")),
        ("i32", b"\x00\x00\x00\x0A", (10, b"")),
        ("i32", b"\xF0\x00\x00\x0A", (-268435446, b"")),
        ("i8", b"\x00\x00\x00\x0A", (0, b"\x00\x00\x0A")),
        ("isize", b"\x00\x00\x00\x0F\x0A", (15, b"\x0A")),
        ("i16", b"\x01\x04\xEF\x0A", (260, b"\xEF\x0A")),
        ("BigUint", b"\x00\x00\x00\x02\x01\xa2\xaa\xaa\xaa", (418, b"\xaa\xaa\xaa")),
        ("BigInt", b"\x00\x00\x00\x02\x81\xa2\xaa\xaa\xaa", (-32350, b"\xaa\xaa\xaa")),
        ("bool", b"\x01\x0a", (True, b"\x0a")),
        (
            "utf-8 string",
            b"\x00\x00\x00\x10heythisisastring\x01\x0a\xaa\xaa",
            ("heythisisastring", b"\x01\x0a\xaa\xaa"),
        ),
        (
            "utf-8string",
            b"\x00\x00\x00\x10heythisisastring\x01\x0a\xaa\xaa",
            ("heythisisastring", b"\x01\x0a\xaa\xaa"),
        ),
        (
            "TokenIdentifier",
            b"\x00\x00\x00\x0ATKN-abcdef\x01\x0a\xaa\xaa",
            ("TKN-abcdef", b"\x01\x0a\xaa\xaa"),
        ),
        (
            "EgldOrEsdtTokenIdentifier",
            b"\x00\x00\x00\x04EGLD\x01\x0a\xaa\xaa",
            ("EGLD", b"\x01\x0a\xaa\xaa"),
        ),
        ("bytes", b"\x00\x00\x00\x01\xAA\xEE", (b"\xAA", b"\xEE")),
    ],
)
def test_nested_decode_basic(
    type_name: str, data: bytes, expected_result: Tuple[int, bytes]
):
    # Given
    # When
    result = basic_type.nested_decode_basic(type_name, data)

    # Then
    assert expected_result == result


def test_nested_decode_address():
    # Given
    data = (
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\xed\xd3"
        b"\xb6W\xa1\xe3~$u\xc8\xc3\x02\xa1\x0fTj\xf8\x90'd\xd7Y\xab\xcd\xef"
    )
    expected_bech32_address = (
        "erd1qqqqqqqqqqqqqpgqahfmv4apudlzgawgcvp2zr65dtufqfmy6avsazkewu"
    )
    expected_remaining_data = b"\xab\xcd\xef"
    # When
    result, remaining_data = basic_type.nested_decode_basic("Address", data)

    # Then
    assert expected_bech32_address == result
    assert expected_remaining_data == remaining_data


@pytest.mark.parametrize(
    "type_prefix",
    ["u", "i"],
)
@pytest.mark.parametrize(
    "type_number",
    [1, 7, 9, 142],
)
def test_basic_integer_type(type_prefix: str, type_number: int):
    # Given
    type_name = type_prefix + str(type_number)
    # When
    try:
        basic_type.nested_decode_basic(type_name, b"")
        raise RuntimeError("Above line should raise an error")
    except ValueError as err:
        assert err.args[0] == f"Invalid integer type: {type_number}"


def test_unknown_basic_type_nested_decode():
    # Given
    type_name = "List<TokenIdentifier>"

    # When
    try:
        basic_type.nested_decode_basic(type_name, b"")
        raise RuntimeError("Above line should raise an error")
    except errors.UnknownType as err:
        assert err.args[0] == f"Unknown type: {type_name}"


def test_extract_from_size():
    # Given
    data = b"\x00\x00\x00\x08\x15d\x89u\x84V\x98B\xaa\xaa\xaa"

    # When
    element, data = basic_type.get_bytes_element_from_size(data)

    # Then
    assert element == b"\x15d\x89u\x84V\x98B"
    assert data == b"\xaa\xaa\xaa"


def test_wrong_bool_nested_decode():
    # Given
    data = b"\x02"

    # When
    try:
        basic_type.nested_decode_basic("bool", data)
        raise RuntimeError("Above line should raise an error")
    except ValueError as err:
        assert err.args[0] == "Expected a boolean but found the value 2"


@pytest.mark.parametrize(
    "type_name, data, expected_result",
    [
        ("u32", b"\x0A", 10),
        ("u32", b"\xF0\x00\x00\x0A", 4026531850),
        ("u8", b"", 0),
        ("usize", b"\x08", 8),
        ("u16", b"\x01\x04", 260),
        ("i32", b"\x0A", 10),
        ("i32", b"\xF0\x00\x00\x0A", -268435446),
        ("i8", b"", 0),
        ("isize", b"\x0F", 15),
        ("i16", b"\x01\x04", 260),
        ("BigUint", b"\x01\xa2", 418),
        ("BigInt", b"\x81\xa2", -32350),
        ("bool", b"\x01", True),
        ("bool", b"", False),
        ("utf-8 string", b"heythisisastring", "heythisisastring"),
        ("utf-8string", b"heythisisastring", "heythisisastring"),
        (
            "TokenIdentifier",
            b"TKN-abcdef",
            "TKN-abcdef",
        ),
        (
            "EgldOrEsdtTokenIdentifier",
            b"EGLD",
            "EGLD",
        ),
        ("bytes", b"\xAA\xEE", b"\xAA\xEE"),
    ],
)
def test_top_decode_basic(
    type_name: str, data: bytes, expected_result: Tuple[int, bytes]
):
    # Given
    # When
    result = basic_type.top_decode_basic(type_name, data)

    # Then
    assert expected_result == result


def test_wrong_bool_top_decode():
    # Given
    data = b"\x02"

    # When
    try:
        basic_type.top_decode_basic("bool", data)
        raise RuntimeError("Above line should raise an error")
    except ValueError as err:
        assert err.args[0] == "Expected a boolean but found the value 2"


def test_unknown_basic_type_top_decode():
    # Given
    type_name = "List<TokenIdentifier>"

    # When
    try:
        basic_type.top_decode_basic(type_name, b"")
        raise RuntimeError("Above line should raise an error")
    except errors.UnknownType as err:
        assert err.args[0] == f"Unknown type: {type_name}"


def test_top_decode_address():
    # Given
    data = (
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00\xed\xd3"
        b"\xb6W\xa1\xe3~$u\xc8\xc3\x02\xa1\x0fTj\xf8\x90'd\xd7Y"
    )
    expected_bech32_address = (
        "erd1qqqqqqqqqqqqqpgqahfmv4apudlzgawgcvp2zr65dtufqfmy6avsazkewu"
    )

    # When
    result = basic_type.top_decode_basic("Address", data)

    # Then
    assert expected_bech32_address == result
