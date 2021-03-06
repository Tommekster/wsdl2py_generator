from typing import Iterable, List, Union
from zeep import wsdl, xsd
from zeep.wsdl import definitions
from .type_tools import get_python_type
from .definitions import FieldDef, TypeDef


def generate_types(doc: wsdl.Document) -> List[TypeDef]:
    types = [
        d
        for t in doc.types.types
        if hasattr(t, "elements")
        for d in _create_type_defs(t)
    ]
    return types


def _create_type_defs(t: xsd.Type, name: str = None) -> List[TypeDef]:
    """
    Create TypeDef(s) including nested types
    """
    name = name or t.name
    definition = TypeDef(
        ns=t.qname.namespace,
        name=name,
        inherits=[
            get_python_type(b._xsd_type, parent_name=name)
            for b in t._extension_types
            if hasattr(b, "_xsd_type")
        ],
        fields=[
            FieldDef(
                name=e_name,
                type=get_python_type(
                    e.type,
                    parent_name=name,
                ),
                is_optional=e.is_optional,
                is_array=e.accepts_multiple
            )
            for _fields in (t.elements, t.attributes)
            for e_name, e in _fields
        ]
    )
    nested_types = [
        d
        for _, e in t.elements
        if hasattr(e.type, "elements") and not e.type.is_global
        for d in _create_type_defs(e.type, name=f"{name}_{e.type.name}")
    ]
    return [definition] + nested_types


def generate_code(types: Iterable[TypeDef]) -> str:
    definitions = "\n\n".join(t.code for t in types)
    code = f"""from __future__ import annotations
from dataclasses import dataclass
import datetime
from typing import Union, Optional, Any, List


{definitions}
"""
    return code
