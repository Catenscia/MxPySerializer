import base64
from pathlib import Path
from typing import Any, Dict, List, Union

from multiversx_sdk_network_providers.contract_query_response import (
    ContractQueryResponse,
)
import pytest

from mxpyserializer.abi_serializer import AbiSerializer


def test_abi_loading():
    # Given
    file_path = Path("tests/data/mycontract.abi.json")

    # When
    abi_serializer = AbiSerializer.from_abi(file_path)

    # Then
    assert list(abi_serializer.endpoints.keys()) == [
        "setConfig",
        "getSum",
        "add",
        "myEndpoint",
        "myEndpoint2",
        "endpoint_5",
        "getPairs",
        "swapMultiTokensFixedInput",
        "addLiquidity",
        "setSwapEnabledByUser",
        "init",
    ]
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
            b"\x01\x00\x00\x00\x01\x10\x02\x03\x04\x05\x1E\xA5",
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
            [
                {
                    "pair_id": 1,
                    "state": {"name": "Active", "discriminant": 1, "values": None},
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
                    "state": {"name": "Active", "discriminant": 1, "values": None},
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
                    "state": {"name": "Active", "discriminant": 1, "values": None},
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


@pytest.mark.parametrize(
    "return_data,endpoint_name,expected_result",
    [
        (
            [
                "AAAACg==",
                "AAAAeAEBY5L6MvMp/IWpWRnnjdLAMHLbORq20nPy6yGGe14/NtwAAAALTU1MRy05YTkwN2"
                "IAAAAMV0VHTEQtYmQ0ZDc5AAAAEE1NTEdXRUdMRC04MzBkZjIAAAASAAAAC2s2F3MlLnj1"
                "2ET3AAAACQED3roTHjjYfQAAAAgeTdFH8A0BhQE=",
                "AAAAeQIA7ZTU+9847vZKnJJ/1vFolYMeqSpPJgNwQT7GIeCKbwgAAAAOUEFEQVdBTi1hMT"
                "dmNTgAAAAKVEdSLTY4ZGExZQAAABFQQURBV0FOVEdSLTM1Y2YwMgAAABIAAAAKEOV6kSUp"
                "6VwAAAAAAAsaDmJr8jc9T4AAAAAAAAoQ5XqRJSnpXAAAAQ==",
            ],
            "getPairs",
            [
                10,
                {
                    "pair_id": 120,
                    "state": {"name": "Active", "discriminant": 1, "values": None},
                    "enabled": True,
                    "owner": (
                        "erd1vwf05vhn987gt22er8ncm5kqxped"
                        "kwg6kmf88uhtyxr8kh3lxmwqr7me6y"
                    ),
                    "first_token_id": "MMLG-9a907b",
                    "second_token_id": "WEGLD-bd4d79",
                    "lp_token_id": "MMLGWEGLD-830df2",
                    "lp_token_decimal": 18,
                    "first_token_reserve": 129610503061042963410339063,
                    "second_token_reserve": 18725608891927287933,
                    "lp_token_supply": 2183631501244825989,
                    "lp_token_roles_are_set": True,
                },
                {
                    "pair_id": 121,
                    "state": {
                        "name": "ActiveButNoSwap",
                        "discriminant": 2,
                        "values": None,
                    },
                    "enabled": False,
                    "owner": (
                        "erd1ak2df77l8rh0vj5ujfladutgjkp3a2"
                        "f2funqxuzp8mrzrcy2duyqxtgx9m"
                    ),
                    "first_token_id": "PADAWAN-a17f58",
                    "second_token_id": "TGR-68da1e",
                    "lp_token_id": "PADAWANTGR-35cf02",
                    "lp_token_decimal": 18,
                    "first_token_reserve": 79791000000000000000000,
                    "second_token_reserve": 31500000000000000000000000,
                    "lp_token_supply": 79791000000000000000000,
                    "lp_token_roles_are_set": True,
                },
            ],
        ),
        (["AQAAAAxXRUdMRC1hYmNkZWY="], "endpoint_5", ["WEGLD-abcdef"]),
    ],
)
def test_decode_from_query_response(
    return_data: List[str], endpoint_name: str, expected_result: List
):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)
    response = ContractQueryResponse()
    response.return_data = return_data
    response.return_code = "ok"

    # When
    results = abi_serializer.decode_contract_query_response(endpoint_name, response)

    # Then
    assert expected_result == results


@pytest.mark.parametrize(
    "b64_input_data,expected_results",
    [
        (
            "c2V0Q29uZmlnQDU3NDU0NzRDNDQyRDYyNjQzNDY0MzczOUA1NTUzNDQ0MzJENjMzNzM2NjYzM"
            "TY2QDQyNTU1MzQ0MkQzNDMwNjIzNTM3NjVANTU1MzQ0NTQyRDY2Mzg2MzMwMzg2M0AxRUAwMU"
            "AwOUBGMzQ2QTU1QkJGMzg0QjdFRkVDNDBCQ0M2Qzk2QzlGNjc4NDY0Q0IyN0M4ODNENzk0QTh"
            "EOEY4QzM1Njg2Q0Y4QDMwNEE4NkRCRjNBQzIyQjM4MUFBMEJCNTAxRjlCOUQzNTI0MjQ2MjRF"
            "QUVGNTNFRjUwQzE2NkQ1OTY0Qzc5QzhAMzU5M0YxNThEMUI4NjhBODA4OEFEMEFFNUREMTcwO"
            "EIyMzJBQjRENzA1ODI2MTQ4QjMwODgzRTcxMDNBMDY0OUAwMDAwMDAwMDAwMDAwMDAwMDUwME"
            "JFNEVCQTRCMkVDQ0JDRjE3MDNCQkQ2QjJFMEQxMzUxNDMwRTc2OUY1NDgzQDFCQzE2RDY3NEV"
            "DODAwMDA=",
            (
                "setConfig",
                [],
                [
                    "WEGLD-bd4d79",
                    "USDC-c76f1f",
                    "BUSD-40b57e",
                    "USDT-f8c08c",
                    30,
                    1,
                    9,
                    "erd17dr22kal8p9halkyp0xxe9kf7euyvn9j0jyr67223k8ccdtgdnuq2wfu5s",
                    "erd1xp9gdkln4s3t8qd2pw6sr7de6dfyy33yath48m6sc9ndt9jv08yqp84mtg",
                    "erd1xkflzkx3hp52szy26zh9m5ts3v3j4dxhqkpxzj9npzp7wyp6qeysfpqz2m",
                    "erd1qqqqqqqqqqqqqpgqhe8t5jewej70zupmh44jurgn29psua5l2jps3ntjj3",
                    2000000000000000000,
                ],
            ),
        ),
        (
            "RVNEVFRyYW5zZmVyQDU4NGM0ODJkMzg2NDYxNjEzNTMwQDQxZDZlODYyMjAyMzAwNDAwMEA3Mz"
            "c3NjE3MDRkNzU2Yzc0Njk1NDZmNmI2NTZlNzM0NjY5Nzg2NTY0NDk2ZTcwNzU3NEAwMTc1MmM2"
            "OWZhOGZmMDAwQDAxQDU4NGM0ODJkMzg2NDYxNjEzNTMwQDU3NDU0NzRjNDQyZDYyNjQzNDY0Mz"
            "czOQ==",
            (
                "swapMultiTokensFixedInput",
                [
                    {
                        "identifier": "XLH-8daa50",
                        "nonce": 0,
                        "amount": 1214524100000000000000,
                    }
                ],
                [105039000000000000, True, "XLH-8daa50", "WEGLD-bd4d79"],
            ),
        ),
        (
            "TXVsdGlFU0RUTkZUVHJhbnNmZXJAMDAwMDAwMDAwMDAwMDAwMDA1MDAwMGI0YzA5NDk0N2U0Mj"
            "dkNzk5MzFhOGJhZDgxMzE2Yjc5N2QyMzhjZGIzZkAwMkA1YTRmNDcyZDYzMzYzNjMyMzMzOUBA"
            "MDI4MjE1ZTQwNEA1NzQ1NDc0YzQ0MmQ2MjY0MzQ2NDM3MzlAQDE1ZjY5OTcxODIzNTMyQDYxNj"
            "Q2NDRjNjk3MTc1Njk2NDY5NzQ3OUAwMUAwMQ==",
            (
                "addLiquidity",
                [
                    {
                        "identifier": "ZOG-c66239",
                        "nonce": 0,
                        "amount": 10772407300,
                    },
                    {
                        "identifier": "WEGLD-bd4d79",
                        "nonce": 0,
                        "amount": 6182113405711666,
                    },
                ],
                [1, 1],
            ),
        ),
        (
            "TXVsdGlFU0RUTkZUVHJhbnNmZXJAMDJANGY0ZTQ1MmQ2NjM5MzkzNTM0NjZAMDBAMDNiOTJmNG"
            "JmZWQ5ZTI4MDAwQDRjNDU0NzRjNDQyZDY0MzczNDY0NjEzOUAwMEAwNzY4ZDgzNDBhNjFiMzQ2"
            "QDYxNjQ2NDRjNjk3MTc1Njk2NDY5NzQ3OUAwMUAwMQ==",
            (
                "addLiquidity",
                [
                    {
                        "identifier": "ONE-f9954f",
                        "nonce": 0,
                        "amount": 68684200000000000000,
                    },
                    {
                        "identifier": "LEGLD-d74da9",
                        "nonce": 0,
                        "amount": 533914273867477830,
                    },
                ],
                [1, 1],
            ),
        ),
        (
            "RVNEVE5GVFRyYW5zZmVyQDRjNGI0NTUzNDQ1NDJkNjY2MzMxMzk2MjYxQDM3QDMwMDJkY2RlYT"
            "AwY2I0ZmMxOEAwMDAwMDAwMDAwMDAwMDAwMDUwMDA2YjQ2YjE1MDkxZDczMGU1ZjNiOGM4N2Mz"
            "ZTljOGE1ZDgxOGM3YmE1NDgzQDczNjU3NDUzNzc2MTcwNDU2ZTYxNjI2YzY1NjQ0Mjc5NTU3Mz"
            "Y1NzJAMDAwMDAwMDAwMDAwMDAwMDA1MDA4YzY4YzMxMTg2YzNkOTZmYmEzOTMyZjM4ZDg1NDFm"
            "MjVmODkyOTFiNTQ4Mw==",
            (
                "setSwapEnabledByUser",
                [
                    {
                        "identifier": "LKESDT-fc19ba",
                        "nonce": 55,
                        "amount": 885649999999999999000,
                    }
                ],
                ["erd1qqqqqqqqqqqqqpgq335vxyvxc0vklw3extecmp2p7f0cj2gm2jpswk0kgg"],
            ),
        ),
    ],
)
def test_decode_endpoint_input_data(b64_input_data: str, expected_results: List):
    # Given
    file_path = Path("tests/data/mycontract.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)
    input_data = base64.b64decode(b64_input_data).decode()

    # When
    results = abi_serializer.decode_endpoint_input_data(input_data)

    # Then
    assert results == expected_results
