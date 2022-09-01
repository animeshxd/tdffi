

import enum
import json
import os
import re
from typing import IO, Dict, Tuple, Any


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

dtypes = {
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

data = {
    'class': {
        'isabstract': False,
        'isfunction': False,
        'name': 'class',
        'childrens': [],
        'params': [
            ('type', 'var', 'description', 'nullable')
        ],
    }
}

    

class _absts:
    def __init__(self) -> None:
        self.loaded = False
        try:
            _json = json.load(open('tl/members.json'))
            self.loaded = True
        except FileNotFoundError:
            _json = {}
        self.abstracts: Dict[str, list] = _json
    def __getitem__(self, _k):
        return self.abstracts.get(_k, [])
    def __setitem__(self, _k, _v) -> None:
        if self.loaded:
            return
        if _k in self.abstracts:
            self.abstracts[_k].append(_v)
        else:
            self.abstracts[_k] = [_v]


def dump():
    with open(td_api, 'w') as f:
        json.dump(data, f)

def camelCase(x: str):
    return x[0].lower()+x[1:]

class Type(enum.Enum):
    TL = 2
    DART = 3
    VECTOR_TL = 4
    VECTOR_DART = 6
    
def vector_to_List(vector):
    type_ = re.search("vector<(\w+)>", vector).group(1)
    dtype, _, istl = to_dart_type(type_)

    return f"List<{dtype}>", _, Type(istl.value * 2)

def to_dart_type(type_: str) -> Tuple[str, str, Type]:
                                #    d     t   enum
    if type_.startswith('vector'):
        return vector_to_List(type_)

    dtype = dtypes.get(type_, None)
    if dtype is not None:
        return dtype, type_, Type.DART
    else:
        _ = camelCase(type_)
        return _, _, Type.TL


class Serilizer(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, set):
            return list(o)
        if isinstance(o, Type):
            return o.value
        return super().default(o)
    

class Generator:
    td_api = "tl/td_api.tl"
    member_f = 'tl/members.json'
    data_f = 'tl/schema.json'


    dtypes = {
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
    absts = _absts()

    # flags
    preloaded = False
    miss = True
    isfunction = False
    isabstract = False
    haveabstract = False



    # temp
    param_description = {
        #param: description, isnull
    }
    description = ''
    eqclass = ''
    abstract_class = ''

    #store
    classes = {}

    def reset(self):
        self.isfunction = False
        self.isabstract = False
        self.haveabstract = False
        

    def load(self, override):
                # load exixting
        try:
            self.classes = json.load(open(self.data_f))
            loaded = True
        except FileNotFoundError:
            loaded = False

        
        self.preloaded = loaded and self.absts.loaded
        if self.preloaded:
            return


        with open(td_api, ) as f:
            for i in f:
                if self.miss:
                    if i.startswith('vector'):
                        self.miss = False
                    continue    
                if i.startswith('---functions---'):
                    self.isfunction = True
                    continue

                if not i.startswith(('//', '\n')):
                    self.isabstract = False
                    try:
                        self.simplify(i)
                    except Exception:
                        print(i)
                        raise
                    self.param_description.clear()

                if i.startswith('\n'):
                    self.description = ""
                    self.param_description.clear()

                if i.startswith('//'):
                    if i.startswith('//@class'):
                        # //@class AuthenticationCodeType @description Provides information about the method by which an authentication code is delivered to the user
                        match = re.search('//@class (.+) @description (.+)', i)
                        name, desc = match.groups()
                        _class = camelCase(name)
                        self.abstract_class = _class
                        self.isabstract = True
                        self.description = desc
                        self.classes[_class] = {
                            'tl': '',
                            'secound': '', 
                            'description': desc.strip(),
                            'isabstract': True,
                            'isfunction': False,
                            'haveabstract': False,
                            'extends': 'TlObject',
                            'params': []
                        }
                    else:
                        #3(param), 4(description)
                        for i in re.finditer(r"(?=(@(param_)?(\w+)(.+?))(@|$))", i):
                            param, desc = i.group(3), i.group(4) # variable # description
                            param_ = i.group(2) # param_
                            if param == 'description' and param_ is None:
                                self.description = desc
                                # _io.write(f'///{desc}\n///\n')
                            else:
                                self.param_description[param] = (desc.strip(), bool(re.search("(?i)(may be null|If empty|pass null)", desc)))

        self.reset()

    def write(self):
        _io: IO

        with open(exports_class, 'w+') as cio, open(exports_function, 'w+') as fio:
            cio.write(preamble)
            cio.write('\n\n')
            cio.write(TlObject)

            fio.write(preamble)
            fio.write("import 'classes.dart';\n\n\n")

            fio.write(function)

            _io = cio

            """
            'tl': tl_constructor,
            'secound': secound, 
            'description': self.description.strip(),
            'isabstract': self.isabstract,
            'isfunction': self.isfunction,
            'haveabstract': self.haveabstract,
            'extends': extends,
            'params': params
            """

            for _cls, _v in self.classes.items():
               
                isfunction = _v['isfunction']
                isabstract = _v['isabstract']
                haveabstract = _v['haveabstract']

                tl = _v['tl']
                secound = _v['secound']
                description = _v['description']
                params: list = _v['params']
                extends = _v['extends']

                if isfunction:
                    _io = fio
                    # exit()
                    _io.write(f'\n///Returns {secound}\n///')

                _io.write(f'\n\n/// {description} \n///')
                _io.write(f"\n/// {tl} ///")

                if isabstract:
                    _io.write("\n///"+"".join(f'`{i}` , ' for i in self.absts[_cls]))
                    _io.write(f'\nabstract class {_cls} extends TlObject {{}}\n')
                    continue

                params.append([
                    "extra",
                    [
                        "dynamic",
                        "dynamic",
                        3
                    ],
                    "extra param",
                    True
                    ]
                )
                s = '' # class memebers
                cargs = '' # constructor args
                _json = f'"@type": "{_cls}",' 
                ldargs = '  ' # toList body


                l = len(params) 
                for i, d in enumerate(params):
                    _var, _type, desc, isnull = d[0], d[1], d[2], d[3]
                    dtype, _, type = _type[0], _type[1], Type(_type[2])
                    #dart, tl,     enum

                    end = "," if i != l-1  else ""
                    var = _var + ('' if dtype != _var else '_')
                    var = var + ( '_' if _cls == var else '')


                    _io.write(f'\n///[{var}] - {desc}\n///')

                    if not isfunction:
                        if type == Type.TL:
                            clss = self.absts[dtype]
                            if clss:
                                temp = f"switch (_map['{_var}']{'?' if isnull else ''}['@type']) {{"
                                for a in clss:
                                    temp += f"""
                                    case '{a}':
                                        {var} = {a}.fromMap(_map["{_var}"]);
                                        break;
                                    """
                                temp += f"""
                                    case null:
                                    default:
                                        {f"{var} = null;" if isnull else ''}
                                        break;
                                }}
                                """
                                ldargs += temp
                            else:
                                ldargs += f'{var} = {dtype}.fromMap(_map["{_var}"]);\n          '

                        elif type == Type.VECTOR_TL:
                            clss = self.absts[_]
                            if clss:
                                temp = (f"{var} = _map['{_var}']{'?' if isnull else ''}.map((e) {{\n"
                                        f"switch (e['@type']) {{" 
                                        )
                                for a in clss:
                                    temp += f"""
                                    case '{a}':
                                        return {a}.fromMap(e);
                                    """

                                temp += '}}).toList();'
                                ldargs += temp
                                # print('_______________')
                            else:
                                # ldargs += f'{_xdarg} = (_map?["{darg}"] ?? [])?.map((e) => {_}.fromMap(e)).toList();\n          '
                                ldargs += f'{var} = {dtype}.from((_map["{_var}"] ?? []).map((e) => {_}.fromMap(e)));\n'

                        elif type in (Type.VECTOR_DART, Type.DART):
                            if (i == l - 1):
                                ldargs += f'{var} = _map["@extra"];\n'
                            else:
                                ldargs += f'{var} = _map["{_var}"];\n'
                    # class member
                    s+=f"    ///{desc}\n"
                    s = s+f"    {'late ' if not isnull else ''}{dtype}{'?' if isnull else ''} {var};\n"

                    # constructor args
                    cargs+= f"{'required ' if not isnull else ''}this.{var}{end}"
                    if (i is l - 1):
                        # print(i, l)
                        _json += "if(extra != null) '@extra': extra"
                        # print(_json)
                        continue
                    _json += f'"{_var}": {var}{end}'

                _io.write(f'\nclass {_cls} extends {extends} {{\n\n')
                _io.write(f'    {_cls}({{{cargs}}});\n\n')
                _io.write(s)
                _io.write("\n")

                methods = f"""\
                final String TYPE = "{_cls}";
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
                {_cls}.fromMap(Map<String, dynamic>? _map){{
                    if (_map == null) return;
                    {'var _ = _map["@type"];'}
                    {ldargs}
                    }}
                """

                _io.write(methods)
                if not isfunction:
                    _io.write(extra_methods)
                    
                _io.write('}\n')
              
    def generate(self, override = False):
        self.load(override)
        
        self.write()

        if not self.preloaded:
            json.dump(self.absts.abstracts, fp=open( self.member_f , 'w'), indent=4)
            json.dump(self.classes, fp=open(self.data_f, 'w'), cls=Serilizer, indent=4)


    def simplify(self, tl_constructor):
        _ = tl_constructor.split("=")
        first, secound, *__ = (i.strip() for i in _)
        secound = camelCase(secound[:-1])
        segments = first.split()
        _class = segments[0]
        args = [i.split(':') for i in segments[1:]]

        print("=============================================")
        print("tl: ", tl_constructor.strip())
        print('name: ',_class)
        print('secound: ',secound)
        print('description: ',self.description)
        print('args: ', args)

        self.haveabstract = self.abstract_class == secound
        if self.haveabstract:
            self.absts[self.abstract_class] = _class

        params = list(map(lambda e: (e[0][0], to_dart_type(e[0][1]), *e[1]) , zip(args, self.param_description.values())))
        for i in params:
            print(i)
        print(json.dumps(params, cls=Serilizer))
        print(self.param_description)
        print("is abstract: ", self.isabstract)
        print("have abstract: ", self.haveabstract)
        print("=============================================")

        extends = 'TlObject'
        if self.haveabstract:
            extends = secound 
        elif self.isfunction:
            extends = 'Func'
    
        self.classes[_class] = {
            'tl': tl_constructor,
            'secound': secound, 
            'description': self.description.strip(),
            'isabstract': self.isabstract,
            'isfunction': self.isfunction,
            'haveabstract': self.haveabstract,
            'extends': extends,
            'params': params
        }


        # exit()

if __name__ == '__main__':
    x = Generator()
    x.generate()
    os.popen(f'dart format {exports_class} {exports_function}')

    # print(x.absts.methods)
    # print(x.classes)