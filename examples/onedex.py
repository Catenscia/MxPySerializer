"""
author: Etienne Wallet

Some example interactions with the OneDex Pair contract
"""

import json
from pathlib import Path
from multiversx_sdk_core import Address, ContractQueryBuilder

from multiversx_sdk_network_providers import ProxyNetworkProvider

from mxpyserializer.abi_serializer import AbiSerializer


def example_get_pair_status():
    """
    In this example we query the status of pool pair and display it
    """
    # create the serializer and encode the arguments
    file_path = Path("abis/onedex-sc.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)
    endpoint_name = "viewPair"
    args = [57]  # id of the Pair
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)

    # create the query as usual
    proxy_provider = ProxyNetworkProvider("https://gateway.multiversx.com")
    builder = ContractQueryBuilder(
        contract=Address.from_bech32(
            "erd1qqqqqqqqqqqqqpgqqz6vp9y50ep867vnr296mqf3dduh6guvmvlsu3sujc"
        ),
        function=endpoint_name,
        call_arguments=encoded_args,
    )
    query = builder.build()
    response = proxy_provider.query_contract(query)

    # parse the results and display them
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )
    print(json.dumps(parsed_results, indent=4))


def example_get_amount_in():
    """
    In this example, we ask the contract how much token we should send to get
    a desired amount of output token
    """
    # create the serializer and encode the arguments
    file_path = Path("abis/onedex-sc.abi.json")
    abi_serializer = AbiSerializer.from_abi(file_path)
    endpoint_name = "getAmountIn"
    args = [
        "USDC-c76f1f",  # token in
        "WEGLD-bd4d79",  # token out
        1000000000000000000,  # wanted amount of token out, here 1 WEGLD
    ]
    encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)

    # create the query as usual
    proxy_provider = ProxyNetworkProvider("https://gateway.multiversx.com")
    builder = ContractQueryBuilder(
        contract=Address.from_bech32(
            "erd1qqqqqqqqqqqqqpgqqz6vp9y50ep867vnr296mqf3dduh6guvmvlsu3sujc"
        ),
        function=endpoint_name,
        call_arguments=encoded_args,
    )
    query = builder.build()
    response = proxy_provider.query_contract(query)

    # parse the results and display them
    parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )
    print(json.dumps(parsed_results, indent=4))


if __name__ == "__main__":
    example_get_pair_status()
    example_get_amount_in()
