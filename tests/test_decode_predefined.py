from typing import Dict

import pytest
from mxpyserializer.abi_serializer import AbiSerializer
from mxpyserializer.predefined_type import decimal_struct_to_decimal_str


@pytest.mark.parametrize(
    "decimal_struct,expected_result",
    [
        (
            {"data": 123456, "decimals": 3},
            "123.456",
        ),
        ({"data": 10, "decimals": 0}, "10"),
        ({"data": 15000, "decimals": 4}, "1.5000"),
        ({"data": 15, "decimals": 1}, "1.5"),
    ],
)
def test_decimal_struct_to_decimal_str(decimal_struct: Dict, expected_result: str):
    # Given
    # When
    result = decimal_struct_to_decimal_str(decimal_struct)

    # Then
    assert expected_result == result


@pytest.mark.parametrize(
    "type_name,data,expected_result",
    [
        ("ManagedDecimal<usize>", b"\x00\x00\x00\x01\x0a\x00\x00\x00\x00", "10"),
        ("ManagedDecimal<usize>", b"\x00\x00\x00\x01\x65\x00\x00\x00\x01", "10.1"),
        (
            "ManagedDecimal<1>",
            b"\x00\x00\x00\x01\x65",
            "10.1",
        ),
        (
            "ManagedDecimal<10>",
            b"\x00\x00\x00\x06\x01\x1f\x71\x82\xa0\x00",
            "123.4560000000",
        ),
        (
            "ManagedDecimal<usize>",
            b"\x00\x00\x00\x06\x01\x1f\x71\x82\xa0\x00\x00\x00\x00\x0a",
            "123.4560000000",
        ),
    ],
)
def test_nested_decode_managed_decimals(
    type_name: str, data: bytes, expected_result: str
):
    # Given
    abi_serializer = AbiSerializer()

    # When
    results, left_over_bytes = abi_serializer.nested_decode(type_name, data)

    # Then
    assert expected_result == results
    assert left_over_bytes == b""


@pytest.mark.parametrize(
    "type_name,data,expected_result",
    [
        ("ManagedDecimal<usize>", b"\x00\x00\x00\x01\x0a\x00\x00\x00\x00", "10"),
        ("ManagedDecimal<usize>", b"\x00\x00\x00\x01\x65\x00\x00\x00\x01", "10.1"),
        (
            "ManagedDecimal<1>",
            b"\x65",
            "10.1",
        ),
        (
            "ManagedDecimal<10>",
            b"\x01\x1f\x71\x82\xa0\x00",
            "123.4560000000",
        ),
        (
            "ManagedDecimal<usize>",
            b"\x00\x00\x00\x06\x01\x1f\x71\x82\xa0\x00\x00\x00\x00\x0a",
            "123.4560000000",
        ),
    ],
)
def test_top_decode_managed_decimals(type_name: str, data: bytes, expected_result: str):
    # Given
    abi_serializer = AbiSerializer()

    # When
    results = abi_serializer.top_decode(type_name, data)

    # Then
    assert expected_result == results
