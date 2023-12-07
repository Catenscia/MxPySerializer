# First Scene

In this section, we will create our first query while encoding the inputs and decoding the results with `MxPySerializer`.
We will select the pair contract of OneDex and query the information of one of its pools.

## Serializer

To create a serializer, the object that will encode and decode our data, we just have to pass it the path to the ABI file of the OneDex contract.

```python
from pathlib import Path
from mxpyserializer.abi_serializer import AbiSerializer

file_path = Path("abis/onedex-sc.abi.json")
abi_serializer = AbiSerializer.from_abi(file_path)
```

## Input Encoding

The endpoint we will call, `viewPair`, requires as input the id of the pair. We will take a random id, for example 57.
The serializer will be in charge of encoding the input as the endpoint `viewPair` expects it.

```python
endpoint_name = "viewPair"
args = [57]  # id of the Pair
encoded_args = abi_serializer.encode_endpoint_inputs(endpoint_name, args)
```

## Query

Make the query as usual

```python
from multiversx_sdk_core import Address, ContractQueryBuilder
from multiversx_sdk_network_providers import ProxyNetworkProvider

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
```

## Parse the results

You can now give the results to `MxPySerializer` so that he can decode them and make them readable!

```python
parsed_results = abi_serializer.decode_contract_query_response(
        endpoint_name, response
    )
print(json.dumps(parsed_results, indent=4))
```

```json
[
    {
        "pair_id": 57,
        "state": {
            "name": "Active",
            "discriminant": 1,
            "values": null
        },
        "enabled": true,
        "owner": "erd1vudplk63q6fph97suwkqeafw2hmlgctp2aqszsxhv5ur3lkvgrmscg53uk",
        "first_token_id": "HYPE-619661",
        "second_token_id": "LEGLD-d74da9",
        "lp_token_id": "HYPELEGLD-d65493",
        "lp_token_decimal": 18,
        "first_token_reserve": 27675995026043458404845725,
        "second_token_reserve": 586365485849411410,
        "lp_token_supply": 1016042899275369744,
        "lp_token_roles_are_set": true
    }
]
```

And that's it!

## Complete code

```python
import json
from pathlib import Path
from multiversx_sdk_core import Address, ContractQueryBuilder

from multiversx_sdk_network_providers import ProxyNetworkProvider

from mxpyserializer.abi_serializer import AbiSerializer

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
```