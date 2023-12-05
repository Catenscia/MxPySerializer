"""
author: Etienne Wallet

This module contains the abi parser class which also have the methods to serialize
and deserialize complex types
"""
from __future__ import annotations
import json

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from multiversx_sdk_network_providers.contract_query_response import (
    ContractQueryResponse,
)

from mxpyserializer import basic_type
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

    @staticmethod
    def from_dict(data: Dict) -> AbiSerializer:
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

        structs = {}
        enums = {}
        for type_name, element in data.get("types", {}).items():
            if element["type"] == "struct":
                structs[type_name] = AbiStruct.from_dict({"name": type_name, **element})
            elif element["type"] == "enum":
                enums[type_name] = AbiEnum.from_dict({"name": type_name, **element})
            else:
                raise ValueError(
                    f"Uknown type {element['type']} for custom type {type_name}"
                )

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
        return cls.from_dict(raw_content)

    def nested_decode_iterable(
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
            raise ValueError(
                f"Struct {type_name} is not defined by the ABI file"
            ) from err

        return self.nested_decode_fields(type_definition.fields, data)

    def decode_custom_enum(
        self, type_name: str, data: bytes
    ) -> Tuple[Dict[str, Any], bytes]:
        """
        Decodes a part of the input data assuming it is a custom enum defined in the
        ABI. All childs elements of the structures are always nested encoded.
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
            raise ValueError(
                f"Struct {type_name} is not defined by the ABI file"
            ) from err

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
            raise ValueError(
                f"Discriminant {discriminant} is not defined in enum {type_name}"
            )

        if len(selected_variant.fields):
            inner_types = [f.type for f in selected_variant.fields]
            inner_values, data = self.nested_decode_iterable(inner_types, data)
        else:
            inner_values = None

        decoded_enum = {
            "name": selected_variant.name,
            "discriminant": discriminant,
            "values": inner_values,
        }
        return decoded_enum, data

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
            return self.nested_decode_iterable(list_size * [inner_type_name], data)

        array_pattern = re.match(r"^array(\d+)<(.*)>$", type_name)
        if array_pattern is not None:
            array_size = int(array_pattern.groups()[0])
            inner_type_name = array_pattern.groups()[1]
            return self.nested_decode_iterable(array_size * [inner_type_name], data)

        tuple_pattern = re.match(r"^tuple<(.*)>$", type_name)
        if tuple_pattern is not None:
            inner_types = tuple_pattern.groups()[0].replace(" ", "").split(",")
            return self.nested_decode_iterable(inner_types, data)

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

        raise ValueError(f"Unkown type {type_name}")

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
                    raise ValueError(
                        f"Number of elements ({len(data)}) is not coherent with"
                        f" the multi value size ({len(inner_types)})"
                    )
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
            if len(data) == 1:
                data = data[0]
            else:
                raise ValueError(f"Data should not be a list for type {type_name}")

        if type_name in basic_type.BASIC_TYPES:
            return basic_type.top_decode_basic(type_name, data)

        list_pattern = re.match(r"^List<(.*)>$", type_name)
        if list_pattern is not None:
            inner_type_name = list_pattern.groups()[0]
            return self.top_decode_iterable(inner_type_name, data)

        if type_name.startswith("Option") and len(data) == 0:
            return None

        # for other cases, we can directly use the nested_decode function
        result, data = self.nested_decode(type_name, data)
        if len(data) != 0:
            raise ValueError(f"Some left over bytes were not decoded: {data}")
        return result

    def decode_contract_query_response(
        self, query_response: ContractQueryResponse, endpoint_name: str
    ) -> Any:
        """
        Decode the response of a contract query by relying on the ABI definition

        :param query_response: response from the contract query
        :type query_response: ContractQueryResponse
        :param endpoint_name: name of the endpoint that was called during the query
        :type endpoint_name: str
        :return: decoded results
        :rtype: Any
        """
        try:
            endpoint = self.endpoints[endpoint_name]
        except KeyError as err:
            raise ValueError(f"Unknown endpoint {endpoint_name}") from err
        bytes_data_parts = query_response.get_return_data_parts()
        decoded_results = []
        for output in endpoint.outputs:
            is_multiresults = output.get("multi_result", False)
            if is_multiresults:
                bytes_data, bytes_data_parts = bytes_data_parts, []
            elif len(bytes_data_parts) == 0:  # optional value case
                bytes_data = b""
            else:
                bytes_data = bytes_data_parts.pop(0)
            decoded_output = self.top_decode(output["type"], bytes_data)
            if is_multiresults:
                decoded_results.extend(decoded_output)
            else:
                decoded_results.append(decoded_output)
        if len(bytes_data_parts) > 0:
            raise ValueError(f"Endpoint {endpoint_name} return more data than expected")
        return decoded_results
