import os
import zeep
from . import data_types, service_types


def generate(wsdl_path: str, output_dir: str) -> None:
    client = zeep.Client(wsdl_path)
    _ensure_output_dir(output_dir)
    _create_package_init_file(output_dir)
    _generate_types(client, output_dir)
    _generate_services(client, output_dir)


def _ensure_output_dir(output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def _create_package_init_file(output_dir: str) -> None:
    with open(os.path.join(output_dir, "__init__.py"), "w"):
        pass


def _generate_types(client: zeep.Client, output_dir: str) -> None:
    types = data_types.generate_types(client.wsdl)
    code = data_types.generate_code(types)
    with open(os.path.join(output_dir, "data_types.py"), "w") as f:
        f.write(code)


def _generate_services(client: zeep.Client, output_dir: str) -> None:
    services = service_types.generate_services(client.wsdl)
    code = service_types.generate_code(services)
    with open(os.path.join(output_dir, "services.py"), "w") as f:
        f.write(code)
