"""
author: Etienne Wallet

This module contains the dataclasses describing the data elements used by the package
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AbiEndpoint:
    """
    Represents an endpoint defined in an ABI file
    """

    name: str
    mutability: str
    inputs: List[Dict]
    outputs: List[Dict]
    docs: List[str]

    @staticmethod
    def from_dict(data: Dict) -> AbiEndpoint:
        """
        Parse a dictionnary into an instance of this class

        :param data: data to parse
        :type data: Dict
        :return: instance of the class
        :rtype: AbiEndpoint
        """
        return AbiEndpoint(
            name=data["name"],
            mutability=data["mutability"],
            inputs=data["inputs"],
            outputs=data["outputs"],
            docs=data.get("docs", []),
        )


@dataclass
class AbiField:
    """
    Represents a field for a struct or a variant
    """

    name: str
    type: str
    docs: List[str]

    @staticmethod
    def from_dict(data: Dict) -> AbiField:
        """
        Parse a dictionnary into an instance of this class

        :param data: data to parse
        :type data: Dict
        :return: instance of the class
        :rtype: AbiField
        """
        return AbiField(
            name=data["name"],
            type=data["type"],
            docs=data.get("docs", []),
        )


@dataclass
class AbiStruct:
    """
    Represents an struct defined in an ABI file
    """

    name: str
    fields: List[AbiField]
    docs: List[str]

    @staticmethod
    def from_dict(data: Dict) -> AbiStruct:
        """
        Parse a dictionnary into an instance of this class

        :param data: data to parse
        :type data: Dict
        :return: instance of the class
        :rtype: AbiStruct
        """
        return AbiStruct(
            name=data["name"],
            fields=[AbiField.from_dict(f) for f in data["fields"]],
            docs=data.get("docs", []),
        )


@dataclass
class AbiVariant:
    """
    Represents a variant for an ABI enum
    """

    name: str
    discriminant: int
    fields: List[AbiField]

    @staticmethod
    def from_dict(data: Dict) -> AbiVariant:
        """
        Parse a dictionnary into an instance of this class

        :param data: data to parse
        :type data: Dict
        :return: instance of the class
        :rtype: AbiVariant
        """
        return AbiVariant(
            name=data["name"],
            discriminant=data["discriminant"],
            fields=[AbiField.from_dict(f) for f in data.get("fields", [])],
        )


@dataclass
class AbiEnum:
    """
    Represents an enum defined in an ABI file
    """

    name: str
    variants: List[AbiVariant]
    docs: List[str]

    @staticmethod
    def from_dict(data: Dict) -> AbiEnum:
        """
        Parse a dictionnary into an instance of this class

        :param data: data to parse
        :type data: Dict
        :return: instance of the class
        :rtype: AbiEnum
        """
        return AbiEnum(
            name=data["name"],
            variants=[AbiVariant.from_dict(v) for v in data["variants"]],
            docs=data.get("docs", []),
        )
