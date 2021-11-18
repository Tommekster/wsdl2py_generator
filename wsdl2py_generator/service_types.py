from typing import Iterable, List
import zeep.wsdl
import zeep.wsdl.definitions
from dataclasses import dataclass
from wsdl2py_generator.data_types import FieldDef, get_type_name


@dataclass
class OperationDef:
    name: str
    arguments: List[FieldDef]
    return_type: str

    def __repr__(self) -> str:
        _arguments = ", ".join(repr(a) for a in self.arguments)
        return f"{self.name}({_arguments}) -> {self.return_type}"

    @property
    def code(self) -> str:
        _arguments = ", ".join(repr(a) for a in self.arguments)
        _arguments = ", ".join(["self", _arguments])
        _declaration = f"{self.name}({_arguments}) -> {self.return_type}"
        _vars = ", ".join(a.name for a in self.arguments)
        code = f"""
def {_declaration}:
    return self._service.{self.name}({_vars})
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


def generate_services(doc: zeep.wsdl.Document) -> List[ServiceDef]:
    services = [
        ServiceDef(
            name=s.name,
            binding=port.binding.name.text,
            url=port.binding_options["address"],
            operations=generate_operations(s)
        )
        for s, port in
        (
            (s, next(iter(s.ports.values())))
            for s in doc.services.values()
        )
    ]
    return services


def generate_operations(service: zeep.wsdl.definitions.Service) -> List[OperationDef]:
    operations = [
        OperationDef(
            name=operation.name,
            arguments=[
                FieldDef(
                    name=name,
                    type=get_type_name(
                        e.type.qname.text,
                        port.binding.wsdl.types
                    )
                )
                for name, e in operation.input.body.type.elements
            ],
            return_type=operation.output.body.type.name
        )
        for port in service.ports.values()
        for operation in port.binding._operations.values()
    ]
    return operations


def generate_code(services: Iterable[ServiceDef]) -> str:
    definitions = "\n\n".join(t.code for t in services)
    code = f"""import zeep
from .data_types import *
import datetime
from typing import Union


{definitions}
"""
    return code
