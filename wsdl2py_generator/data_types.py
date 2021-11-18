from typing import Iterable, List
from zeep import wsdl, xsd, exceptions as zeep_exc
from dataclasses import dataclass
import re


@dataclass
class FieldDef:
    name: str
    type: str

    def __repr__(self) -> str:
        return self.code

    @property
    def code(self) -> str:
        return f"{self.name}: {self.type}"


@dataclass
class TypeDef:
    ns: str
    name: str
    fields: List[FieldDef]

    def __repr__(self) -> str:
        _fields = ", ".join(repr(f) for f in self.fields)
        return f"<{self.name}({_fields})>"

    @property
    def code(self) -> str:
        _fields = "\n".join(" "*4 + f.code for f in self.fields)
        code = f"""@dataclass
class {self.name}:
{_fields}
"""
        return code


def generate_types(doc: wsdl.Document) -> List[TypeDef]:
    expression = re.compile(r"(?P<ns>[\w\d]+):(?P<name>\w+)\((?P<args>.*)\)")
    signatures = (t.signature(schema=doc.types) for t in doc.types.types)
    matches = (expression.match(value) for value in signatures)
    name_arguments = [m.groupdict().values() for m in matches if m is not None]

    types = []
    while len(name_arguments):
        ns, name, args = name_arguments.pop(0)
        fields, inner_types = parse_arguments(name, args, doc.types)
        types.append(TypeDef(ns=ns, name=name, fields=fields))
        name_arguments += inner_types
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


def parse_arguments(parent_name: str, args: str, types: xsd.Schema) -> List[FieldDef]:
    known_types = {}
    R = re.compile(
        r"(?P<arg>\w+): (?P<type>(?P<simple>[\w\d]+:\w+)|(?P<complex>\{(((\w+: )?[\w\d]+:\w+), )*?(((\w+: )?(\w|\d)+:\w+))\}))")
    fields = []
    complex_types = []
    for name, t, st, ct, *_ in R.findall(args):
        if t == st:
            try:
                _type = types.get_type(st, fail_silently=True)
            except zeep_exc.LookupError:
                pass
            if _type and not hasattr(_type, "elements") and len(_type.accepted_types) == 1:
                field_type = type_fullname(_type.accepted_types[0])
            elif _type and not hasattr(_type, "elements") and len(_type.accepted_types) > 1:
                names = (type_fullname(t) for t in _type.accepted_types)
                field_type = "Union[" + ", ".join(names) + "]"
            elif _type and hasattr(_type, "elements"):
                field_type = _type.name
            else:
                field_type = known_types[st] if st in known_types else st
        elif t == ct:
            field_type = f"{parent_name}_{name}"
            complex_types.append(("", field_type, ct))
        else:
            raise ValueError("More complex arguments: \n{t}")
        field = FieldDef(name=name, type=field_type)
        fields.append(field)
    return fields, complex_types


def type_fullname(klass: type):
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__  # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__
