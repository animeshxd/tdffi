import json
import enum
import re
import io
from typing import Dict, Tuple


data_map = {
    'double': 'double',
    'string': 'String',
    'int32': 'int',
    'int53': 'int',
    'int64': 'String',
    'bytes': 'String', # 'Uint8List',
    'Bool': 'bool',
    "emojis": 'List<String>',
    'dynamic': 'dynamic',

    # vector {t:Type} # [ t ] = Vector t
}

td_api = "tl/td_api.tl"
exports_class = "lib/td/classes.dart"
exports_function = "lib/td/functions.dart"


TlObject = """
abstract class TlObject {
  Map<String, dynamic> toJson();
  String toJsonEncoded();
  Pointer<Utf8> toCharPtr();

}
""".strip()

function = """
abstract class Func extends TlObject {

}
""".strip()

preamble = """
// ignore_for_file: camel_case_types, non_constant_identifier_names, unnecessary_question_mark, no_leading_underscores_for_local_identifiers
import 'dart:ffi' show Pointer;
import 'dart:convert' show jsonEncode;
import 'package:ffi/ffi.dart' show StringUtf8Pointer, Utf8;
""".strip()

class Type(enum.Enum):
    TL = 2
    DART = 3
    VECTOR_TL = 4
    VECTOR_DART = 6
    
 
class _absts:
    def __init__(self) -> None:
        self.loaded = False
        try:
            _json = json.load(open('tl/members.json'))
            self.loaded = True
        except FileNotFoundError:
            _json = {}
        self.methods: Dict[str, list] = _json
    def __getitem__(self, _k):
        return self.methods.get(_k, None)
    def __setitem__(self, _k, _v) -> None:
        if self.loaded:
            return
        if _k in self.methods:
            self.methods[_k].append(_v)
        else:
            self.methods[_k] = [_v]

absts = _absts()

description = ""
param_description: Dict[str, tuple] = {}

def vector_to_List(vector):
    type_ = re.search("vector<(\w+)>", vector).group(1)
    dtype, _, istl = to_dart_type(type_)

    return f"List<{dtype}>", _, Type(istl.value * 2)

