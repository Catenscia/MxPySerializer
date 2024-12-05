"""
author: Etienne Wallet

This module contains types that are not basic while being predifined
(so not written by default in the ABI)
"""

from decimal import ROUND_DOWN, Decimal
import decimal
from typing import Any, Dict, Optional
from mxpyserializer.data_models import AbiField, AbiStruct

decimal.getcontext().prec = 100  # some tokens have realy high supply and precision

MANAGED_DECIMAL_STRUCT = AbiStruct(
    "ManagedDecimal",
    [
        AbiField("data", "BigUint", ["value * scaling_factor"]),
        AbiField("decimals", "usize", ["number_of_decimals (precision)"]),
    ],
    ["Structure representing decimals with managed precision"],
)


def decimal_struct_to_decimal_str(decimal_struct: Dict) -> str:
    """
    Convert a decimal represented as a structure to a decimal string

    :param decimal_struct: decimal as a struct
    :type decimal_struct: Dict
    :return: decimal as a string
    :rtype: str
    """
    decimal_value = (
        Decimal(decimal_struct["data"]) / Decimal(10) ** decimal_struct["decimals"]
    )
    quantiziser = Decimal("1." + "0" * decimal_struct["decimals"])
    quantize_decimal_value = decimal_value.quantize(quantiziser, rounding=ROUND_DOWN)
    return str(quantize_decimal_value)


def decimal_arg_to_decimal_struct(arg: Any, decimals: Optional[int] = None) -> Dict:
    """
    Parse a user input into the structure defining a managed decimal.
    If the decimals are not specified, it will be deduced from the number
    of decimals of the provided argument

    :param arg: argument describing the managed decimal to convert
    :type arg: Any
    :param decimals: number of decimals for the provided argument, defaults to None
    :type decimals: Optional[int], optional
    :return: argument parsed into a managed decimals struct
    :rtype: Dict
    """
    if isinstance(arg, (str, int, float, Decimal)):
        decimal_value = Decimal(arg)
        if decimals is None:
            decimals = max(0, -decimal_value.as_tuple().exponent)
        data = int(decimal_value * Decimal(10) ** decimals)
        return {"data": data, "decimals": decimals}
    if isinstance(arg, Dict):
        return arg
    raise TypeError(f"Could not convert {type(arg)} ({arg}) into a decimal struct")
