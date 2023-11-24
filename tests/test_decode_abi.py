from pathlib import Path
from typing import Any, Dict, List, Union

import pytest

from mxpyserializer.abi_serializer import AbiSerializer


def test_abi_loading():
    # Given
    file_path = Path("tests/data/mycontract.abi.json")

    # When
    abi_serializer = AbiSerializer.from_abi(file_path)

    # Then
    assert list(abi_serializer.endpoints.keys()) == ["getSum", "add"]
    assert list(abi_serializer.structs.keys()) == [
        "MyAbiStruct",
        "MyAbiStruct2",
        "Pair",
    ]
    assert list(abi_serializer.enums.keys()) == ["State", "MyAbiEnum"]

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
        (
            "MyAbiStruct",
            (
                b"\x00\x00\x00\x02\x1E\xA5"
                b"\x00\x00\x00\x03\x00\x01\x00\x00\x00\x01\x00"
                b"\x00"
                b"\xFF\xFF\xFF\xFF"
            ),
            {
                "field1": 7845,
                "field2": [None, 1, None],
                "field3": [False, -1],
            },
        ),
    ],
)
def test_decode_struct(struct_name: str, data: bytes, expected_results: Dict):
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
        (
            "Option<BigUint>",
            b"\x01\x00\x00\x00\x02\x00\x10\x02\x03\x04\x05\x1E\xA5",
            16,
            b"\x02\x03\x04\x05\x1E\xA5",
        ),
        (
            "Option<BigUint>",
            b"\x00\x00\x00\x00\x02\x00\x10\x02\x03\x04\x05\x1E\xA5",
            None,
            b"\x00\x00\x00\x02\x00\x10\x02\x03\x04\x05\x1E\xA5",
        ),
    ],
)
def test_nested_decode(
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


@pytest.mark.parametrize(
    "type_name,data,expected_results",
    [
        (
            "variadic<Pair>",
            [
                b"\x00\x00\x00\x01\x01\x01\x00\x00\x00\x0cESTAR-461bab\x00\x00\x00\x0c"
                b"WEGLD-bd4d79\x00\x00\x00\x11ESTARWEGLD-083383\x00\x00\x00\x12\x00\x00"
                b"\x00\n&ND\x16\xd5\x91\xcd\xa60M\x00\x00\x00\x08Pz\x83\xb0D\xc2\x14"
                b"\xeb\x00\x00\x00\x08m\xd1\xdc_\x13X\xdf\xee\x01",
                b"\x00\x00\x00\x02\x01\x01\x00\x00\x00\nMPH-f8ea2b\x00\x00\x00\x0cWEGLD"
                b"-bd4d79\x00\x00\x00\x0fMPHWEGLD-3deb18\x00\x00\x00\x12\x00\x00\x00"
                b"\x02\x02\xba\x00\x00\x00\x08\x0b\x13\xf4i\x82\xf1\x11\xec\x00\x00\x00"
                b"\x08\r}\t\xf3\x85N\xe12\x01",
                b"\x00\x00\x00\x03\x01\x01\x00\x00\x00\nGCC-3194ab\x00\x00\x00\x0bUSDC-"
                b"c76f1f\x00\x00\x00\x0eGCCUSDC-bff8c7\x00\x00\x00\x12\x00\x00\x00\n\tA"
                b"\x97(\xe4\x91\xbd\xd0\xc0\xa3\x00\x00\x00\x04|qy:\x00\x00\x00\t3\x88"
                b"\xec\xd4\xfb6\xff\x92\xdf\x01",
            ],
            [
                {
                    "enabled": True,
                    "first_token_id": "ESTAR-461bab",
                    "first_token_reserve": 180893678730462127075405,
                    "lp_token_decimal": 18,
                    "lp_token_id": "ESTARWEGLD-083383",
                    "lp_token_roles_are_set": True,
                    "lp_token_supply": 7913348321171267566,
                    "pair_id": 1,
                    "second_token_id": "WEGLD-bd4d79",
                    "second_token_reserve": 5799092263283987691,
                    "state": {"discriminant": 1, "name": "Active", "values": None},
                },
                {
                    "enabled": True,
                    "first_token_id": "MPH-f8ea2b",
                    "first_token_reserve": 698,
                    "lp_token_decimal": 18,
                    "lp_token_id": "MPHWEGLD-3deb18",
                    "lp_token_roles_are_set": True,
                    "lp_token_supply": 971944036100137266,
                    "pair_id": 2,
                    "second_token_id": "WEGLD-bd4d79",
                    "second_token_reserve": 798250292980290028,
                    "state": {"discriminant": 1, "name": "Active", "values": None},
                },
                {
                    "enabled": True,
                    "first_token_id": "GCC-3194ab",
                    "first_token_reserve": 43711228917631329288355,
                    "lp_token_decimal": 18,
                    "lp_token_id": "GCCUSDC-bff8c7",
                    "lp_token_roles_are_set": True,
                    "lp_token_supply": 950650442818273645279,
                    "pair_id": 3,
                    "second_token_id": "USDC-c76f1f",
                    "second_token_reserve": 2087811386,
                    "state": {"discriminant": 1, "name": "Active", "values": None},
                },
            ],
        ),
        ("State", b"", {"discriminant": 0, "name": "Inactive", "values": None}),
        ("List<u8>", b"\x01\x02\x01\x03", [1, 2, 1, 3]),
        ("bool", [b"\x01"], True),
        (
            "variadic<multi<bool,Option<u8>>>",
            [b"", b"", b"\x01", b"\x01\x08"],
            [[False, None], [True, 8]],
        ),
    ],
)
def test_top_decode(
    type_name: str, data: Union[bytes, List[bytes]], expected_results: Any
):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results = abi_serializer.top_decode(type_name, data)

    # Then
    assert expected_results == results
