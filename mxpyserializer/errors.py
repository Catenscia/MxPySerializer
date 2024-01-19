"""
author: Etienne Wallet

This module contains the custom errors defined for this package
"""


from typing import Any, List, Optional


class MxPySerializerException(Exception):
    """
    Root class for all custom errors of this package
    """


class UnknownCustomTypeType(MxPySerializerException):
    """
    To be raised when a custom type has an unknown type
    """

    def __init__(self, custom_type: str, unknown_type: str) -> None:
        message = f"The custom type {custom_type} has an unknown type: {unknown_type}"
        super().__init__(message)


class UnknownType(MxPySerializerException):
    """
    To be raised when a type is unknown
    """

    def __init__(self, unknown_type: str) -> None:
        message = f"Unknown type: {unknown_type}"
        super().__init__(message)


class UnknownStruct(MxPySerializerException):
    """
    To be raised when a user defined Struct in not present in the ABI definition
    """

    def __init__(self, struct_name: str) -> None:
        message = f"Struct {struct_name} is not defined by the ABI file"
        super().__init__(message)


class MissingStuctField(MxPySerializerException):
    """
    To be raised when a field was not provided for a Struct definition
    """

    def __init__(self, struct_name: str, missing_field) -> None:
        message = f"Missing field {missing_field} for struct {struct_name}"
        super().__init__(message)


class UnknownEnum(MxPySerializerException):
    """
    To be raised when a user defined Enum in not present in the ABI definition
    """

    def __init__(self, enum_name: str) -> None:
        message = f"Enum {enum_name} is not defined by the ABI file"
        super().__init__(message)


class UnknownEnumDiscriminant(MxPySerializerException):
    """
    To be raised when a discriminant is not defined for an Enum
    """

    def __init__(self, enum_name: str, discriminant: int) -> None:
        message = f"Discriminant {discriminant} is not defined for Enum {enum_name}"
        super().__init__(message)


class EnumVariantNotFound(MxPySerializerException):
    """
    To be raised when a variant could not be found for an Enum
    """

    def __init__(
        self, enum_name: str, name: Optional[str], discriminant: Optional[int]
    ) -> None:
        message = (
            f"No variant found in the Enum {enum_name} with name = {name} and/or "
            f"discriminant = {discriminant}"
        )
        super().__init__(message)


class ElementsNumberMismatch(MxPySerializerException):
    """
    To be raised when the number of elements doesn't match the number of types
    """

    def __init__(self, values: List[Any], types: List[str]) -> None:
        message = (
            f"Numbers of values and associated types don't match: {len(values)} "
            f"!= {len(types)}"
        )
        super().__init__(message)


class MultiElementsNumberMismatch(MxPySerializerException):
    """
    To be raised when the number of elements doesn't match the number of types
    """

    def __init__(self, values: List[Any], types: List[str]) -> None:
        message = (
            f"The number of elements ({len(values)}) is not coherent with "
            f"the multi value size ({len(types)})"
        )
        super().__init__(message)


class LeftOverData(MxPySerializerException):
    """
    To be raised when there are still some data left after decoding
    """

    def __init__(self, data: bytes) -> None:
        message = f"Some left over bytes were not decoded: {data}"
        super().__init__(message)


class UnknownEndpoint(MxPySerializerException):
    """
    To be raised when an endpoint is unknown
    """

    def __init__(self, unknown_endpoint: str) -> None:
        message = f"Unknown endpoint: {unknown_endpoint}"
        super().__init__(message)
