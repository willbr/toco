import os
import sys
import argparse

from ie.src.py.parse2_syntax import is_atom, puts_expr
from ie.src.py.ie import parse_file
from rich.console import Console

console = Console(markup=False)
python_print = print
print = console.print

here = os.path.abspath(os.path.dirname(__file__))

class Rope():
    def __init__(self):
        self.lines = [[]]
        pass

    def write(self, s):
        self.lines[-1].append(s)

    def write_line(self, line=""):
        self.lines[-1].append(line)
        self.lines.append([])

    def render(self):
        return '\n'.join(''.join(line) for line in self.lines)


class CompilationUnit():
    def __init__(self, filename=None):
        self.libs = []
        self.types = {
                'char': 'short',
                'short': 'short',
                'int': 'int',
                'long': 'long',
                }
        self.structs = {}
        self.functions = {}
        self.global_vars = {}
        self.top_level = []
        self.toco_header = []
        self.keywords = []
        self.infix_symbols = """
        = := == !=
        + += - -= * *= / /=
        > >= < <=
        and or
        """.split()
        self.filenames = []
        self.lib_directories = []

        libs_dir = os.path.abspath(os.path.join(here, '../libs'))

        self.lib_directories.append(os.path.abspath(os.path.curdir))
        self.lib_directories.append(libs_dir)

        if filename:
            self.read_file(filename)


    def read_file(self, filename):
        self.filenames.append(filename)
        prog = parse_file(filename)

        for x in prog:
            head, *args = x
            if head in ['def', 'func-decl']:
                self.compile_func_decl(*args)

        for x in prog:
            # puts_expr(x)
            self.compile(x)

        if self.keywords:
            self.compile_keywords()


    def compile_keywords(self):
        escaped_keywords = ('keyword_' + x for x in self.keywords)
        body = ([kw, 'ie/newline'] for kw in escaped_keywords)
        x = ('enum', 'toco_keyword', 'ie/newline', *body)
        self.compile(x)

        x = "typedef toco_keyword enum toco_keyword".split()
        self.compile(x)


    def compile(self, x):
        head, *args = x
        if head == 'def':
            self.compile_proc(*args)
        elif head == 'func-decl':
            self.compile_func_decl(*args)
        elif head == 'include-lib':
            self.compile_lib(*args)
        elif head == 'import':
            self.compile_import(*args)
        elif head == 'struct':
            self.compile_struct(*args)
        elif head == 'globals':
            self.compile_globals(args)
        elif head == 'typedef':
            self.compile_typedef(*args)
        elif head == 'define':
            self.compile_define(*args)
        elif head == 'comment':
            self.top_level.append(compile_comment(*args))
        elif head == 'enum':
            self.top_level.append(self.compile_enum(*args))
        elif head == 'ie/newline':
            assert args == []
        else:
            print(head)
            assert False


    def compile_func_decl(self, fn_name, *spec):
        cbody = []
        params = []

        if not is_atom(fn_name):
            if fn_name[0] == 'ie/neoteric':
                assert len(fn_name) == 3
                raw_params = fn_name[2]
                fn_name    = fn_name[1]
            else:
                assert False

            if raw_params[0] == 'ie/infix':
                raw_params = split_on_commas(raw_params[1:])
                params = self.compile_params(raw_params)
            else:
                assert False

        returns, body = split_newline(spec)

        n = len(returns)
        if n == 0:
            returns = 'void'
            pass
        elif n == 1:
            returns = returns[0]
        else:
            assert False

        if body:
            if body[0][0] == 'params':
                assert params == []
                params = compile_params(body[0][1:])
                body = body[1:]

            if spec[0][0] == 'returns':
                assert returns == None
                returns = compile_returns(body[0][1:])
                body = body[1:]
            elif returns == None:
                returns = 'void'

        self.functions[fn_name] = [params, returns, body]


    def compile_lib(self, lib_name, *body):
        assert body[0] == 'ie/newline'
        body = body[1:]
        assert len(body) == 0
        self.libs.append(lib_name)
        name = lib_name.strip('"')
        clib = f"#include <{name}>"
        self.top_level.append(clib)


    def compile_import(self, lib_name, *body):
        filenames = [lib_name, lib_name + '.h.ie', lib_name + '.c.ie']
        assert body == ('ie/newline',)
        for lib_dir in self.lib_directories:
            for name in filenames:
                path = os.path.join(lib_dir, name)
                # print(path)
                if os.path.exists(path):
                    self.read_file(path)
                    return
        assert False


    def compile_proc(self, fn_name, *spec):
        if not is_atom(fn_name):
            if fn_name[0] == 'ie/neoteric':
                assert len(fn_name) == 3
                raw_params = fn_name[2]
                fn_name    = fn_name[1]
            else:
                assert False

        [params, returns, body] = self.functions[fn_name]

        cbody = [self.compile_statement(x) for x in body]

        self.functions[fn_name] = [params, returns, cbody]


    def compile_statement(self, x):
        head, *rest = x
        args, body = split_newline(rest)

        if args == []:
            pass
        elif args[0] == "=":
            args = [head, ['ie/infix', *args[1:]]]
            head = '='

        if args == []:
            pass
        elif args[0] in self.infix_symbols:
            nx = transform_infix([head] + args)
            if is_atom(nx):
                return nx
            head, *args = nx

        if head == 'while':
            return self.compile_while(args, body)
        elif head == 'var':
            return self.compile_var(args, body) + ";"
        elif head == ':=':
            return self.compile_let(args, body) + ";"
        elif head == 'if':
            return self.compile_if(args, body)
        elif head == 'comment':
            return compile_comment(*args, *body)
        elif head == 'return':
            return self.compile_return_statement(*args, *body)

        assert body == [] or body == ()
        ce = self.compile_expression([head, *args])
        return ce + ";"

    def compile_let(self, args, body):
        assert body == []
        num_args = len(args)
        assert num_args == 2

        var_name, x = args
        var_type = self.infer_type(x)
        var_val = self.compile_expression(x)

        if var_type == 'cstring':
            h = "typedef char *cstring;"
            if h not in self.toco_header:
                self.toco_header.append(h)

        if x[0] == 'ie/neoteric':
            _, cmd, arg = x
            if cmd in self.types.keys():
                if cmd == var_type:
                    var_val = self.compile_expression(arg)

        return self.compile_var_decl(var_name, var_type, var_val)


    def infer_type(self, x):
        if is_atom(x):
            first_char = x[0]
            if first_char == ':':
                return 'toco_keyword'
            elif first_char == '"':
                return 'cstring'

            try:
                n = int(x)
                return 'int'
            except ValueError:
                pass

            try:
                n = float(x)
                return 'float'
            except ValueError:
                pass

            return 'symbol'

        n = len(x)
        head, *rest = x
        if head == 'ie/neoteric':
            cmd = rest[0]
            if self.is_type(cmd):
                return cmd
            params, returns, body = self.functions[cmd]
            return returns
        else:
            assert False


    def is_type(self, type_name):
        base_type = type_name.lstrip("*")
        return base_type in self.types.keys()


    def compile_while(self, pred, body):
        cpred = self.compile_expression(transform_infix(pred))
        cbody = [self.compile_statement(s) for s in body]
        return f"while ({cpred})", cbody


    def compile_typedef(self, type_name, *body):
        type_spec, rest = split_newline(body)
        assert rest == ()
        decl = "typedef " + self.compile_var_decl(type_name, type_spec) + ";"
        self.top_level.append(decl)


    def compile_struct(self, struct_name, *body):
        assert body[0] == 'ie/newline'
        assert len(body) > 1
        struct_spec = {}
        for member_spec in body[1:]:
            member_name, member_type, nl = member_spec
            assert nl == 'ie/newline'
            struct_spec[member_name] = member_type
        self.types[struct_name] = ['struct', struct_spec]
        self.structs[struct_name] = struct_spec

        struct_decl = [f"struct {struct_name} {{"]
        for member_name, member_type in struct_spec.items():
            decl = self.compile_var_decl(member_name, member_type)
            struct_decl.append(f"    {decl};")
        struct_decl.append("};")
        self.top_level.append('\n'.join(struct_decl) + '\n')


    def compile_globals(self, body):
        assert body[0] == 'ie/newline'
        body.pop(0)
        for elem in body:
            assert len(elem) == 4
            var_name, let, x, nl = elem
            var_name = self.mangle(var_name)
            assert let == ':='
            assert nl == 'ie/newline'
            neoteric, var_type, var_initial = x
            assert neoteric == 'ie/neoteric'
            # print(var_initial)
            # print(x)
            decl = self.compile_var_decl(var_name, var_type, var_initial)
            # print(decl)
            # print()
            self.global_vars[var_name] = decl
            self.top_level.append(decl + ";")


    def compile_define(self, *args):
        first_line, body = split_newline(args)
        sep   = ""
        dbody = ""
        if body != ():
            assert False
        n = len(first_line)
        if n == 1:
            define_name = first_line[0]
        elif n == 2:
            define_name = first_line[0]
            sep = " "
            dbody = first_line[1]
        else:
            assert False
        decl = f"#define {define_name}{sep}{dbody}"
        self.top_level.append(decl)


    def compile_if(self, pred, body):
        cpred = self.compile_expression(transform_infix(pred))
        cbody = [self.compile_statement(s) for s in body]
        return f"if ({cpred})", cbody


    def compile_enum(self, *args):
        first_line, enum_body = split_newline(args)
        assert len(first_line) == 1
        name = first_line[0]
        enum = []
        for x in enum_body:
            line, body = split_newline(x)
            assert len(line) == 1
            assert body == []
            enum.append(line[0])
        s = [f"enum {name} {{"]
        s.append(',\n'.join(f"    {x}" for x in enum))
        s.append('};')
        return '\n'.join(s)


    def compile_return_statement(self, *args):
        x, body = split_newline(args)
        assert body == ()
        nx = transform_infix(x)
        cx = self.compile_expression(nx)
        c = f"return {cx};"
        return c


    def compile_print_macro(self, *args):
        assert len(args) == 1
        print_args = self.parse_format_string(args[0])
        cargs = ', '.join(self.compile_expression(s) for s in print_args)
        return f"printf({cargs})"


    def compile_println_macro(self, *args):
        assert len(args) == 1
        print_args = self.parse_format_string(args[0], True)
        cargs = ', '.join(self.compile_expression(s) for s in print_args)
        return f"printf({cargs})"


    def compile_fprint_macro(self, *args):
        file, fmt = args
        print_args = self.parse_format_string(fmt)
        print_args.insert(0, file)
        cargs = ', '.join(self.compile_expression(s) for s in print_args)
        return f"fprintf({cargs})"


    def compile_fprintln_macro(self, *args):
        file, fmt = args
        print_args = self.parse_format_string(fmt, True)
        print_args.insert(0, file)
        cargs = ', '.join(self.compile_expression(s) for s in print_args)
        return f"fprintf({cargs})"

    
    def parse_format_string(self, fmt, append_newline=False):
        assert fmt[0] == '"' and fmt[-1] == '"'
        fmt = fmt[1:-1]

        lhs, rhs = fmt.split("{",1)
        template = [lhs]
        vargs = []
        while rhs:
            try:
                lhs, rhs = rhs.split("{",1)
            except ValueError:
                lhs, rhs = rhs, ''
            a, text = lhs.split("}")
            v, fmt = a.rsplit(" ", 1)
            vargs.append(v)

            if fmt[0] == '=':
                template.append(f"{v}=")
                fmt = fmt[1:]

            template.append('%' + fmt)
            template.append(text)

        if append_newline:
            template.append('\\n')

        printf_format = '"' + ''.join(template) + '"'

        return [printf_format, *vargs]


    def compile_expression(self, x, depth=0):
        if is_atom(x):
            return self.mangle(x)

        # print(x)
        head, *rest = x

        if head == 'print':
            return self.compile_print_macro(*rest)
        elif head == 'println':
            return self.compile_println_macro(*rest)
        elif head == 'fprint':
            return self.compile_fprint_macro(*rest)
        elif head == 'fprintln':
            return self.compile_fprintln_macro(*rest)

        while head in ['ie/infix', 'ie/neoteric']:
            if head == 'ie/infix':
                if x == ['ie/infix']:
                    return ''
                # print(1,head, rest)
                nx = transform_infix(rest)
                if is_atom(nx):
                    return nx
                head, *rest = nx
                # print(2,head, rest)
                if rest == []:
                    return head
            elif head == 'ie/neoteric':
                head, *rest = rest

        args, body = split_newline(rest)
        assert body == ()
        cargs = [self.compile_expression(a, depth+1) for a in args]

        if head in self.infix_symbols:
            # print(head, cargs)
            r =  f" {head} ".join(cargs)
            if depth:
                return "(" + r + ")"
            else:
                return r
        elif self.is_type(head):
            assert len(cargs) == 1
            cast_name = self.compile_var_decl("", head)
            # return f"({cast_name})({', '.join(cargs)})"
            return f"({cast_name}){cargs[0]}"
        elif head == "inc":
            assert len(cargs) == 1
            return f"{cargs[0]} += 1"
        else:
            return f"{head}({', '.join(cargs)})"


    def compile_params(self, spec):
        if spec[0] == 'ie/newline':
            spec = spec[1:]

        params = []
        for param in spec:
            n = len(param)
            if len(param) == 3:
                assert param.pop() == 'ie/newline'

            if n == 1:
                if param[0] == 'void':
                    params.append('void')
                else:
                    print(param)
                    assert False
            else:
                var_name, var_type = param
                params.append(self.compile_var_decl(var_name, var_type))
        return params


    def compile_var_decl(self, var_name, var_type, initial_value=None):
        is_struct = var_type == 'struct'

        if is_struct:
            if is_atom(initial_value):
                assert False
            head, *rest = initial_value
            iv = transform_infix(rest)
            struct_name, *struct_values = iv
            var_type += f" {struct_name}"

        lhs = ""
        rhs = ""

        if is_atom(var_type):
            while var_type[0] == '*':
                lhs = "*" + lhs
                var_type = var_type[1:]
        else:
            var_type = ' '.join(var_type)

        decl = f"{var_type} {lhs}{var_name}{rhs}"

        if is_struct and initial_value:
            decl += " = {" + ', '.join(struct_values) + "}"
        elif initial_value:
            ce = self.compile_expression(initial_value)
            decl += f" = {ce}"

        return decl


    def mangle(self, name):
        x = name
        if x[0] == ':':
            keyword = x[1:]
            if keyword not in self.keywords:
                self.keywords.append(keyword)
            x = 'keyword_' + keyword
        return x.replace('-', '_')


    def render(self):
        lines = Rope()

        for e in self.toco_header:
            lines.write_line(e)

        for e in self.top_level:
            lines.write_line(e)

        if self.top_level:
            lines.write_line("")

        func_decls = 0
        for name, spec in self.functions.items():
            if name == 'main':
                continue
            params, returns, body = spec
            if body == ():
                continue
            print_func_decl(lines, name, params, returns, ' ', ';')
            func_decls += 1

        if func_decls:
            lines.write_line("")


        for name, spec in self.functions.items():
            params, returns, body = spec
            if body == ():
                continue
            print_func_decl(lines, name, params, returns, '\n', ' ')

            print_block(lines, body, 1)
            lines.write_line("")

        return lines.render()


    def print(self):
        print(self.render())


