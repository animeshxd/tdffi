import re
import io


data_map = {
    'double': 'double',
    'string': 'String',
    'int32': 'int',
    'int53': 'int',
    'int64': 'int',
    'bytes': 'String', # 'Uint8List',
    'Bool': 'bool',
    "vector<T>": 'List<T>',
    "emojis": 'List<String>'

    # vector {t:Type} # [ t ] = Vector t
}

td_api = "tl/td_api.tl"
exports_class = "lib/td/classes.dart"
exports_function = "lib/td/functions.dart"


TlObject = """
abstract class TlObject {
  Map<String, dynamic> toJson();
  Pointer<Utf8> toCharPtr();
}
""".strip()

function = """
abstract class Func extends TlObject {

}
""".strip()

preamble = """
// ignore_for_file: camel_case_types, non_constant_identifier_names, unnecessary_question_mark
import 'dart:ffi' show Pointer;
import 'dart:convert' show jsonEncode;
import 'package:ffi/ffi.dart' show StringUtf8Pointer, Utf8;
""".strip()


def vector_to_List(vector):
    type_ = re.search("vector<(\w+)>", vector).group(1)
    return f"List<{to_DartType(type_)}>"

def to_DartType(type_: str):
    if type_.startswith('int'):
        return "int"

    if type_.startswith('vector'):
        return vector_to_List(type_)

    return data_map.get(type_, type_[0].lower()+type_[1:])


def construct(tl_constructor: str, f, class__: str, isfunc=False):
    
    _ = tl_constructor.split("=")
    first, secound, *__ = (i.strip() for i in _)
    # print(first, secound[0].lower()+secound[1:])

    sio = io.StringIO()
    # testCallVectorIntObject x:vector<testInt> testVectorIntObject;
    _ = first.split()
    class_name = _[0].strip()
    extends = class__.strip().lower() == secound[:-1].strip().lower()
    # print([class__.lower().strip(), secound[:-1].strip().lower()], class__.strip().lower() == secound.strip().lower())
    if extends:
        # exit()
        what = class__
    elif isfunc:
        what = 'Func'
    else:
        what = "TlObject"
    if isfunc:
        sio.write(f'///Returns {secound}\n///\n')
    sio.write(f"///tl => {tl_constructor}///\n")
    sio.write(f'class {class_name} extends {what} {{\n\n')
    args = [i.split(':') for i in _[1:]]
   
    s = ''
    cargs = ''
    _json = f'"@type": "{class_name}",'
    if isfunc:
        args.append(['extra', 'dynamic'])
    l = len(args)    
    if args:
        for i, d in enumerate(args):
            last = "," if i != l-1  else ""
            _dtype = to_DartType(d[1])
            _darg = d[0].strip()
            _xdarg = _darg if _dtype != _darg else _darg+"_"
            if class_name == _xdarg:
                # print("same")
                _xdarg+='_'
            s = s+f'    {_dtype}? {_xdarg};\n'
            cargs+= f'this.{_xdarg}{last}'
            if (i is l - 1) and isfunc:
                # print(i, l)
                _json += "if(extra != null) '@extra': extra"
                # print(_json)
                continue
            _json += f'"{_darg}": {_xdarg}{last}'

        
        
        sio.write(f'    {class_name}({{{cargs}}});\n\n')
        sio.write(s)
        sio.write("\n")

    sio.write('    @override\n')
    sio.write('    Map<String, dynamic> toJson() {\n')
    sio.write(f'        return {{{_json}}};\n')
    sio.write('    }\n')
    sio.write('    @override\n')
    sio.write('    Pointer<Utf8> toCharPtr() {\n')
    sio.write(f'        return jsonEncode({{{_json}}}).toNativeUtf8();\n')
    sio.write('    }\n')
        
    sio.write('}\n')

    sio.seek(0)
    print(sio.getvalue(), file=f)
    sio.close()
    
    
def generate():
    nowFunction = False
    with open(exports_class, 'w+') as cio, open(exports_function, 'w+') as fio:
        cio.write(preamble)
        cio.write('\n\n')
        cio.write(TlObject)

        fio.write(preamble)
        fio.write("import 'classes.dart';\n\n\n")

        fio.write(function)
        


        _io = cio
        class__ = ''
        with open(td_api, ) as f:
            miss = True

            for i in f:
                if miss:
                    if i.startswith('vector'):
                        miss = False
                    continue    
                if i.startswith('---functions---'):
                    _io = fio
                    nowFunction = True
                    continue

                if not i.startswith(('//', '\n')):
                    try:
                        construct(i, _io, class__, nowFunction)
                    except Exception:
                        print(i)
                        raise

                if i.startswith('\n'):
                    _io.write(i)

                if i.startswith('//'):
                    if i.startswith('//@class'):
                        # //@class AuthenticationCodeType @description Provides information about the method by which an authentication code is delivered to the user
                        _class = re.search('//@class (.+) @description (.+)', i)
                        name, desc = _class.groups()
                        class__ = name[0].lower()+name[1:]
                        _io.write(f'///@description {desc}\n///\n')
                        _io.write(f'abstract class {class__} extends TlObject {{}}\n')
                    else:
                        _io.write(f'/{i}///\n')


if __name__ =='__main__':
    import os
    os.makedirs("lib/td/", exist_ok=True)
    generate()