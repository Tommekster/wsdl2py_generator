from zeep import xsd


def get_python_type(_type: xsd.Type) -> str:
    if hasattr(_type, "elements"):
        if _type.is_global:
            return _type.name
    else:
        if len(_type.accepted_types) == 1:
            return type_fullname(_type.accepted_types[0])
        elif len(_type.accepted_types) > 1:
            names = (type_fullname(t) for t in _type.accepted_types)
            return "Union[" + ", ".join(names) + "]"
    raise NotImplementedError("This is very complex type!")


def type_fullname(klass: type):
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__  # avoid outputs like 'builtins.str'
    return module + '.' + klass.__qualname__
