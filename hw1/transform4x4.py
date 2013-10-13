# Eric Pelz
# CS 171: Introduction to Computer Graphics

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc

from matrix import MatrixExtended
import sys
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
          p[0] = p[1] + [p[2]]
        else:           # lines : line
          p[0] = [p[1]]

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

def parseAndMultiplyTransformations(data, parser):
  # parse transformations from data
  transformations = parser.parse(data)

  # multiply transformations and return the result
  # Note: we perform a foldr (reduce is foldl, so reverse and multiply opposite)
  transformations.reverse()
  return reduce(lambda y,x: x*y, transformations)

if __name__=='__main__':
  # build lexer and parser
  simpleLexer()
  parser = simpleParser()

  # read and parse description of transformation from stdin
  data = ''.join(sys.stdin)
  mtx = parseAndMultiplyTransformations(data, parser)

  # print result to stdout
  for row in mtx.tolist():
    for elem in row:
      sys.stdout.write("{:8.4f}".format(elem))
    sys.stdout.write("\n")
