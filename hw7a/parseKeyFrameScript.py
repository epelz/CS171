# Eric Pelz
# CS 171: Introduction to Computer Graphics

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc

import sys
import keyFrameScript as kfs

### Parser specific functions ###
tokens = ('FRAME', 'TRANSLATION', 'ROTATION', 'SCALE', 'NUMBER')

def simpleLexer():
  # set up regex for number parsing
  reals_noE = r'-?(\d*\.\d*|\d+)'
  reals = reals_noE + r'(e-?\d+)?'

  t_FRAME = 'Frame'
  t_TRANSLATION = 'translation'
  t_ROTATION = 'rotation'
  t_SCALE = 'scale'

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
    #pass

  def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

  def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

  return lex.lex()

def simpleParser():
  ## Parse overall file ##
  def p_file(p):
    '''file : single keyframes'''
    # Note: assumes at least one keyframe
    p[0] = kfs.Script(int(p[1]), p[2])

  ## Parse keyframes ##
  def p_keyframes(p):
    '''keyframes : keyframe
                 | keyframe keyframes'''
    if len(p) == 3: # keyframes : keyframe keyframes
      p[0] = [p[1]] + p[2]
    else:           # keyframes : keyframe
      p[0] = [p[1]]
  def p_keyframe(p):
    '''keyframe : FRAME NUMBER translines'''
    frameNum = int(p[2])
    translation = None
    scale = None
    rotation = None

    # parse transformations
    for transform in p[3]:
      if transform.transformType == kfs.Transform.translation:
        assert translation is None
        translation = transform
      elif transform.transformType == kfs.Transform.scale:
        assert scale is None
        scale = transform
      elif transform.transformType == kfs.Transform.rotation:
        assert rotation is None
        rotation = transform

    p[0] = kfs.Frame(frameNum, \
        translation = translation, scale = scale, rotation = rotation)

  ## Parse transformation matrices ##
  def p_translines(p):
    '''translines : transline
                  | transline translines'''
    if len(p) == 3: # translines : transline translines
      p[0] = [p[1]] + p[2]
    else:           # translines : transline
      p[0] = [p[1]]
  def p_transline(p):
    '''transline : TRANSLATION triple
                 | SCALE triple
                 | ROTATION quad'''
    type, data = p[1:]
    if type == 'translation':
      p[0] = kfs.Transform.newTranslation(data)
    elif type == 'scale':
      p[0] = kfs.Transform.newScale(data)
    elif type == 'rotation':
      p[0] = kfs.Transform.newRotation(data)

  ## Parse parts of the above ##
  def p_single(p):
    '''single : NUMBER'''
    p[0] = p[1]
  def p_triple(p):
    '''triple : NUMBER NUMBER NUMBER'''
    p[0] = p[1:]
  def p_quad(p):
    '''quad : NUMBER NUMBER NUMBER NUMBER'''
    p[0] = p[1:]

  # Error rule for syntax errors
  def p_error(p):
    print "Syntax error in input!"

  # Build the parser
  return yacc.yacc()

def parse(data):
  # build lexer and parser
  simpleLexer()
  parser = simpleParser()

  return parser.parse(data)

if __name__=='__main__':
  data = ''.join(sys.stdin)
  print parse(data)
