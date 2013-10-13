import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc

from matrix import MatrixExtended
import sys # TODO REMOVE
tokens = ('TRANSLATION', 'ROTATION', 'SCALEFACTOR', 'NUMBER')

def simpleLexer():
    # set up regex for number parsing
    posint = r'0|([1-9]\d*)'
    ints = r'-?(' + posint + r')'
    expanded_ints = r'(' + posint + r'|\.\d+|' + posint + r'\.\d+)' # e.g. 5, .5, or 5.5
    reals = r'-?' + expanded_ints + '(e' + ints + r')?'

    t_TRANSLATION = 'translation'
    t_ROTATION = 'rotation'
    t_SCALEFACTOR = 'scaleFactor'

    # special characters to be ignored (spaces and tabs)
    t_ignore = ' \t'

    # when we see real numbers what do we do?
    @TOKEN(reals)
    def t_NUMBER(t):
        # set the value of the token to its corresponding numerical value
        t.value = float(t.value)
        # once again return the token
        return t

    # do nothing when we see a comment
    def t_COMMENT(t):
        r'\#.*'
        pass

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    return lex.lex()


def simpleParser():
    def p_lines(p):
        '''lines : lines line
                 | line'''
        if len(p) == 3: # lines : lines line
          # TODO: Multiply matrices in the correct order
          p[0] = p[1] + [p[2]]
        else:
          p[0] = [p[1]] # lines : line

    def p_line_translation(p):
        '''line : TRANSLATION NUMBER NUMBER NUMBER'''
        p[0] = MatrixExtended.getTranslationMatrix(p[2], p[3], p[4])

    def p_line_rotation(p):
        '''line : ROTATION NUMBER NUMBER NUMBER NUMBER'''
        p[0] = MatrixExtended.getRotationMatrix(p[2], p[3], p[4], p[5])

    def p_line_scalefactor(p):
        '''line : SCALEFACTOR NUMBER NUMBER NUMBER'''
        p[0] = MatrixExtended.getScalingMatrix(p[2], p[3], p[4])

    # Error rule for syntax errors
    def p_error(p):
        print "Syntax error in input!"

    # Build the parser
    return yacc.yacc()

simpleLexer() # build lexer
parser = simpleParser() # build parser

# TODO: Put this in a main, and make it pretty
data = ''.join(sys.stdin)
a = parser.parse(data)
print a
