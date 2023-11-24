from pathlib import Path
from typing import Any, Dict

import pytest

from mxpyserializer.abi_serializer import AbiSerializer


def test_abi_loading():
    # Given
    file_path = Path("tests/data/mycontract.abi.json")

    # When
    abi_serializer = AbiSerializer.from_abi(file_path)

    # Then
    assert list(abi_serializer.endpoints.keys()) == ["getSum", "add"]
    assert list(abi_serializer.structs.keys()) == ["MyAbiStruct", "MyAbiStruct2"]
    assert list(abi_serializer.enums.keys()) == ["MyAbiEnum"]

    assert len(abi_serializer.structs["MyAbiStruct"].fields) == 3


@pytest.mark.parametrize(
    "enum_name,data,expected_results",
    [
        ("MyAbiEnum", b"", {"name": "Nothing", "discriminant": 0, "values": None}),
        ("MyAbiEnum", b"\x00", {"name": "Nothing", "discriminant": 0, "values": None}),
        (
            "MyAbiEnum",
            b"\x01\x00\x00\x00\x0A",
            {"name": "Something", "discriminant": 1, "values": [10]},
        ),
        (
            "MyAbiEnum",
            (
                b"\x02\x0F"
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                b"\x01"
                b"\x00\x00\x00\x0A"
                b"TKN-abcdef"
            ),
            {
                "name": "SomethingMore",
                "discriminant": 2,
                "values": [
                    15,
                    {
                        "field1": 7845,
                        "field2": [1, 2, 3],
                        "field3": [True, "TKN-abcdef"],
                    },
                ],
            },
        ),
    ],
)
def test_decode_enum(enum_name: str, data: bytes, expected_results: Dict):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results, data = abi_serializer.decode_custom_enum(enum_name, data)

    # Then
    assert expected_results == results


@pytest.mark.parametrize(
    "struct_name,data,expected_results",
    [
        (
            "MyAbiStruct2",
            (
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                b"\x01"
                b"\x00\x00\x00\x0A"
                b"TKN-abcdef"
            ),
            {
                "field1": 7845,
                "field2": [1, 2, 3],
                "field3": [True, "TKN-abcdef"],
            },
        ),
    ],
)
def test_nested_decode(struct_name: str, data: bytes, expected_results: Dict):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results, data = abi_serializer.decode_custom_struct(struct_name, data)

    # Then
    assert expected_results == results


@pytest.mark.parametrize(
    "type_name,data,expected_results,expected_left_over_data",
    [
        (
            "MyAbiStruct2",
            (
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03"
                b"\x01"
                b"\x00\x00\x00\x0A"
                b"TKN-abcdef"
                b"\x00\x00\x00\x0A"
            ),
            {
                "field1": 7845,
                "field2": [1, 2, 3],
                "field3": [True, "TKN-abcdef"],
            },
            b"\x00\x00\x00\x0A",
        ),
        (
            "array5<u8>",
            b"\x01\x02\x03\x04\x05\x1E\xA5",
            [1, 2, 3, 4, 5],
            b"\x1E\xA5",
        ),
    ],
)
def test_decode_struct(
    type_name: str, data: bytes, expected_results: Any, expected_left_over_data: bytes
):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results, left_over_data = abi_serializer.nested_decode(type_name, data)

    # Then
    assert expected_results == results
    assert expected_left_over_data == left_over_data
