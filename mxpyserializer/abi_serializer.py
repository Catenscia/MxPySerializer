"""
author: Etienne Wallet

This module contains the abi parser class which also have the methods to serialize
and deserialize complex types
"""

from __future__ import annotations
from copy import deepcopy
from dataclasses import asdict
import json

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable

from multiversx_sdk_core import Address
from multiversx_sdk_core.errors import ErrBadPubkeyLength
from multiversx_sdk_network_providers.contract_query_response import (
    ContractQueryResponse,
)

from mxpyserializer import basic_type, errors
from mxpyserializer.data_models import AbiEndpoint, AbiField, AbiStruct, AbiEnum


class AbiSerializer:
    """
    This class is contructed from an ABI file and provides methods to
    serialize and deserialize data according to ABI definitions.
    """

    def __init__(
        self,
        endpoints: Optional[Dict[str, AbiEndpoint]] = None,
        structs: Optional[Dict[str, AbiStruct]] = None,
        enums: Optional[Dict[str, AbiEnum]] = None,
    ):
        self.endpoints = {} if endpoints is None else endpoints
        self.structs = {} if structs is None else structs
        self.enums = {} if enums is None else enums

    def to_dict(self) -> Dict:
        """
        Export this instance as a Dict

        :return: instance as dict
        :rtype: Dict
        """
        return {
            "endpoints": {e: asdict(v) for e, v in self.endpoints.items()},
            "structs": {e: asdict(v) for e, v in self.structs.items()},
            "enums": {e: asdict(v) for e, v in self.enums.items()},
        }

    @staticmethod
    def from_dict(data: Dict) -> AbiSerializer:
        """
        Parse a dictionnary representing an AbiSerializer and instantiate it

        :param data: data to parse
        :type data: Dict
        :return: instance generated from the file
        :rtype: AbiSerializer
        """
        return AbiSerializer(
            endpoints={
                e: AbiEndpoint.from_dict(v) for e, v in data["endpoints"].items()
            },
            structs={e: AbiStruct.from_dict(v) for e, v in data["structs"].items()},
            enums={e: AbiEnum.from_dict(v) for e, v in data["enums"].items()},
        )

    @staticmethod
    def from_abi_dict(data: Dict) -> AbiSerializer:
        """
        Parse a dictionnary as an ABI file and construct an AbiSerializer
        instance accordingly

        :param data: data to parse
        :type data: Dict
        :return: instance generated from the file
        :rtype: AbiSerializer
        """
        endpoints = {}
        if "endpoints" in data:
            for endpoint in data["endpoints"]:
                endpoints[endpoint["name"]] = AbiEndpoint.from_dict(endpoint)

        if "constructor" in data:
            endpoint_kargs = {
                "name": "init",
                "mutability": "mutable",
                **data["constructor"],
            }
            endpoints[endpoint_kargs["name"]] = AbiEndpoint.from_dict(endpoint_kargs)

        structs = {}
        enums = {}
        for type_name, element in data.get("types", {}).items():
            if element["type"] == "struct":
                structs[type_name] = AbiStruct.from_dict({"name": type_name, **element})
            elif element["type"] == "enum":
                enums[type_name] = AbiEnum.from_dict({"name": type_name, **element})
            else:
                raise errors.UnknownCustomTypeType(type_name, element["type"])

        return AbiSerializer(endpoints, structs, enums)

    @classmethod
    def from_abi(cls, abi_file_path: Path) -> AbiSerializer:
        """
        Read an ABI file and construct an AbiSerializer instance accordingly

        :param abi_file_path: path to the ABI file
        :type abi_file_path: Path
        :return: instance generated from the file
        :rtype: AbiSerializer
        """
        with open(abi_file_path.as_posix(), "r", encoding="utf-8") as file:
            raw_content = json.load(file)
        return cls.from_abi_dict(raw_content)

    def decode_iterable(
        self, inner_types: List[str], data: bytes
    ) -> Tuple[List[Any], bytes]:
        """
        Decodes a part of the input data as a concatenation of nested encoded elements.
        Returns the left over.

        :param inner_types: types of the concatenated elements to retrieve, in order.
        :type inner_types: List[str]
        :param data: data containing the values to extract
        :type data: bytes
        :return: list of decoded values and the left over bytes
        :rtype: Tuple[List[Any], bytes]
        """
        decoded_values = []
        for inner_type in inner_types:
            result, data = self.nested_decode(inner_type, data)
            decoded_values.append(result)
        return decoded_values, data

    def top_encode_iterable(self, inner_types: List[str], value: List[Any]) -> bytes:
        """
        Encode the input value as a concatenation of nested encoded elements.

        :param inner_types: types of the concatenated elements to encode, in order.
        :type inner_types: List[str]
        :param value: list containing the values to encode
        :type value: List[Any]
        :return: encoded value
        :rtype: bytes
        """
        encoded_value = bytes()
        if len(value) != len(inner_types):
            raise errors.ElementsNumberMismatch(value, inner_types)
        for inner_type, inner_value in zip(inner_types, value):
            encoded_value += self.nested_encode(inner_type, inner_value)
        return encoded_value

    def top_decode_iterable(self, inner_type: str, data: bytes) -> List[Any]:
        """
        Decodes a part of the input data as a concatenation of top encoded elements.

        :param inner_type: type of the concatenated elements to retrieve
        :type inner_type: str
        :param data: data containing the values to extract
        :type data: bytes
        :return: list of decoded values
        :rtype: List[Any]
        """
        decoded_values = []
        while len(data) > 0:
            result, data = self.nested_decode(inner_type, data)
            decoded_values.append(result)
        return decoded_values

    def nested_decode_fields(
        self, fields: List[AbiField], data: bytes
    ) -> Tuple[Dict[str, Any], bytes]:
        """
        Decodes a part of the input data as a concatenation of nested encoded elements.
        Returns the left over.

        :param fields: each field  must contains the keys "name" and "type"
        :type fields: List[AbiField]
        :param data: data containing the values to extract
        :type data: bytes
        :return: tuple of a Dict of field name with their decoded values
                and the left over bytes
        :rtype: Tuple[Dict[str, Any], bytes]
        """
        decoded_values = {}
        for field in fields:
            result, data = self.nested_decode(field.type, data)
            decoded_values[field.name] = result
        return decoded_values, data

    def decode_custom_struct(
        self, type_name: str, data: bytes
    ) -> Tuple[Dict[str, Any], bytes]:
        """
        Decodes a part of the input data assuming it is a custom struct defined in the
        ABI. All childs elements of the structures are always nested encoded.
        Returns the left over.

        :param type_name: name of the type of the value to extract from the data
        :type type_name: str
        :param data: data containing the value to extract
        :type data: bytes
        :return: decoded structure and the left over bytes
        :rtype: Tuple[Dict[str, Any], bytes]
        """
        try:
            type_definition = self.structs[type_name]
        except KeyError as err:
            raise errors.UnknownStruct(type_name) from err

        return self.nested_decode_fields(type_definition.fields, data)

    def encode_custom_struct(self, type_name: str, data: Union[Dict, List]) -> bytes:
        """
        Encodes the input data assuming it is a custom struct defined in the
        ABI. All childs elements of the structures are always nested encoded.

        :param type_name: name of the type of the value to extract from the data
        :type type_name: str
        :param data: data to encode
        :type data: Union[Dict, List]
        :return: encoded struct
        :rtype: bytes
        """
        try:
            type_definition = self.structs[type_name]
        except KeyError as err:
            raise errors.UnknownStruct(type_name) from err
        if len(data) != len(type_definition.fields):
            raise errors.ElementsNumberMismatch(data, type_definition.fields)
        if isinstance(data, List):
            data = {field.name: d for field, d in zip(type_definition.fields, data)}
        results = bytes()
        for field in type_definition.fields:
            try:
                value = data[field.name]
            except KeyError as err:
                raise errors.MissingStuctField(type_name, field.name) from err
            results += self.nested_encode(field.type, value)
        return results

    def decode_custom_enum(
        self, type_name: str, data: bytes
    ) -> Tuple[Dict[str, Any], bytes]:
        """
        Decodes a part of the input data assuming it is a custom enum defined in the
        ABI. All childs elements of the enums are always nested encoded.
        Returns the left over.

        :param type_name: name of the type of the value to extract from the data
        :type type_name: str
        :param data: data containing the value to extract
        :type data: bytes
        :return: decoded enum and the left over bytes
        :rtype: Tuple[Dict[str, Any], bytes]
        """
        try:
            abi_enum = self.enums[type_name]
        except KeyError as err:
            raise errors.UnknownEnum(type_name) from err

        if len(data) == 0:  # Top encoding case for discriminant 0
            discriminant = 0
        else:
            discriminant, data = basic_type.nested_decode_basic("i8", data)

        selected_variant = None
        for variant in abi_enum.variants:
            if variant.discriminant == discriminant:
                selected_variant = variant
                break

        if selected_variant is None:
            raise errors.UnknownEnumDiscriminant(type_name, discriminant)

        if len(selected_variant.fields):
            inner_types = [f.type for f in selected_variant.fields]
            inner_values, data = self.decode_iterable(inner_types, data)
        else:
            inner_values = None

        decoded_enum = {
            "name": selected_variant.name,
            "discriminant": discriminant,
            "values": inner_values,
        }
        return decoded_enum, data

    def encode_custom_enum(
        self, type_name: str, value: Any, top_encode: bool = False
    ) -> bytes:
        """
        Encode the input data assuming it is a custom enum defined in the
        ABI. All childs elements of the enums are always nested encoded.

        :param type_name: name of the type of the value to extract from the data
        :type type_name: str
        :param value: value to encode. Can be the discriminant, the name. If the enum
            variant must contains inner values, then it should be passed as a Dict
            containing the keys 'values' and one of 'discriminant' or 'name'
        :type value: Any
        :param top_encode: is the encoding should be a top or a nested encoding
        :type top_encode: bool, default to False
        :return: encoded enum
        :rtype: bytes
        """
        try:
            abi_enum = self.enums[type_name]
        except KeyError as err:
            raise errors.UnknownEnum(type_name) from err
        if isinstance(value, int):  # assuming discriminant
            discriminant, name, inner_values = value, None, None
        elif isinstance(value, str):  # assuming name
            discriminant, name, inner_values = None, value, None
        elif isinstance(value, Dict):  # assuming full definition
            discriminant = value.get("discriminant", None)
            name = value.get("name", None)
            inner_values = value.get("values", None)
        else:
            raise TypeError(
                f"Enum value should be an int, a str or a dict, got {type(value)}"
            )

        selected_variant = None
        for variant in abi_enum.variants:
            if variant.discriminant == discriminant or variant.name == name:
                selected_variant = variant
                break

        if selected_variant is None:
            raise errors.EnumVariantNotFound(type_name, name, discriminant)

        if top_encode and selected_variant.discriminant == 0 and inner_values is None:
            return bytes()

        encoded_discriminant = basic_type.nested_encode_basic(
            "i8", selected_variant.discriminant
        )
        if len(selected_variant.fields):
            if not isinstance(inner_values, list):
                raise TypeError(
                    "Expected a list of inner values for variant "
                    f"{selected_variant.discriminant} of the enum {type_name}"
                )
            inner_types = [f.type for f in selected_variant.fields]
            encoded_inner_values = self.top_encode_iterable(inner_types, inner_values)
        else:
            encoded_inner_values = bytes()
        return encoded_discriminant + encoded_inner_values

    def nested_decode(self, type_name: str, data: bytes) -> Tuple[Any, bytes]:
        """
        Decodes a part of the input data assuming a nested-encoded
        format. Returns the left over.

        :param type_name: name of the type of the value to extract from the data
        :type type_name: str
        :param data: data containing the value to extract
        :type data: bytes
        :return: decoded value and the left over bytes
        :rtype: Tuple[Any, bytes]
        """
        if type_name in basic_type.BASIC_TYPES:
            return basic_type.nested_decode_basic(type_name, data)

        list_pattern = re.match(r"^List<(.*)>$", type_name)
        if list_pattern is not None:
            inner_type_name = list_pattern.groups()[0]
            list_size, data = basic_type.nested_decode_basic("u32", data)
            return self.decode_iterable(list_size * [inner_type_name], data)

        array_pattern = re.match(r"^array(\d+)<(.*)>$", type_name)
        if array_pattern is not None:
            array_size = int(array_pattern.groups()[0])
            inner_type_name = array_pattern.groups()[1]
            return self.decode_iterable(array_size * [inner_type_name], data)

        tuple_pattern = re.match(r"^tuple<(.*)>$", type_name)
        if tuple_pattern is not None:
            inner_types = tuple_pattern.groups()[0].replace(" ", "").split(",")
            return self.decode_iterable(inner_types, data)

        option_pattern = re.match(r"^Option<(.*)>$", type_name)
        if option_pattern is not None:
            is_some, data = basic_type.nested_decode_basic("bool", data)
            if is_some:
                inner_type_name = option_pattern.groups()[0]
                return self.nested_decode(inner_type_name, data)
            return None, data

        if type_name in self.structs:
            return self.decode_custom_struct(type_name, data)

        if type_name in self.enums:
            return self.decode_custom_enum(type_name, data)

        raise errors.UnknownType(type_name)

    def nested_encode(self, type_name: str, value: Any) -> bytes:
        """
        Encode the input value assuming a nested-encoded format.

        :param type_name: name of the type of the value to encode into
        :type type_name: str
        :param value: value to encode
        :type value: Any
        :return: encoded value
        :rtype: bytes
        """
        if type_name in basic_type.BASIC_TYPES:
            return basic_type.nested_encode_basic(type_name, value)

        list_pattern = re.match(r"^List<(.*)>$", type_name)
        if list_pattern is not None:
            if not isinstance(value, Iterable):
                raise TypeError("Value to encode must be an iterable for List type")
            inner_type_name = list_pattern.groups()[0]
            list_size = len(value)
            encoded_list_size = basic_type.nested_encode_basic("u32", list_size)
            encoded_value = self.top_encode_iterable(
                list_size * [inner_type_name], value
            )
            return encoded_list_size + encoded_value

        array_pattern = re.match(r"^array(\d+)<(.*)>$", type_name)
        if array_pattern is not None:
            if not isinstance(value, Iterable):
                raise TypeError("Value to encode must be an iterable for array type")
            array_size = int(array_pattern.groups()[0])
            inner_type_name = array_pattern.groups()[1]
            return self.top_encode_iterable(array_size * [inner_type_name], value)

        tuple_pattern = re.match(r"^tuple<(.*)>$", type_name)
        if tuple_pattern is not None:
            if not isinstance(value, Iterable):
                raise TypeError("Value to encode must be an iterable for tuple type")
            inner_types = tuple_pattern.groups()[0].replace(" ", "").split(",")
            return self.top_encode_iterable(inner_types, value)

        option_pattern = re.match(r"^Option<(.*)>$", type_name)
        if option_pattern is not None:
            if value is None:
                return basic_type.nested_encode_basic("bool", False)
            option_encoding = basic_type.nested_encode_basic("bool", True)
            inner_type_name = option_pattern.groups()[0]
            return option_encoding + self.nested_encode(inner_type_name, value)

        if type_name in self.structs:
            return self.encode_custom_struct(type_name, value)
        if type_name in self.enums:
            return self.encode_custom_enum(type_name, value)

        raise errors.UnknownType(type_name)

    def top_decode(self, type_name: str, data: Union[List[bytes], bytes]) -> Any:
        """
        Decodes a part of the input data assuming a top-encoded
        format

        :param type_name: name of the type of the value to extract from the data
        :type type_name: str
        :param data: data containing the value to extract
        :type data: bytes
        :return: decoded value
        :rtype: Any
        """
        if isinstance(data, List):
            variadic_multi_pattern = re.match(r"^variadic<multi<(.*)>>$", type_name)
            if variadic_multi_pattern is not None:
                inner_types = (
                    variadic_multi_pattern.groups()[0].replace(" ", "").split(",")
                )
                if len(data) % len(inner_types) != 0:
                    raise errors.MultiElementsNumberMismatch(data, inner_types)
                results = []
                while len(data) > 0:
                    sub_results = []
                    for inner_type in inner_types:
                        sub_results.append(self.top_decode(inner_type, data.pop(0)))
                    results.append(sub_results)
                return results

            variadic_pattern = re.match(r"^variadic<(.*)>$", type_name)
            if variadic_pattern is not None:
                inner_type = variadic_pattern.groups()[0]
                return [self.top_decode(inner_type, sd) for sd in data]

            # at this point, the data should not be a list of bytes
            if len(data) == 0:
                data = None
            elif len(data) == 1:
                data = data[0]
            else:
                raise TypeError(f"Data should not be a list for type {type_name}")

        if type_name in basic_type.BASIC_TYPES:
            return basic_type.top_decode_basic(type_name, data)

        optional_pattern = re.match(r"^optional<(.*)>$", type_name)
        if optional_pattern is not None:
            if data is None or len(data) == 0:
                return None
            inner_type_name = optional_pattern.groups()[0]
            return self.top_decode(inner_type_name, data)

        list_pattern = re.match(r"^List<(.*)>$", type_name)
        if list_pattern is not None:
            inner_type_name = list_pattern.groups()[0]
            return self.top_decode_iterable(inner_type_name, data)

        if type_name.startswith("Option") and len(data) == 0:
            return None

        # for other cases, we can directly use the nested_decode function
        result, data = self.nested_decode(type_name, data)
        if len(data) != 0:
            raise errors.LeftOverData(data)
        return result

    def top_encode(self, type_name: str, value: Any) -> Union[bytes, List[bytes], None]:
        """
        Encode the input data assuming a top-encoded format

        :param type_name: name of the type of the value to encode into
        :type type_name: str
        :param value: value to encode
        :type value: Any
        :return: encoded value (None if no encoding, for optional value for example)
        :rtype: Union[bytes, List[bytes], None]
        """
        variadic_multi_pattern = re.match(r"^variadic<multi<(.*)>>$", type_name)
        if variadic_multi_pattern is not None:
            if not isinstance(value, Iterable):
                raise TypeError("Value to encode must be an iterable for variadic type")
            inner_types = variadic_multi_pattern.groups()[0].replace(" ", "").split(",")
            encoded_value = []
            for multi in value:
                if not isinstance(multi, Iterable):
                    raise TypeError(
                        "Value to encode must be an iterable for multi type"
                    )
                if len(multi) != len(inner_types):
                    raise errors.ElementsNumberMismatch(multi, inner_types)
                for inner_value, inner_type in zip(multi, inner_types):
                    encoded_value.append(self.top_encode(inner_type, inner_value))
            return encoded_value

        variadic_pattern = re.match(r"^variadic<(.*)>$", type_name)
        if variadic_pattern is not None:
            if not isinstance(value, Iterable):
                raise TypeError("Value to encode must be an iterable for variadic type")
            inner_type = variadic_pattern.groups()[0]
            encoded_value = []
            for inner_value in value:
                encoded_value.append(self.top_encode(inner_type, inner_value))
            return encoded_value

        list_pattern = re.match(r"^List<(.*)>$", type_name)
        if list_pattern is not None:
            if not isinstance(value, Iterable):
                raise TypeError("Value to encode must be an iterable for List type")
            inner_type_name = list_pattern.groups()[0]
            return self.top_encode_iterable(len(value) * [inner_type_name], value)

        optional_pattern = re.match(r"^optional<(.*)>$", type_name)
        if optional_pattern is not None:
            if value is None:
                return None
            if isinstance(value, (list, tuple)):
                if len(value) == 0:
                    return None
                value = value[0]
            inner_type_name = optional_pattern.groups()[0]
            return self.top_encode(inner_type_name, value)

        if type_name.startswith("Option<") and value is None:
            return bytes()

        if type_name in self.enums:
            return self.encode_custom_enum(type_name, value, True)

        if type_name in basic_type.BASIC_TYPES:
            return basic_type.top_encode_basic(type_name, value)

        # for other cases, we can directly use the nested_decode function
        return self.nested_encode(type_name, value)

    def decode_contract_query_response(
        self,
        endpoint_name: str,
        query_response: ContractQueryResponse,
    ) -> Any:
        """
        Decode the response of a contract query by relying on the ABI definition


        :param endpoint_name: name of the endpoint that was called during the query
        :type endpoint_name: str
        :param query_response: response from the contract query
        :type query_response: ContractQueryResponse
        :return: decoded results
        :rtype: Any
        """
        if query_response.return_code != "ok":
            raise ValueError(
                f"Query failed: {query_response.return_code}, "
                f"{query_response.return_message}"
            )
        try:
            endpoint = self.endpoints[endpoint_name]
        except KeyError as err:
            raise errors.UnknownEndpoint(endpoint_name) from err
        bytes_data_parts = query_response.get_return_data_parts()
        return self.decode_io(endpoint.outputs, bytes_data_parts)

    def decode_io(
        self, io_list: List[Dict], bytes_data_parts: List[bytes]
    ) -> List[Any]:
        """
        Decode a list of bytes parts based on a list of inputs or outputs types

        :param io_list: orders list of types definitions to expect
        :type io_list: List[Dict]
        :param bytes_data_parts: data to decode
        :type bytes_data_parts: List[bytes]
        :return: decoded data
        :rtype: List[Any]
        """
        decoded_results = []
        for io_element in io_list:
            io_type = io_element["type"]
            is_multiresults = (
                io_element.get("multi_result", False)
                or io_element.get("multi_arg", False)
            ) and not io_type.startswith("optional")
            if is_multiresults:
                bytes_data, bytes_data_parts = bytes_data_parts, []
            elif len(bytes_data_parts) == 0:  # option value case
                bytes_data = b""
            else:
                bytes_data = bytes_data_parts.pop(0)
            decoded_output = self.top_decode(io_type, bytes_data)
            if is_multiresults:
                if decoded_output is not None:
                    decoded_results.extend(decoded_output)
            else:
                if not io_type.startswith("optional") or decoded_output is not None:
                    decoded_results.append(decoded_output)
        if len(bytes_data_parts) > 0:
            raise errors.LeftOverData(bytes_data_parts)
        return decoded_results

    def encode_endpoint_inputs(self, endpoint_name: str, values: List) -> List[bytes]:
        """
        Encode given values into the expected types of an endpoint

        :param endpoint_name: name of the endpoint
        :type endpoint_name: str
        :param values: values to encode
        :type values: List
        :return: values encoded as inputs
        :rtype: List[bytes]
        """
        try:
            endpoint = self.endpoints[endpoint_name]
        except KeyError as err:
            raise errors.UnknownEndpoint(endpoint_name) from err
        values_copy = deepcopy(values)
        encoded_inputs = []
        for endpoint_input in endpoint.inputs:
            to_encode_type = endpoint_input["type"]
            is_multi_arg = endpoint_input.get(
                "multi_arg", False
            ) and not to_encode_type.startswith("optional")
            if is_multi_arg:
                to_encode, values_copy = values_copy, []
            else:
                try:
                    to_encode = values_copy.pop(0)
                except IndexError:
                    to_encode = None
            encoded_input = self.top_encode(to_encode_type, to_encode)
            if is_multi_arg:
                if encoded_input is not None:
                    encoded_inputs.extend(encoded_input)
            else:
                if (
                    not to_encode_type.startswith("optional")
                    or encoded_input is not None
                ):
                    encoded_inputs.append(encoded_input)
        return encoded_inputs

    def decode_endpoint_input_data(
        self, raw_input_data: str
    ) -> Tuple[str, List[Dict], List[Any]]:
        """
        Decode the input data of a transaction that calls an endpoint of
        the smart-contract

        :param raw_input_data: full input data (not b64 encoded)
        :type raw_input_data: str
        :return: endpoint name, Esdt transfers, list of decoded inputs
        :rtype: Tuple[str, List[Dict], List[Any]]
        """
        data_parts = raw_input_data.split("@")
        transfers = []
        decoded_inputs = []
        if len(data_parts) == 0:
            return transfers, decoded_inputs

        # first decode if there is any transfer
        first_function = data_parts.pop(0)  # first function is not serialized
        if first_function == "ESDTTransfer":
            transfers.append(
                {
                    "identifier": self.top_decode(
                        "TokenIdentifier", bytes.fromhex(data_parts.pop(0))
                    ),
                    "nonce": 0,
                    "amount": self.top_decode(
                        "BigUint", bytes.fromhex(data_parts.pop(0))
                    ),
                }
            )
            endpoint_name = self.top_decode(
                "utf-8 string", bytes.fromhex(data_parts.pop(0))
            )
        elif first_function == "MultiESDTNFTTransfer":
            first_part = bytes.fromhex(data_parts.pop(0))
            try:
                Address.from_hex(first_part.hex(), "erd").bech32()  # receiver
                n_transfers = self.top_decode("u32", bytes.fromhex(data_parts.pop(0)))
            except ErrBadPubkeyLength:
                n_transfers = self.top_decode("u32", first_part)

            for _ in range(n_transfers):
                transfers.append(
                    {
                        "identifier": self.top_decode(
                            "TokenIdentifier", bytes.fromhex(data_parts.pop(0))
                        ),
                        "nonce": self.top_decode(
                            "u64", bytes.fromhex(data_parts.pop(0))
                        ),
                        "amount": self.top_decode(
                            "BigUint", bytes.fromhex(data_parts.pop(0))
                        ),
                    }
                )
            endpoint_name = self.top_decode(
                "utf-8 string", bytes.fromhex(data_parts.pop(0))
            )
        else:
            endpoint_name = first_function

        # then decode the inputs
        try:
            endpoint = self.endpoints[endpoint_name]
        except KeyError as err:
            raise errors.UnknownEndpoint(endpoint_name) from err

        decoded_inputs = self.decode_io(
            endpoint.inputs, [bytes.fromhex(e) for e in data_parts]
        )
        return endpoint_name, transfers, decoded_inputs
