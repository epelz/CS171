# Eric Pelz
# CS 171: Introduction to Computer Graphics

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc

from matrix import MatrixExtended
import sys
tokens = ('NUMBER', 'POLYLINE')

def simpleLexer():
    # set up regex for number parsing
    reals = r'-?(\d+\.\d+)'

    t_POLYLINE = 'polyline'

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

    def p_line(p):
        '''line : POLYLINE points'''
        p[0] = p[2]

    def p_points(p):
        '''points : points point
                  | point'''
        if len(p) == 3: # points : points point
          p[0] = p[1] + [p[2]]
        else:           # points : point
          p[0] = [p[1]]

    def p_point(p):
        '''point : NUMBER NUMBER'''
        p[0] = (p[1], p[2])

    # Error rule for syntax errors
    def p_error(p):
        print "Syntax error in input!"

    # Build the parser
    return yacc.yacc()

def matchPointPairs(listOfPoints):
  lines = []
  for points in listOfPoints:
    lastPoint = None
    for point in points:
      if lastPoint:
        lines += [(lastPoint, point)]
      lastPoint = point
  return lines

def getPixelMatrix(xmin, xmax, ymin, ymax, xRes, yRes, lineSegments):
  pass

if __name__=='__main__':
  # build lexer and parser
  simpleLexer()
  parser = simpleParser()

  # TODO: READ OTHER INFORMATION FROM STDIN
  # read and parse point pairs
  data = ''.join(sys.stdin)
  listOfPoints = parser.parse(data)
  lineSegments = matchPointPairs(listOfPoints)

  # TODO: GET PIXEL MATRIX

  # TODO: PRINT OUTPUT
