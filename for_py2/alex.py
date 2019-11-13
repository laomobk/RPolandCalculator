# -*- encoding: UTF-8 -*-

#用于ail的词法分析器
 
__author__ = 'LaomoBK'
 
ALEX_VERSION_NUM = (0, 1)   
ALEX_VERSION_EXTRA = 'Beta' 
ALEX_VERSION_DATE = (10, 27, 2019)
 
from tokentype import *
from error import error_msg
 
def skip_comment_line(source, cursor):
    cur = 0  
    ccur = cursor  
    while ccur < len(source):
        if source[ccur] == '\n':
            break
        cur += 1
        ccur += 1
    
    return cur + 1  
 
def skip_comment_block(source, cursor):
    ccur = cursor
    cur = 0  
    lni = 0  
 
    try:
        while True:
            if source[ccur] == '\n':
                lni += 1
            
            if source[ccur] == '*' and source[ccur + 1] =='/':
                cur += 2 
 
                return (cur, lni)  
            ccur += 1
            cur += 1
    
    except IndexError:
        return (-1, 0)
 
def get_identifier(source, cursor):
    buffer = ''   
    ccur = cursor  
    cur = 0
 
    while ccur < len(source):
 
        if not (source[ccur].isalnum() or  \
          source[ccur] == '_' or  \
          source[ccur].isalpha()):
            break
        
        buffer += source[ccur]
 
        ccur += 1
        cur += 1
 
    return (cur, buffer)
 
def get_number(source, cursor):
    buffer = '' 
    ccur = cursor  
    cur = 0 
 
    while ccur < len(source):
        if not (source[ccur].isalnum() or source[ccur] in ('.', 'x', 'X')):
            break
 
        buffer += source[ccur]
        cur += 1
        ccur += 1
 
    return (cur, buffer)
 
def get_string(source, cursor):
    buffer = ''   
    ccur = cursor   
    cur = 0  
    lni = 0  
 
    instr = False
    hasEND = False
 
    schr = ''
 
    while ccur < len(source):
        if instr and source[ccur] == schr and source[ccur - 1] != '\\':
            hasEND = True  
            break
 
        if source[ccur] == '\n':
            lni += 1
 
        if instr:
            buffer += source[ccur]
        cur += 1
        ccur += 1
 
        if not instr:
            schr = source[ccur-1]
            instr = True
 
    if not hasEND:
        return (-1, 0, 0)
 
    return (cur+1, lni, buffer)  
 
class Cursor:
    def __init__(self, value=0):
        self.value = value
 
 
class Token:
    def __init__(self, value, ttype, ln):
        self.value = value
        self.ttype = ttype
        self.ln = ln
 
    def __repr__(self):
        return '<Token \'{0}\'  Type:{1}  LineNumber:{2}>'.format(
            self.value,
            self.ttype,
            self.ln
            )
 
    __str__ = __repr__ 
 
 
class TokenStream:
    def __init__(self):
        self.__tli = []
 
    def __iter__(self):
        return iter(self.__tli)
 
    def append(self, tok):
 
        self.__tli.append(tok)
 
    def __repr__(self):
        return repr(self.__tli)
 
    __str__ = __repr__
 
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.__tli[index]
 
        return self.__tli[index] \
                if len(self.__tli) > index  \
                else None
 
    def __len__(self):
        return len(self.__tli)
 
    @property
    def token_list(self):
        return self.__tli
 
 
