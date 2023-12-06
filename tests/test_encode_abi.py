from pathlib import Path
from typing import Any, Dict, List, Union

import pytest

from mxpyserializer.abi_serializer import AbiSerializer


@pytest.mark.parametrize(
    "enum_name,value,top_encode,expected_results",
    [
        (
            "MyAbiEnum",
            {"name": "Nothing", "discriminant": 0, "values": None},
            True,
            b"",
        ),
        (
            "MyAbiEnum",
            0,
            True,
            b"",
        ),
        (
            "MyAbiEnum",
            "Nothing",
            True,
            b"",
        ),
        (
            "MyAbiEnum",
            0,
            False,
            b"\x00",
        ),
        (
            "MyAbiEnum",
            {"name": "Something", "discriminant": 1, "values": [10]},
            True,
            b"\x01\x00\x00\x00\x0A",
        ),
        (
            "MyAbiEnum",
            {
                "name": "SomethingMore",
                "values": [
                    15,
                    {
                        "field1": 7845,
                        "field2": [1, 2, 3],
                        "field3": [True, "TKN-abcdef"],
                    },
                ],
            },
            True,
            (
                b"\x02\x0F"
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                b"\x01"
                b"\x00\x00\x00\x0A"
                b"TKN-abcdef"
            ),
        ),
    ],
)
def test_encode_enum(
    enum_name: str, value: Any, top_encode: bool, expected_results: bytes
):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results = abi_serializer.encode_custom_enum(enum_name, value, top_encode)

    # Then
    assert expected_results == results


@pytest.mark.parametrize(
    "struct_name,value,expected_results",
    [
        (
            "MyAbiStruct2",
            {
                "field1": 7845,
                "field2": [1, 2, 3],
                "field3": [True, "TKN-abcdef"],
            },
            (
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                b"\x01"
                b"\x00\x00\x00\x0A"
                b"TKN-abcdef"
            ),
        ),
        (
            "MyAbiStruct2",
            [
                7845,
                [1, 2, 3],
                [True, "TKN-abcdef"],
            ],
            (
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                b"\x01"
                b"\x00\x00\x00\x0A"
                b"TKN-abcdef"
            ),
        ),
        (
            "MyAbiStruct",
            {
                "field1": 7845,
                "field2": [None, 1, None],
                "field3": [False, -1],
            },
            (
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x01\x00\x00\x00\x01\x00"
                b"\x00"
                b"\xFF\xFF\xFF\xFF"
            ),
        ),
    ],
)
def test_encode_struct(
    struct_name: str, value: Union[List, Dict], expected_results: bytes
):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results = abi_serializer.encode_custom_struct(struct_name, value)

    # Then
    assert expected_results == results


@pytest.mark.parametrize(
    "type_name,value,expected_results",
    [
        (
            "MyAbiStruct2",
            {
                "field1": 7845,
                "field2": [1, 2, 3],
                "field3": [True, "TKN-abcdef"],
            },
            (
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                b"\x01"
                b"\x00\x00\x00\x0A"
                b"TKN-abcdef"
            ),
        ),
        (
            "array5<u8>",
            [1, 2, 3, 4, 5],
            b"\x01\x02\x03\x04\x05",
        ),
        (
            "Option<BigUint>",
            16,
            b"\x01\x00\x00\x00\x01\x10",
        ),
        (
            "Option<BigUint>",
            None,
            b"\x00",
        ),
    ],
)
def test_nested_encode(type_name: str, value: Any, expected_results: bytes):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results = abi_serializer.nested_encode(type_name, value)

    # Then
    assert expected_results == results