def compile_comment(*args):
    first_line, rest = split_newline(args)
    comment_body = [repr(first_line)]
    for line in rest:
        comment_body += repr(line)
    #todo escape */ in comment body
    comment = '/* ' + ' '.join(comment_body) + ' */'
    return comment


def compile_returns(spec):
    assert spec[1] == 'ie/newline'
    assert len(spec) == 2
    return spec[0]


def print_func_decl(lines, name, params, returns, sep, end):
    if params:
        cparams = ', '.join(params)
    else:
        cparams = 'void'
    code = f"{returns}{sep}{name}({cparams}){end}"
    *body, final = code.split('\n')

    for l in body:
        lines.write_line(l)

    lines.write(final)


def compile_var(args, body):
    assert body == []
    num_args = len(args)
    if num_args == 2:
        var_name, var_type = args
        return f"{var_type} {var_name}"
    elif num_args == 3:
        var_name, var_type, var_val = args
        return f"{var_type} {var_name} = {var_val}"
    else:
        assert False


def split_on_commas(lst):
    r = [[]]
    for e in lst:
        if e == ',':
            r.append([])
        else:
            r[-1].append(e)
    return r


def transform_infix(x):
    if ',' in x:
        sections = split_on_commas(x)
    else:
        sections = [x]

    transformed_sections = []
    for section in sections:
        n = len(section)

        if n == 0:
            transformed_sections.append(section)
            continue
        elif n == 1:
            transformed_sections.append(section[0])
            continue
        elif (n % 2) == 0:
            print(x)
            assert False

        first_arg, first_op, *rest = x
        xx = [first_op, first_arg]
        for i in range(2, len(x)):
            if i % 2:
                assert first_op == x[i]
            else:
                xx.append(x[i])
        return xx

    n = len(transformed_sections)

    if n == 0:
        assert False
    elif n == 1:
        return transformed_sections[0]
    else:
        return transformed_sections


def split_newline(x):
    try:
        pos = x.index('ie/newline')
        lhs = x[:pos]
        rhs = x[pos+1:]
    except ValueError:
        lhs = x
        rhs = ()
    finally:
        return lhs, rhs


def print_block(lines, body, depth):
    indent = "    " * depth

    lines.write_line("{")

    for s in body:
        lines.write(indent)
        if isinstance(s, str):
            lines.write_line(s)
        else:
            head, sub = s
            lines.write(head + " ")
            print_block(lines, sub, depth+1)
            lines.write_line("")

    indent = "    " * (depth-1)
    lines.write(indent + "}")


def is_string_literal(s):
    if len(s) < 2:
        return False
    return s[0] == '"' and s[-1] == '"'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile")
    parser.add_argument("file", nargs='+')
    args = parser.parse_args()

    cu = CompilationUnit()

    for file in args.file:
        cu.read_file(file)

    if args.outfile == None:
        cu.print()
    else:
        lines = cu.render()
        with open(args.outfile, 'w') as f:
            f.write(lines)
