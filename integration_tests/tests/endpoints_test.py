from typing import List
from multiversx_sdk_core import Address, ContractQueryBuilder
from multiversx_sdk_network_providers import ProxyNetworkProvider
import pytest

from mxpyserializer.abi_serializer import AbiSerializer


def test_endpoint_1(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
):
    # Given
    endpoint_name = "endpoint_1"
    args = []

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == args


def test_endpoint_2(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
):
    # Given
    endpoint_name = "endpoint_2"
    args = [4, 75, 874566, 8984584484, 1848]

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == args


def test_endpoint_3(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
):
    # Given
    endpoint_name = "endpoint_3"
    args = [-4, -75, -874566, 8984584484, -1848]

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == args


@pytest.mark.parametrize(
    "args",
    [
        [
            "WEGLD-abcdef",
            "erd1qqqqqqqqqqqqqpgqf48ydzn8shr8mnmrvydq2fn9v2afzd3c4fvsk4wglm",
        ],
        [
            "WEGLD-abcdef",
            Address.from_bech32(
                "erd1qqqqqqqqqqqqqpgqf48ydzn8shr8mnmrvydq2fn9v2afzd3c4fvsk4wglm"
            ),
        ],
    ],
)
def test_endpoint_4(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
    args: List,
):
    # Given
    endpoint_name = "endpoint_4"

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == [
        "WEGLD-abcdef",
        "erd1qqqqqqqqqqqqqpgqf48ydzn8shr8mnmrvydq2fn9v2afzd3c4fvsk4wglm",
    ]


def test_endpoint_5(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
):
    # Given
    endpoint_name = "endpoint_5"
    args = ["WEGLD-abcdef"]

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == args


def test_endpoint_5_bis(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
):
    # Given
    endpoint_name = "endpoint_5_bis"
    args = ["WEGLD-abcdef", 789]

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)

    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == args


def test_endpoint_6(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
):
    # Given
    endpoint_name = "endpoint_6"
    args = [7846, 1, 2, 3]

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == args


def test_endpoint_7(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
):
    # Given
    endpoint_name = "endpoint_7"
    args = [
        "Monday",
        "Sunday",
        "Default",
        {"name": "Today", "values": ["Tuesday"]},
        {"name": "Write", "values": [b"\x01\x02\x04\x08", 14]},
        {
            "name": "Struct",
            "values": [8, b"\x09\x2D", 0, 789484, 485],
        },
    ]

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == [
        {"name": "Monday", "discriminant": 0, "values": None},
        {"name": "Sunday", "discriminant": 6, "values": None},
        {"name": "Default", "discriminant": 0, "values": None},
        {
            "name": "Today",
            "discriminant": 1,
            "values": [{"name": "Tuesday", "discriminant": 1, "values": None}],
        },
        {
            "name": "Write",
            "discriminant": 2,
            "values": [b"\x01\x02\x04\x08", 14],
        },
        {
            "name": "Struct",
            "discriminant": 3,
            "values": [8, b"\x09\x2D", 0, 789484, 485],
        },
    ]


def test_endpoint_8(
    proxy_provider: ProxyNetworkProvider,
    contract_address: Address,
    abi_serializer: AbiSerializer,
):
    # Given
    endpoint_name = "endpoint_8"
    args = [
        ["WEGLD-abcdef", 0, 89784651],
        ["MEX-abcdef", 0, 184791484],
    ]

    # When
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
    query = ContractQueryBuilder(
        contract=contract_address,
        function=endpoint_name,
        call_arguments=encoded_args,
    ).build()
    response = proxy_provider.query_contract(query)
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )

    # Then
    assert parsed_results == [
        {"token_identifier": "WEGLD-abcdef", "token_nonce": 0, "amount": 89784651},
        {"token_identifier": "MEX-abcdef", "token_nonce": 0, "amount": 184791484},
    ]
