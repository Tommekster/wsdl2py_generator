from typing import Iterable, List
import zeep.wsdl
import zeep.wsdl.definitions
from .type_tools import get_python_type
from .definitions import FieldDef, ServiceDef, OperationDef


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
                    type=get_python_type(
                        e.type,
                        parent_name=operation.input.body.type.name
                    ),
                    is_optional=e.is_optional,
                    is_array=e.max_occurs == "unbounded"
                )
                for name, e in (
                    operation.input.body.type.elements
                    if hasattr(operation.input.body.type, "elements")
                    else [(operation.input.body.type.name.lower(), operation.input.body)]
                )
            ],
            return_type=(
                operation.output.body.type.name
                if operation.output
                else "None"
            )
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
from typing import Union, Optional, Any, List


{definitions}
"""
    return code
