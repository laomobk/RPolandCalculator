from alex import TokenStream, Token, Lex
from tokentype import *

import math
import sys

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
        'is' : 0,
        'print' : 0,
        '*' : 2,
        '/' : 2,
        '^' : 3,
        '(' : -726,
        ')' : -726,
        '<null>' : -726
    }

localv = []

SYS_EXIT = 1

if not SYS_EXIT:
    sys.exit = lambda x:0


_WELCOME_STR = '''PyCalculator v1.0a  (11 nov, 2019 release)'''

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

        elif tok.value in operations and tok.value not in ('(', ')'):
            t = operation_stack[-1].value \
                    if operation_stack else '<null>'

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

        elif tok.value == ',':
            t = output_stack.pop()
            nt = tl[i + 1] if len(tl) > i + 1 else ()

            output_stack.append(tuple((t,)) + tuple((nt,)))

            i += 1
        
        elif tok.ttype == LAP_IDENTIFIER and tok.value not in operations:
            output_stack.append(tok)

        elif tok.ttype == LAP_STRING:
            output_stack.append(tok)

        i += 1
    
    final = output_stack + operation_stack[::-1]
    final_plain = [tok.value   \
            if isinstance(tok, Token) else str([t.value for t in tok]) for tok in final]

    return RPolandExpr(final, final_plain)


def check_func(tok_value):
    return tok_value in ('cos', 'sin', 'tan', 'ln', 'lg')


def check_cmd(tok_value):
    return check_func(tok_value) or (tok_value in ('is', 'print', 'log'))


def unpack_variable(v :Variable):
    if isinstance(v, Variable):
        return unpack_variable(v.value)
    else:
        return v


def search_variable(vname :str):
    for v in localv:
        if v.name == vname:
            return v


def check_variable(v :Variable) -> Variable:
    if v.value is None:
        raise CalcException('E: variable \'%s\' is not defined.' % v.name)
    return v


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

            elif tok.ttype == LAP_IDENTIFIER and not check_cmd(tok.value):
                if search_variable(tok.value):
                    v = search_variable(tok.value)
                    stack.append(v)
                else:
                    stack.append(Variable(tok.value, None))

            elif tok.value in operations and not check_cmd(tok.value):
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

            elif check_func(tok.value):
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

            elif check_cmd(tok.value):
                if tok.value == 'is':
                    if len(pstr) - i != 1:
                        raise CalcException('E: syntax error')
                    value = stack.pop()
                    name = stack.pop()
                    
                    if not name.isconst:
                        name = name.name
                    else:
                        raise CalcException('E: Cannot define a constant')
                    
                    s = search_variable(name)
                    if s:
                        s.value = value
                    else:
                        localv.append(Variable(name, value))

                    stack.append(value)

                if tok.value == 'print':
                    l = [unpack_variable(stack.pop()) for _ in range(len(stack))][::-1]
                    print(*l)
                    stack.append(Variable('<number>', 0, True))


                if tok.value == 'log':
                    l = [unpack_variable(check_variable(stack.pop())) for _ in range(2)][::-1]
                    y = math.log(*l)

                    stack.append(Variable('<number>', float(y), True)) 
            i += 1
    except IndexError:
        raise CalcException('E:Illegal expression!')
    except (TypeError, ZeroDivisionError) as e:
        raise CalcException('E: Python: %s' % str(e))

    return stack[0].value


if __name__ == '__main__':
    import readline

    print(_WELCOME_STR)

    while True:
        text = input('> ')

        lex = Lex('.$str:%s\n' % text, True)
        ts = lex.lex()

        p = make_rpoland(ts)
        
        try:
            #print('RPOLAND= ', ' '.join(p.plain_list))
            print('<', run_rpoland(p.tok_list))
        except CalcException as e:
            print(str(e))
