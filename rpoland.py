import math
import sys
import importlib
import traceback

from alex import TokenStream, Token, Lex
from tokentype import *

__author__ = 'LaomoBK'

operations = {
        '+' : 1,
        '-' : 1,
        '%' : 1,
        'sin' : 1,
        'cos' : 1,
        'tan' : 1,
        'log' : 1,
        'ln' : 1,
        'lg' : 1,
        'is' : -1,
        '.' : 0,
        'get' : 0,
        'is_const' : -1,
        'print' : -1,
        'input' : -1,
        'del' : -1,
        'array' : 0,
        'call' : -1,
        'load' : -1,
        '*' : 2,
        '/' : 2,
        '^' : 3,
        '(' : -726,
        ')' : -726,
        '{' : -726,
        '}' : -726,
        '<null>' : -726
    }


SYS_EXIT = 1

if not SYS_EXIT:
    sys.exit = lambda x:0

_VERSION = '1.3.1'
_WELCOME_STR = '''RPolandCalculator %s  (16 nov, 2019 release)''' % _VERSION

_funcs = ('cos', 'sin', 'tan', 'ln', 'lg')

_cmds = ('is', 'print', 'log', 
        'is_const', 'input', 
        'del', 'array', '.', 'get',
        'call', 'load')

_add_mon = (
        'array', 'print', 'call'
        )

class CalcException(Exception):
    pass

class RPolandExpr:
    def __init__(self, tok_list :list, plain_list :list):
        self.tok_list = tok_list
        self.plain_list = plain_list


class Variable:
    def __init__(self, name :str, value, isconst=False):
        self.name = name
        self.value = value
        self.isconst = isconst


    def __str__(self):
        return '<variable \'%s\' value= %s >' % (self.name, self.value)

    __repr__ = __str__


class Module:
    def __init__(self, name :str, value):
        self.__module = value
        self.value = value
        self.name = name

    def get_member(self, name :str) -> Variable:
        if not hasattr(self.__module, name):
            raise CalcException('E: attribute error : <module \'%s\'> -> \'%s\'' % (self.__module.__name__, name))
        v = getattr(self.__module, name)
        return Variable('<member>', v, True)

    def __str__(self):
        return '<module \'%s\' value= %s >' % (self.name, self.value)

    __repr__ = __str__

    def __getattr__(self, name :str):
        if not hasattr(self.__module, name):
            return None
        return getattr(self.__module, name)


class PyFunction:
    def __init__(self, name :str, argc :int, pyfunc):
        self.__func = pyfunc
        #self.__cobj = pyfunc.__code__
        
        self.value = pyfunc
        self.name = name
        self.argc = argc

    def __str__(self):
        return '<pyFunction \'%s\' value= %s >' % (self.name, self.value)

    __repr__ = __str__

    def call(self, *argv) -> Variable:
        rtn = self.__func(*argv)
        return Variable('<return value>', rtn, True)

    __call__ = call


def import_module(mname) -> Module:
    try:
        m = importlib.import_module('extra.%s' % mname)
    except ImportError:
        try:
            m = importlib.import_module('%s' % mname)
        except ImportError:
            raise CalcException('E: no module named : \'%s\'' % mname)
            return Module('<null>', None)

    return Module('<module %s>' % mname, m)


localv = [
         Variable('e', math.e, True),
         Variable('__version__', _VERSION, True),
         Variable('pi', math.pi, True),
         Variable('π', math.pi, True),
         Variable('$', '<END>', True),

         Variable('Array', import_module('array'), True),
         Variable('Math', import_module('math'), True),
         Variable('Builtins', import_module('builtins'), True),

         Variable('fuck', 'Watch it!')
        ]


