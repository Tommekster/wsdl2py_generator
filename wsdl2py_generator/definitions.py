from typing import List
from dataclasses import dataclass
import re


@dataclass
class FieldDef:
    name: str
    type: str
    is_optional: bool
    is_array: bool

    def __repr__(self) -> str:
        return self.code

    @property
    def code(self) -> str:
        _type = self.type
        _type = f"List[{_type}]" if self.is_array else _type
        _type = f"Optional[{_type}]" if self.is_optional else _type
        return f"{self.name}: {_type}"


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


@dataclass
class OperationDef:
    name: str
    arguments: List[FieldDef]
    return_type: str

    def __repr__(self) -> str:
        _arguments = ", ".join(repr(a) for a in self.arguments)
        return f"{self.name}({_arguments}) -> {self.return_type}"

    @property
    def safe_name(self) -> str:
        return re.sub(r"\W", "_", self.name)

    @property
    def code(self) -> str:
        _arguments = ", ".join(repr(a) for a in self.arguments)
        _arguments = ", ".join(["self", _arguments])
        _declaration = f"{self.safe_name}({_arguments}) -> {self.return_type}"
        _vars = ", ".join(a.name for a in self.arguments)
        code = f"""
def {_declaration}:
    return self._service["{self.name}"]({_vars})
"""
        return code


@dataclass
class ServiceDef:
    name: str
    binding: str
    url: str
    operations: List[OperationDef]

    def __repr__(self) -> str:
        return f"<{self.name}Service({len(self.operations)})>"

    @property
    def code(self) -> str:
        _operations = (
            ""
            .join(o.code for o in self.operations)
            .replace("\n", "\n    ")
            .replace("\n    \n", "\n\n")
        )
        code = f"""
class {self.name}Service:
    def __init__(self, client: zeep.Client, **kwargs):
        binding = kwargs.get("binding_name", "{self.binding}")
        url = kwargs.get("address", "{self.url}")
        self._service = client.create_service(binding, url)
{_operations}
"""
        return code
