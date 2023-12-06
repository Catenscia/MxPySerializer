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


@pytest.mark.parametrize(
    "type_name,value,expected_results",
    [
        (
            "variadic<Pair>",
            [
                {
                    "pair_id": 1,
                    "state": "Active",
                    "enabled": True,
                    "owner": "erd19wjjxty40r6356r5mzjf2fmg8we2gxzshltunntk5tg45pl35"
                    "r7ql8yzym",
                    "first_token_id": "ESTAR-461bab",
                    "second_token_id": "WEGLD-bd4d79",
                    "lp_token_id": "ESTARWEGLD-083383",
                    "lp_token_decimal": 18,
                    "first_token_reserve": 191703201754102608732535,
                    "second_token_reserve": 5534808189818947114,
                    "lp_token_supply": 7936982366272361605,
                    "lp_token_roles_are_set": True,
                },
                {
                    "pair_id": 2,
                    "state": 1,
                    "enabled": True,
                    "owner": "erd1rfs4pg224d2wmndmntvu2dhfhesmuda6m502vt5mfctn3wg7"
                    "tu4sk6rtku",
                    "first_token_id": "MPH-f8ea2b",
                    "second_token_id": "WEGLD-bd4d79",
                    "lp_token_id": "MPHWEGLD-3deb18",
                    "lp_token_decimal": 18,
                    "first_token_reserve": 483,
                    "second_token_reserve": 939815210710785732,
                    "lp_token_supply": 871944036100137266,
                    "lp_token_roles_are_set": True,
                },
                {
                    "pair_id": 3,
                    "state": {"name": "Active", "values": None},
                    "enabled": True,
                    "owner": "erd1l8qmksyvfgn60hqhqgucufzx5adp4kny8gf07vypmgytyxqc"
                    "gr9q3u6jnk",
                    "first_token_id": "GCC-3194ab",
                    "second_token_id": "USDC-c76f1f",
                    "lp_token_id": "GCCUSDC-bff8c7",
                    "lp_token_decimal": 18,
                    "first_token_reserve": 42888081699184316689810,
                    "second_token_reserve": 2128039321,
                    "lp_token_supply": 950650442818273645279,
                    "lp_token_roles_are_set": True,
                },
            ],
            [
                b"\x00\x00\x00\x01\x01\x01+\xa5#,\x95x\xf5\x1aht\xd8\xa4\x95'h;\xb2\xa4"
                b"\x18P\xbf\xd7\xc9\xcdv\xa2\xd1Z\x07\xf1\xa0\xfc\x00\x00\x00\x0c"
                b"ESTAR-461bab\x00\x00\x00\x0cWEGLD-bd4d79\x00\x00\x00\x11"
                b"ESTARWEGLD-083383\x00\x00\x00\x12\x00\x00\x00\n(\x98@[$CV\xf4\xa1w"
                b"\x00\x00\x00\x08L\xcf\x96\xb9V\x14\xc6*\x00\x00\x00\x08n%\xd3i\x024"
                b"\x14\x85\x01",
                b"\x00\x00\x00\x02\x01\x01\x1aaP\xa1J\xabT\xed\xcd\xbb\x9a\xd9\xc56\xe9"
                b"\xbea\xbe7\xba\xdd\x1e\xa6.\x9bN\x178\xb9\x1e_+\x00\x00\x00\n"
                b"MPH-f8ea2b\x00\x00\x00\x0cWEGLD-bd4d79\x00\x00\x00\x0fMPHWEGLD-3deb18"
                b"\x00\x00\x00\x12\x00\x00\x00\x02\x01\xe3\x00\x00\x00\x08\r\n\xe4\xf4l"
                b"\xec\xde\xc4\x00\x00\x00\x08\x0c\x19\xc4{'\xc4\xe12\x01",
                b"\x00\x00\x00\x03\x01\x01\xf9\xc1\xbb@\x8cJ'\xa7\xdc\x17\x029\x8e$F"
                b"\xa7Z\x1a\xdad:\x12\xff0\x81\xda\x08\xb2\x18\x18@\xca\x00\x00\x00\n"
                b"GCC-3194ab\x00\x00\x00\x0bUSDC-c76f1f\x00\x00\x00\x0eGCCUSDC-bff8c7"
                b"\x00\x00\x00\x12\x00\x00\x00\n\t\x14\xf7\xb2\x82\x9c\xd4\xc2\xad\x92"
                b"\x00\x00\x00\x04~\xd7M\x99\x00\x00\x00\t3\x88\xec\xd4\xfb6\xff\x92"
                b"\xdf\x01",
            ],
        ),
        (
            "State",
            "Inactive",
            b"",
        ),
        ("List<u8>", [1, 2, 1, 3], b"\x01\x02\x01\x03"),
        ("bool", True, b"\x01"),
        (
            "variadic<multi<bool,Option<u8>>>",
            [[False, None], [True, 8]],
            [b"", b"", b"\x01", b"\x01\x08"],
        ),
    ],
)
def test_top_encode(type_name: str, value: Any, expected_results: bytes):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results = abi_serializer.top_encode(type_name, value)

    # Then
    assert expected_results == results


@pytest.mark.parametrize(
    "endpoint_name, values,expected_results",
    [
        (
            "myEndpoint",
            [15, True, "TFK-15987", "TRE-abcdef"],
            [b"\x0F", b"\x01", b"TFK-15987", b"TRE-abcdef"],
        ),
        ("myEndpoint", [15, False], [b"\x0F", b""]),
        ("myEndpoint2", [15], [b"\x0F"]),
        ("myEndpoint2", [15, 16], [b"\x0F", b"\x10"]),
        (
            "endpoint_5_bis",
            ["WEGLD-abcdef", 789],
            [b"\x01\x00\x00\x00\x0cWEGLD-abcdef", b"\x03\x15"],
        ),
    ],
)
def test_inputs_encode(endpoint_name: str, values: List, expected_results: List[bytes]):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)

    # When
    results = abi_serializer.encode_endpoint_inputs(endpoint_name, values)

    # Then
    assert expected_results == results
