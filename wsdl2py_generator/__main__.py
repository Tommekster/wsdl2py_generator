
from wsdl2py_generator.generator import generate


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Python code generator from WSDL. \nIt's intendet to use with zeep package. ")
    parser.add_argument(
        "wsdl_path",
        type=str,
        help="path or url to WSDL file"
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="output directory for generated files"
    )
    args = parser.parse_args()

    generate(args.wsdl_path, args.output_dir)


if __name__ == "__main__":
    main()