def make_rpoland(stream :TokenStream) -> RPolandExpr:
    tl = stream.token_list

    output_stack = []
    operation_stack = []
    
    i = 0
    while i < len(tl):
        tok = tl[i]

        if tok.ttype == LAP_NUMBER:
            output_stack.append(tok)

        elif tok.value == '(':
            operation_stack.append(tok)

        elif tok.value in operations and tok.value not in ('(', ')', '{', '}'):
            if (tok.value in _add_mon) and tok.ttype == LAP_IDENTIFIER:
                output_stack.append(Token('$', LAP_IDENTIFIER, -1))

            t = operation_stack[-1].value \
                    if operation_stack else '<null>'

            if tok.value == '.':
                tok.ttype = LAP_IDENTIFIER

            while operations[t] > operations[tok.value]:
                pt = operation_stack.pop()
                output_stack.append(pt)
                
                if len(operation_stack) == 0:
                    break

                t = operation_stack[-1]
            operation_stack.append(tok)

        elif tok.value == ')':
            while operation_stack[-1].value != '(':
                output_stack.append(
                    operation_stack.pop())
            operation_stack.pop()  # pop '('

        elif tok.value == '<BUILD_TUPLE>':
            t = output_stack.pop()
            nt = tl[i + 1] if len(tl) > i + 1 else ()

            output_stack.append(tuple((t,)) + tuple((nt,)))

            i += 1
        
        elif tok.ttype == LAP_IDENTIFIER and tok.value not in operations:
            output_stack.append(tok)

        elif tok.ttype == LAP_STRING:
            output_stack.append(tok)

        elif tok.value in ('$'):
            tok.ttype = LAP_IDENTIFIER
            output_stack.append(tok)

        i += 1
    
    final = output_stack + operation_stack[::-1]
    final_plain = [tok.value   \
            if isinstance(tok, Token) else str([t.value for t in tok]) for tok in final]

    return RPolandExpr(final, final_plain)


def check_func(tok :Token):
    return tok.value in _funcs and tok.ttype == LAP_IDENTIFIER


def check_cmd(tok :Token):
    return check_func(tok) or (tok.value in _cmds and tok.ttype == LAP_IDENTIFIER)


def unpack_variable(v :Variable):
    if isinstance(v, Variable):
        return unpack_variable(v.value)
    else:
        return v


def search_variable(vname :str) -> Variable:
    for v in localv:
        if v.name == vname:
            return v


def check_variable(v :Variable) -> Variable:
    if v.value is None:
        raise CalcException('E: variable \'%s\' is not defined.' % v.name)
    return v


def store_var(stack :list, isconst=False):
    global localv

    value = stack.pop()
    name = stack.pop()
    
    if (not name.isconst) or name.isconst and isconst:
        name = name.name
    else:
        raise CalcException('E: Cannot define a constant')

    s = search_variable(name)
    if s:
        if isconst and not s.isconst:
            raise CalcException('E: Cannot make a variable constant')
        s.value = value
    else:
        localv.append(Variable(name, value, isconst))
    
    stack.append(value)


def just_store_var(name :str, value :Variable):
    global localv

    s = search_variable(name)
    if s:
        s.value = value
    else:
        localv.append(Variable(name, value))


