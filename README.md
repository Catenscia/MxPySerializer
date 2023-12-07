# MxPySerializer
MxPySerializer is a python package that serialize and deserialize MultiversX data format by using ABI definitions.

## Installation

Install MxPySerializer with PyPi

```bash
pip install -U mxpyserializer
```

## Quick Example

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

## Documentation

Heads up to the [documentation](https://mxpyserializer.readthedocs.io) to get started!

## Contribution

If you have a feedback, a proposal or if you want to contribute, don't hesitate! we welcome all hands on board :wink: