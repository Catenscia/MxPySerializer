import os
from pathlib import Path

from dotenv import load_dotenv
from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_core import Address
import pytest

from mxpyserializer.abi_serializer import AbiSerializer

load_dotenv("./.env")


@pytest.fixture
def contract_address():
    return Address.from_bech32(os.getenv("TEST_CONTRACT_ADDRESS"))


@pytest.fixture
def proxy_provider():
    return ProxyNetworkProvider(os.getenv("PROXY"))


@pytest.fixture
def abi_serializer():
    return AbiSerializer.from_abi(Path("test-contract/output/test-contract.abi.json"))
