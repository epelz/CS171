# Eric Pelz
# CS 171: Introduction to Computer Graphics

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc

import sys
tokens = ('NUMBER', 'POLYLINE')

def simpleLexer():
    # set up regex for number parsing
    reals = r'-?(\d+\.\d*)'

    t_POLYLINE = 'polyline'

    # special characters to be ignored (spaces and tabs)
    t_ignore = ' \t\r'

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

def calcPixelMatrix(xMin, xMax, yMin, yMax, xRes, yRes, lineSegments):
  '''Given a grid, line segments, and target image size, returns a matrix of pixel data.'''
  def pointToPixel(x, y):
    '''Converts a point to its location in the pixel space.'''
    xScaling = xRes/(xMax-xMin)
    yScaling = yRes/(yMax-yMin)
    newX = (x - xMin) * xScaling
    newY = (y - yMin) * yScaling
    return (int(newX), int(newY))
  def bresenhamAlgorithm(ppt1, ppt2, outMatrix):
    '''Uses Brensenham's Algorithm to determine points to shade in a matrix'''
    # Always start with x1 <= x2
    if ppt1[0] > ppt2[0]:
      ppt1, ppt2 = ppt2, ppt1

    ## casework to generalize algorithm (if slope > 1 or slope < 0)
    neg = False
    swap = False
    # calculate the slope
    if not ppt2[0] == ppt1[0]:
      slope = (ppt2[1] - ppt1[1]) / float(ppt2[0] - ppt1[0])
    else: # if undefined, set to greater than 1
      slope = 5
    # negate y if slope is negative
    if slope < 0:
      neg = True
      ppt1 = (ppt1[0], -1 * ppt1[1])
      ppt2 = (ppt2[0], -1 * ppt2[1])
      slope *= -1
    # swap x and y if slope is large
    if slope > 1:
      swap = True
      # again, make sure new x1 <= x2
      if ppt1[1] > ppt2[1]:
        ppt1, ppt2 = ppt2, ppt1
      py1, px1 = ppt1
      py2, px2 = ppt2
    else:
      px1, py1 = ppt1
      px2, py2 = ppt2

    ## proceed with the algorihtm
    y = py1
    dy = py2 - py1
    dxdy = (py2-py1)+(px1-px2)
    F = (py2-py1)+(px1-px2)
    for x in range(px1, px2+1):
      # undo negations or swaps before shading pixel
      xx, yy = x, y
      if swap:
        xx, yy = yy, xx
      if neg:
        yy *= -1

      if xx >= 0 and xx <= xRes and yy >= 0 and yy <= yRes:
        outMatrix[xx][yy] = True
      if F < 0:
        F += dy
      else:
        y += 1
        F += dxdy

  # initialize new matrix of appropriate size
  pixelMatrix = [[False for _ in range(yRes)] for _ in range(xRes)]

  # for each segment, convert to pixelspace and draw
  for pt1, pt2 in lineSegments:
    ppt1 = pointToPixel(pt1[0], pt1[1])
    ppt2 = pointToPixel(pt2[0], pt2[1])
    bresenhamAlgorithm(ppt1, ppt2, pixelMatrix)

  return pixelMatrix

def printPPMFormat(xRes, yRes, pixelMatrix):
  print "P3"
  print xRes, yRes
  print "255"
  for pixelRow in pixelMatrix:
    for pixel in pixelRow:
      if pixel: # color black
        print "255 255 255"
      else:
        print "0 0 0"

if __name__=='__main__':
  # build lexer and parser
  simpleLexer()
  parser = simpleParser()

  # read and parse commandline arguments
  if len(sys.argv) != 7:
    print "Error: Incorrect number of parameters. Please call using:"
    print "\t$ python draw2d.py xMin xMax yMin yMax xRes yRes < data.2d"
    exit(-1)
  xMin, xMax, yMin, yMax = map(float, sys.argv[1:5])
  xRes, yRes = map(int, sys.argv[5:7])

  # read and parse point pairs
  data = ''.join(sys.stdin)
  listOfPoints = parser.parse(data)
  lineSegments = matchPointPairs(listOfPoints)

  pixelMatrix = calcPixelMatrix(xMin, xMax, yMin, yMax, xRes, yRes, lineSegments)

  printPPMFormat(xRes, yRes, pixelMatrix)