class Lex:
    def __init__(self, filename, testmode=False):
        self.__filename = filename
 
        self.__source = open(filename, 'r', encoding='UTF-8').read()     \
            if not filename.startswith('.$str:')      \
            else (filename[len('.$str:'):] if testmode else open(filename, 'r', encoding='UTF-8').read())            
 
        self.__cursor = Cursor()  
        self.__stream = TokenStream()
        self.__ln = 1  
        
    
    @property
    def __chp(self):
        return self.__cursor.value
    
    @__chp.setter
    def __chp(self, v):
        self.__cursor.value = v
 
    def __movchr(self, step=1):
 
        self.__cursor.value += step
 
    @property
    def __chnow(self):
 
        return self.__source[self.__cursor.value]   \
            if self.__cursor.value < len(self.__source)     \
            else error_msg(-1, 'Syntax error', self.__filename)
 
    def __nextch(self, ni=1):
        return self.__source[self.__cursor.value + ni]      \
            if self.__cursor.value + ni < len(self.__source)       \
            else '<EOF>'
 
    def lex(self):
        buffer = ''
 
        #print(self.__source)
        
        while self.__chp < len(self.__source):
            c = self.__chnow
            
            if ord(c) == 10:
                self.__ln += 1
                self.__movchr(1)
                self.__stream.append(Token(
                    '\n',
                    LAP_ENTER,
                    self.__ln
                ))
 
            elif c in ('+', '-', '*', '^', '%', '|', '&'):  
                if self.__nextch() == '=':
                    self.__stream.append(Token(c+'=', 
                        {
                            '+':LAP_INP_PLUS,
                            '-':LAP_INP_SUB,
                            '*':LAP_INP_MUIT,
                            '%':LAP_INP_MOD,
                            '^':LAP_INP_XOR,
                        }[c],   
                    self.__ln))
                    self.__movchr(2)
 
                elif self.__nextch() in ('+', '-'):  
                    self.__stream.append(Token(c+c,
                    LAP_PLUS_PLUS if self.__nextch() == '+' else LAP_SUB_SUB, 
                    self.__ln))
                    self.__movchr(2)
 
                elif c == '|' and self.__nextch() == '|':  
                    self.__stream.append(Token(
                        '||',
                        LAP_OR,
                        self.__ln
                    ))
                    self.__movchr(2)
 
                elif c == '&' and self.__nextch() == '&':
                    self.__stream.append(Token(
                        '&&',
                        LAP_AND,
                        self.__ln
                    ))
                    self.__movchr(2)
 
                else:
                    self.__stream.append(Token(c,
                        {
                            '+':LAP_PLUS,
                            '-':LAP_SUB,
                            '*':LAP_MUIT,
                            '%':LAP_MOD,
                            '^':LAP_XOR,
                            '|':LAP_BIN_OR,
                            '&':LAP_BIN_AND
                        }[c], 
                    self.__ln))
                    self.__movchr(1)
 
            elif c in ('>', '<'):
                if self.__nextch() in ('>', '<'):
                    if self.__nextch(2) == '=': 
                        if c+self.__nextch() not in ('<<', '>>'):
                            error_msg(self.__ln,
                                'Syntax error:{0}'.format(c + self.__nextch()+self.__nextch(2)),
 
                                self.__filename)
 
                        self.__stream.append(Token(c+c+'=',
                            {
                                '>>':LAP_INP_RSHIFT,
                                '<<':LAP_INP_LSHIFT
                            }.get(c+self.__nextch()),
                            self.__ln
                        ))
 
                        self.__movchr(3)
                    
                    else:   
                        if c+self.__nextch() not in ('<<', '>>'):
                            if c+self.__nextch() == '<>':
                                self.__stream.append(Token(
                                    '<',
                                    LAP_SMALER,
                                    self.__ln
                                    ))
 
                                self.__stream.append(Token(
                                    '>',
                                    LAP_LARGER,
                                    self.__ln
                                    ))
                                
                                self.__movchr(2)
                                continue
 
                            error_msg(self.__ln, 
                                    'Syntax error:{0}'.format(c + self.__nextch()),
                                    self.__filename)
 
                        self.__stream.append(Token(
                            c+self.__nextch(),
                            {
                                '>>':LAP_INP_RSHIFT,
                                '<<':LAP_INP_LSHIFT
                            }[c+self.__nextch()],
                            self.__ln
                        ))
                        self.__movchr(2)
 
                elif self.__nextch() == '=':
                    self.__stream.append(Token(
                        c+'=',
                        LAP_LARGER_EQ if c == '>' else LAP_SMALER_EQ,
                        self.__ln  
                    ))
                    self.__movchr(2)
 
                else:
                    self.__stream.append(Token(
                        c,
                        LAP_LARGER if c == '>' else LAP_SMALER,
                        self.__ln 
                    ))
                    self.__movchr()
 
            elif c == '/':
                if self.__nextch() == '/':
                    self.__movchr(skip_comment_line(self.__source, self.__chp))
                    self.__ln += 1
                
                elif self.__nextch() == '*':
                    self.__movchr(2)
                    mov, lni = skip_comment_block(self.__source, self.__chp)
 
                    if mov == -1:
                        error_msg(-1, 'EOL while scanning comment block', self.__filename)
 
                    self.__movchr(mov)
                    self.__ln += lni
 
                elif self.__nextch == '=':
                    self.__stream.append(Token(
                        '/=',
                        LAP_INP_DIV,
                        self.__ln
                    ))
                    self.__movchr(2)
 
                else:
                    self.__stream.append(Token(
                        '/',
                        LAP_DIV,
                        self.__ln
                    ))
                    self.__movchr()
 
            elif c in ('(', ')', '[', ']', '{', '}', 
                       ',', '.', ';', '$', '@', '#', '\\',':'):
                self.__stream.append(Token(
                    c, 
                    {
                        '(':LAP_SLBASKET, 
                        ')':LAP_SRBASKET, 
                        '[':LAP_MLBASKET, 
                        ']':LAP_MRBASKET, 
                        '{':LAP_LLBASKET, 
                        '}':LAP_LRBASKET,
                        ',':LAP_COMMA, 
                        '.':LAP_DOT, 
                        ';':LAP_SEMI, 
                        '$':LAP_MONEY, 
                        '@':LAP_AT,
                        '#':LAP_WELL,
                        '\\':LAP_ESCAPE,
                        ':':LAP_COLON
                    }[c],
                    self.__ln
                ))
                self.__movchr()
            
            elif c == '!':
                if self.__nextch() == '=':  #!=
                    self.__stream.append(Token(
                        '!=',
                        LAP_UEQ,
                        self.__ln
                    ))
                    self.__movchr(2)
                
                else:  
                    self.__stream.append(Token(
                        '!',
                        LAP_NOT,
                        self.__ln
                    ))
                    self.__movchr()
 
            elif c.isspace() or ord(c) in [x for x in range(32) if x not in (10, 13)] or ord(c) == 127:
                self.__movchr()
 
            elif c.isalpha() or c == '_':
                mov, buf = get_identifier(self.__source, self.__chp)
                self.__stream.append(Token(
                    buf,
                    LAP_IDENTIFIER,
                    self.__ln
                ))
                self.__movchr(mov)
 
            elif c.isalnum():
                mov, buf = get_number(self.__source, self.__chp)
                self.__stream.append(Token(
                    buf,
                    LAP_NUMBER,
                    self.__ln
                ))
                self.__movchr(mov)
 
            elif c == '=':
                if self.__nextch() == '=':
                    self.__stream.append(Token(
                        '==',
                        LAP_EQ,
                        self.__ln
                    ))
                    self.__movchr(2)
 
                else:
                    self.__stream.append(Token(
                        '=',
                        LAP_ASSI,
                        self.__ln
                    ))
                    self.__movchr()
 
            elif c in ('"', '\''):
                mov, lni, buf = get_string(self.__source, self.__chp)
 
                if mov == -1:
                    error_msg(self.__ln, 'EOL while scanning string literal', self.__filename)
                
                self.__stream.append(Token(
                    buf,
                    LAP_STRING,
                    self.__ln
                ))
 
                self.__ln += lni
                self.__movchr(mov)
 
                
            else:
                error_msg(self.__ln, 'Unknown character', self.__filename)
 
        if self.__nextch(-1) == '\\n':
            self.__stream.append(Token(
                '\n',
                LAP_ENTER,
                self.__ln
            ))
 
        self.__stream.append(Token(
                '<EOF>',
                LAP_EOF,
                self.__ln
            ))
 
        return self.__stream
 
if __name__ == '__main__':
    print (Lex('tests/test.ail').lex())