def to_dart_type(type_: str) -> Tuple[str, str, Type]:
                                #    d     t   enum
    if type_.startswith('vector'):
        return vector_to_List(type_)

    dtype = data_map.get(type_, None)
    if dtype is not None:
        return dtype, type_, Type.DART
    else:
        return type_[0].lower()+type_[1:], type_[0].lower()+type_[1:], Type.TL



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
        absts[what] = class_name
    elif isfunc:
        what = 'Func'
    else:
        what = "TlObject"
    
    if isfunc:
        sio.write(f'///Returns {secound}\n///\n')
    sio.write(f"///{tl_constructor}///\n")
    sio.write(f'class {class_name} extends {what} {{\n\n')
    args = [i.split(':') for i in _[1:]]
   
    s = '' # class memebers
    cargs = '' # constructor args
    _json = f'"@type": "{class_name}",' 
    ldargs = '  ' # toList body
    args.append(['extra', 'dynamic'])
    l = len(args)   
    for i, d in enumerate(args):
        last = "," if i != l-1  else ""
        dtype, _, istlobj = to_dart_type(d[1])
        darg = d[0].strip()
        pd_, is_null = param_description.get(darg, ("Extra param", True))
        _xdarg = darg if dtype != darg else darg+"_"
        
        if class_name == _xdarg:
            # print("same")
            _xdarg+='_'
        if not isfunc:
            if istlobj == Type.TL:
                isabst = absts[dtype]
                if isabst:
                    temp = f"switch (_map['{darg}']{'?' if is_null else ''}['@type']) {{"
                    for a in isabst:
                        temp += f"""
                        case '{a}':
                            {_xdarg} = {a}.fromMap(_map["{darg}"]);
                            break;
                        """
                    temp += f"""
                        case null:
                        default:
                            {f"{_xdarg} = null;" if is_null else ''}
                            break;
                    }}
                    """
                    
                    ldargs += temp
                else:
                    ldargs += f'{_xdarg} = {dtype}.fromMap(_map["{darg}"]);\n          '

            elif istlobj == Type.VECTOR_TL:
                isabst = absts[_]
                if isabst:
                    # print(dtype, '===')
                    temp = (f"{_xdarg} = _map['{darg}']{'?' if is_null else ''}.map((e) {{\n"
                            f"switch (e['@type']) {{"
                            
                            )
                    for a in isabst:
                        temp += f"""
                        case '{a}':
                            return {a}.fromMap(e);
                        """

                    temp += '}}).toList();'
                    ldargs += temp
                    # print('_______________')
                else:
                    # ldargs += f'{_xdarg} = (_map?["{darg}"] ?? [])?.map((e) => {_}.fromMap(e)).toList();\n          '
                    ldargs += f'{_xdarg} = {dtype}.from((_map["{darg}"] ?? []).map((e) => {_}.fromMap(e)));\n          '

            elif istlobj in (Type.VECTOR_DART, Type.DART):
                if (i == l - 1):
                    ldargs += f'{_xdarg} = _map["@extra"];\n'
                else:
                    ldargs += f'{_xdarg} = _map["{darg}"];\n          '
        
        # class member
        s   +=f"    ///{pd_}\n"
        s = s+f"    {'late ' if not is_null else ''}{dtype}{'?' if is_null else ''} {_xdarg};\n"

        # constructor args
        cargs+= f"{'required ' if not is_null else ''}this.{_xdarg}{last}"
        if (i is l - 1):
            # print(i, l)
            _json += "if(extra != null) '@extra': extra"
            # print(_json)
            continue
        _json += f'"{darg}": {_xdarg}{last}'

    
    
    sio.write(f'    {class_name}({{{cargs}}});\n\n')
    sio.write(s)
    sio.write("\n")

    methods = f"""\
    final String TYPE = "{class_name}";
    @override
    Map<String, dynamic> toJson() {{
         return {{{_json}}};
    }}
    @override
    String toJsonEncoded(){{
        return jsonEncode(toJson());
    }}
    @override
    Pointer<Utf8> toCharPtr() {{
         return jsonEncode(toJson()).toNativeUtf8();
    }}
    """
    extra_methods = f"""\
    /// Construct from `Map`
    {class_name}.fromMap(Map<String, dynamic>? _map){{
        if (_map == null) return;
        {'var _ = _map["@type"];'}
        {ldargs}
        }}
    """

    sio.write(methods)
    if not isfunc:
        sio.write(extra_methods)
        
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
                    description = ""
                    param_description.clear()
                    _io.write(i)

                if i.startswith('//'):
                    if i.startswith('//@class'):
                        # //@class AuthenticationCodeType @description Provides information about the method by which an authentication code is delivered to the user
                        _class = re.search('//@class (.+) @description (.+)', i)
                        name, desc = _class.groups()
                        class__ = name[0].lower()+name[1:]
                        if absts.loaded:
                            _io.write("///"+"".join(i + ' , ' for i in absts[class__]))
                            _io.write('\n///\n')
                        _io.write(f'///{desc}\n///\n')
                        _io.write(f'abstract class {class__} extends TlObject {{}}\n')
                    else:
                        #3(param), 4(description)
                        for i in re.finditer(r"(?=(@(param_)?(\w+)(.+?))(@|$))", i):
                            param, desc = i.group(3), i.group(4) # variable # description
                            param_ = i.group(2) # param_
                            if param == 'description' and param_ is None:
                                description = desc
                                _io.write(f'///{desc}\n///\n')
                            else:
                                param_description[param.strip()] = (desc, re.search("(?i)(may be null|If empty)", desc))
                                _io.write(f'///[{param}] -{desc}\n///\n')



# class setSerilizer(json.JSONEncoder):
#     def default(self, o: Any) -> Any:
#         if isinstance(o, set):
#             return list(o)
#         return super().default(o) cls=setSerilizer
    

if __name__ =='__main__':
    import os, json
    os.makedirs("lib/td/", exist_ok=True)
    generate()
    # print(absts.methods)
    # print(json.dumps(absts.methods, indent=4, ), file=open('tl/members.json','w'))
    os.popen(f'dart format {exports_class} {exports_function}')