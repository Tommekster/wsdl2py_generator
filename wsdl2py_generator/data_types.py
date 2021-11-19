from typing import Iterable, List
from zeep import wsdl
from .type_tools import get_python_type
from .definitions import FieldDef, TypeDef


def generate_types(doc: wsdl.Document) -> List[TypeDef]:
    types = [
        TypeDef(
            ns=t.qname.namespace,
            name=t.name,
            fields=[
                FieldDef(
                    name=name,
                    type=get_python_type(e.type)
                )
                for name, e in t.elements
            ]
        )
        for t in doc.types.types
        if hasattr(t, "elements")
    ]
    return types


def generate_code(types: Iterable[TypeDef]) -> str:
    definitions = "\n\n".join(t.code for t in types)
    code = f"""from __future__ import annotations
from dataclasses import dataclass
import datetime
from typing import Union


{definitions}
"""
    return code