def run_rpoland(pstr :list):
    if not pstr:    return

    stack = []

    global localv
   
    try:
        i = 0
        while i < len(pstr):
            tok = pstr[i]
            if tok.ttype == LAP_NUMBER:
                stack.append(Variable('<number>', float(tok.value), True))

            elif tok.ttype == LAP_STRING:
                stack.append(Variable('<string>', tok.value, True))

            elif tok.ttype == LAP_IDENTIFIER and not check_cmd(tok):
                if search_variable(tok.value):
                    v = search_variable(tok.value)
                    stack.append(v)
                else:
                    stack.append(Variable(tok.value, None))

            elif tok.value in operations and not check_cmd(tok):
                b = unpack_variable(check_variable(stack.pop()))
                a = unpack_variable(check_variable(stack.pop()))
                res = {
                    '+' : lambda b, a : a + b,
                    '-' : lambda b, a : a - b,
                    '*' : lambda b, a : a * b,
                    '/' : lambda b, a : a / b,
                    '^' : lambda b, a : a ** b,
                    '%' : lambda b, a : a % b,
                    }.get(tok.value)(b, a)

                stack.append(Variable('<number>', res, True))

            elif check_func(tok):
                x = unpack_variable(check_variable(stack.pop()))
                res = {
                       'cos' : lambda x : math.cos(x),
                       'sin' : lambda x : math.sin(x),
                       'tan' : lambda x : math.tan(x),
                       #'log' : lambda x : math.log(x),
                       'ln'  : lambda x : math.log(x, math.e),
                       'lg'  : lambda x : math.log10(x)
                      }.get(tok.value)(x)

                stack.append(Variable('<number>', res, True))

            elif check_cmd(tok):
                if tok.value == 'is':
                    store_var(stack)

                elif tok.value == 'print':
                    l = []
                    while stack:
                        p = stack.pop()
                        if p.name == '$':
                            break
                        l.append(unpack_variable(check_variable(p)))
                    l = l[::-1]
                    print(*l)
                    stack.append(Variable('<number>', 0, True))

                elif tok.value == 'log':
                    l = [unpack_variable(check_variable(stack.pop())) for _ in range(2)][::-1]
                    y = math.log(*l)

                    stack.append(Variable('<number>', float(y), True))

                elif tok.value == 'is_const':
                    store_var(stack, True)

                elif tok.value == 'input':
                    msg = stack.pop()

                    v = input(unpack_variable(check_variable(msg)))
                    
                    try:
                        v = float(v)  # if it can.
                    except:
                        pass

                    v = Variable('<input>', v, True)

                    #stack.append(Variable('<number>', 0, True))
                    stack.append(v)

                elif tok.value == 'del':
                    v = stack.pop()
                    
                    if v.isconst:
                        raise CalcException('E: Cannot delete a const!')

                    check_variable(v)
                    
                    vv = v.value
                    localv.remove(v)

                    stack.append(vv)

                elif tok.value == 'array':
                    l = []
                    while stack:
                        p = stack.pop()
                        if p.name == '$':
                            break
                        l.append(p)
                    stack.append(Variable('<array>', l[::-1], True))
                
                elif tok.value in ('.', 'get'):
                    a = stack.pop()
                    s = stack.pop()

                    ins = unpack_variable(check_variable(s))
                    if tok.value == 'get':
                        targ = unpack_variable(check_variable(a))
                    else:
                        targ = a.name

                    if not ins:
                        raise CalcException('E: attribute error: \'%s\'' % str(targ))
                    if isinstance(ins, Module):
                        v = ins.get_member(targ)
                    else:
                        if hasattr(ins, targ):
                            v = getattr(ins, targ)
                        else:
                            raise CalcException('E: attribute error : \'%s\' -> \'%s\'' % (ins, targ))

                    stack.append(Variable('<attribute>', v, True))

                elif tok.value == 'call':
                    al = []
                    while stack:
                        p = stack.pop()
                        if p.name == '$':
                            break
                        al.append(
                                unpack_variable(check_variable(p)))
                    f = al.pop()
                    al = al[::-1]
                    #f = unpack_variable(check_variable(of))
                    
                    if hasattr(f, 'argc'):  # if it has, check it.
                        if f.argc != len(al):
                            raise CalcException('E: it needs %s argument(s)!' % f.argc)

                    if not hasattr(f, '__call__'):
                        raise CalcException('E: %s is not callable' % f.name)
                    
                    try:
                        rtn = f.__call__(*al)
                    except Exception as e:
                        ts = ' '.join(traceback.format_exception_only(Exception, e))
                        raise CalcException('E :PyFunc: %s' % ts)

                    if not isinstance(rtn, Variable):
                        rtn = Variable('<return value>', rtn, True)

                    stack.append(rtn)

                elif tok.value == 'load':
                    name = unpack_variable(check_variable(stack.pop()))
                    mod = import_module(name)

                    stack.append(Variable('<module>', mod, True))


            i += 1
    except IndexError:
        raise CalcException('E:Illegal expression!')
    except (TypeError, ZeroDivisionError) as e:
        raise CalcException('E: Python: %s' % str(e))

    return stack[0].value


def run_as_interactive():
    import os
    import base64 as b64

    if os.name != 'nt':
        import readline

    print(_WELCOME_STR, '\n')

    err_count = 0
    
    try:
        while True:
            text = input('> ')

            lex = Lex('.$str:%s\n' % text, True)
            ts = lex.lex()

            p = make_rpoland(ts)
            
            try:
                #print('RPOLAND= ', ' '.join(p.plain_list))
                rtn = run_rpoland(p.tok_list)
                print('<', rtn if rtn else 'undefined')
            except CalcException as e:
                print(str(e))
                err_count += 1

                if err_count >= 250:
                    print(
                        b64.b64decode(b'Q2FuJ3QgeW91IGZ1Y2tpbmcgdXNlIGEgY2FsY3VsYXRvcj8=').decode())
                    err_count = 0
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == '__main__':
    run_as_interactive()    
