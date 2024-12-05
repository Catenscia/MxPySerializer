from decimal import Decimal
from typing import Any, Dict, Optional

import pytest
from mxpyserializer.abi_serializer import AbiSerializer
from mxpyserializer.predefined_type import decimal_arg_to_decimal_struct


@pytest.mark.parametrize(
    "type_name,data,expected_results",
    [
        ("ManagedDecimal<usize>", 10, b"\x00\x00\x00\x01\x0a\x00\x00\x00\x00"),
        ("ManagedDecimal<usize>", "10", b"\x00\x00\x00\x01\x0a\x00\x00\x00\x00"),
        (
            "ManagedDecimal<usize>",
            "10.1",
            b"\x00\x00\x00\x01\x65\x00\x00\x00\x01",
        ),
        (
            "ManagedDecimal<1>",
            "10.1",
            b"\x00\x00\x00\x01\x65",
        ),
        (
            "ManagedDecimal<10>",
            "123.456",
            b"\x00\x00\x00\x06\x01\x1f\x71\x82\xa0\x00",
        ),
        (
            "ManagedDecimal<usize>",
            "123.4560000000",
            b"\x00\x00\x00\x06\x01\x1f\x71\x82\xa0\x00\x00\x00\x00\x0a",
        ),
    ],
)
def test_nested_encode_managed_decimals(
    type_name: str, data: Any, expected_results: bytes
):
    # Given
    abi_serializer = AbiSerializer()

    # When
    results = abi_serializer.nested_encode(type_name, data)

    # Then
    assert expected_results == results


@pytest.mark.parametrize(
    "type_name,data,expected_results",
    [
        ("ManagedDecimal<usize>", 10, b"\x00\x00\x00\x01\x0a\x00\x00\x00\x00"),
        ("ManagedDecimal<usize>", "10", b"\x00\x00\x00\x01\x0a\x00\x00\x00\x00"),
        (
            "ManagedDecimal<usize>",
            "10.1",
            b"\x00\x00\x00\x01\x65\x00\x00\x00\x01",
        ),
        (
            "ManagedDecimal<1>",
            "10.1",
            b"\x65",
        ),
        (
            "ManagedDecimal<10>",
            "123.456",
            b"\x01\x1f\x71\x82\xa0\x00",
        ),
        (
            "ManagedDecimal<usize>",
            "123.4560000000",
            b"\x00\x00\x00\x06\x01\x1f\x71\x82\xa0\x00\x00\x00\x00\x0a",
        ),
    ],
)
def test_top_encode_managed_decimals(
    type_name: str, data: Any, expected_results: bytes
):
    # Given
    abi_serializer = AbiSerializer()

    # When
    results = abi_serializer.top_encode(type_name, data)

    # Then
    assert expected_results == results


@pytest.mark.parametrize(
    "arg,decimals,expected_result",
    [
        (
            "123.456",
            3,
            {"data": 123456, "decimals": 3},
        ),
        (
            "123.456",
            None,
            {"data": 123456, "decimals": 3},
        ),
        (
            "10",
            None,
            {"data": 10, "decimals": 0},
        ),
        (
            10,
            None,
            {"data": 10, "decimals": 0},
        ),
        (
            1.5,
            4,
            {"data": 15000, "decimals": 4},
        ),
        (
            Decimal("1.5"),
            4,
            {"data": 15000, "decimals": 4},
        ),
    ],
)
def test_decimal_arg_to_decimal_struct(
    arg: Any, decimals: Optional[int], expected_result: Dict
):
    # Given
    # When
    result = decimal_arg_to_decimal_struct(arg, decimals)

    # Then
    assert expected_result == result
