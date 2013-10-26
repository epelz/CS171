# Eric Pelz
# CS 171: Introduction to Computer Graphics

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc

import sys
import openInventor as oi

### Parser specific functions ###
tokens = ('PCAMERA', 'POS', 'ORIENT', 'NDIST', 'FDIST', 'LEFT', 'RIGHT', \
    'TOP', 'BOTTOM', 'SEPARATOR', 'TRANSFORM', 'TRANSLAT', 'ROT', 'SFACTOR', \
    'COORD3', 'POINT', 'IFACESET', 'COORDINDEX', 'COMMA', 'LBRACE', 'RBRACE', \
    'LBRACKET', 'RBRACKET', 'NUMBER', 'POINTLIGHT', 'MATERIAL', 'ACOLOR', \
    'SCOLOR', 'DCOLOR', 'SHININESS', 'NORMAL', 'LOCATION', 'COLOR', 'VECTOR', \
    'NORMINDEX')

def simpleLexer():
  # set up regex for number parsing
  reals_noE = r'-?(\d*\.\d*|\d+)'
  reals = reals_noE + r'(e-?\d+)?'

  t_PCAMERA = 'PerspectiveCamera'
  t_POS = 'position'
  t_ORIENT = 'orientation'
  t_NDIST = 'nearDistance'
  t_FDIST = 'farDistance'
  t_LEFT = 'left'
  t_RIGHT = 'right'
  t_TOP = 'top'
  t_BOTTOM = 'bottom'

  t_POINTLIGHT = 'PointLight'
  t_LOCATION = 'location'
  t_COLOR = 'color'

  t_SEPARATOR = 'Separator'
  t_TRANSFORM = 'Transform'
  t_TRANSLAT = 'translation'
  t_ROT = 'rotation'
  t_SFACTOR = 'scaleFactor'

  t_COORD3 = 'Coordinate3'
  t_POINT = 'point'
  t_IFACESET = 'IndexedFaceSet'
  t_COORDINDEX = 'coordIndex'
  t_NORMINDEX = 'normalIndex'

  t_COMMA = ','
  t_LBRACE = '{'
  t_RBRACE = '}'
  t_LBRACKET = r'\['
  t_RBRACKET = r'\]'

  t_MATERIAL = 'Material'
  t_ACOLOR = 'ambientColor'
  t_DCOLOR = 'diffuseColor'
  t_SCOLOR = 'specularColor'
  t_SHININESS = 'shininess'

  t_NORMAL = 'Normal'
  t_VECTOR = 'vector'

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
  ## Parse overall blocks ##
  def p_file(p):
    '''file : blocks'''
    # split to camera/separator and instantiate new object
    # Note: assumes one camera, pointlight and at least one separator
    camera = None
    pointLight = None
    separators = []
    for group in p[1]:
      if isinstance(group, oi.PerspectiveCamera):
        camera = group
      if isinstance(group, oi.PointLight):
        pointLight = group
      elif isinstance(group, oi.Separator):
        separators.append(group)
    p[0] = oi.InventorData(camera, pointLight, separators)
  def p_blocks(p):
    '''blocks : block
              | block blocks'''
    if len(p) == 3: # blocks : block blocks
      p[0] = [p[1]] + p[2]
    else:           # blocks : block
      p[0] = [p[1]]
  def p_block(p):
    '''block : camerablock
             | sepblock
             | plightblock'''
    p[0] = p[1]

  ## Parse camera block ##
  def p_camerablock(p):
    '''camerablock : PCAMERA open cameralines close'''
    # split and instantiate new object
    data = dict(p[3])
    p[0] = oi.PerspectiveCamera(
        data['position'],
        data['orientation'],
        data['nearDistance'],
        data['farDistance'],
        data['left'],
        data['right'],
        data['top'],
        data['bottom'])
  def p_cameralines(p):
    '''cameralines : cameraline
                   | cameraline cameralines'''
    if len(p) == 3: # cameralines : cameraline cameralines
      p[0] = [p[1]] + p[2]
    else:           # cameralines : cameraline
      p[0] = [p[1]]
  def p_cameraline(p):
    '''cameraline : POS triple
                  | ORIENT quad
                  | NDIST NUMBER
                  | FDIST NUMBER
                  | LEFT NUMBER
                  | RIGHT NUMBER
                  | TOP NUMBER
                  | BOTTOM NUMBER'''
    p[0] = (p[1], p[2])

  ## Parse point light ##
  def p_plightblock(p):
    '''plightblock : POINTLIGHT open plightlines close'''
    # use input values for location and color, otherwise use defaults
    location = [0, 1, 1]
    color = [1, 1, 1]
    for type, values in p[3]:
      if type == 'location':
        location = values
      elif type == 'color':
        color = values
    p[0] = oi.PointLight(location, color)
  def p_plightlines(p):
    '''plightlines : plightline
                   | plightline plightlines'''
    if len(p) == 3: # plightlines : plightline plightlines
      p[0] = [p[1]] + p[2]
    else:           # plightlines : plightline
      p[0] = [p[1]]
  def p_plightline(p):
    '''plightline : LOCATION triple
                  | COLOR triple'''
    p[0] = (p[1], p[2])

  ## Parse separator block ##
  def p_sepblock(p):
    '''sepblock : SEPARATOR open sepitems close'''
    # split into transforms/coordinate3/faceSet and instantiate new object
    # Note: assumes one coordinate3, one indexedFaceSet, and multiple transforms
    transforms = []
    material = None
    coordinate3 = None
    normal = None
    indexedFaceSet = None
    for group in p[3]:
      if isinstance(group, oi.Material):
        material = group
      elif isinstance(group, oi.Coordinate3):
        coordinate3 = group
      elif isinstance(group, oi.IndexedFaceSet):
        indexedFaceSet = group
      elif isinstance(group, oi.Normal):
        normal = group
      else:
        transforms.append(group)
    p[0] = oi.Separator(transforms, material, coordinate3, normal, indexedFaceSet)
  def p_sepitems(p):
    '''sepitems : sepitem
                | sepitem sepitems'''
    if len(p) == 3: # sepitems : sepitem sepitems
      p[0] = [p[1]] + p[2]
    else:           # sepitems : sepitem
      p[0] = [p[1]]
  def p_sepitem(p):
    '''sepitem : TRANSFORM open translines close
               | COORD3 open POINT sqopen triples sqclose close
               | IFACESET open ifslines close
               | MATERIAL open matlines close
               | NORMAL open VECTOR sqopen triples sqclose close'''
    type = p[1]
    if type == 'Transform':
      p[0] = oi.TransformBlock(p[3])
    elif type == 'Coordinate3':
      p[0] = oi.Coordinate3(p[5])
    elif type == 'IndexedFaceSet':
      data = dict(p[3])
      p[0] = oi.IndexedFaceSet(
          data['coordIndex'],
          data['normalIndex'])
    elif type == 'Material':
      # split and instantiate new object
      data = dict(p[3])
      p[0] = oi.Material(
          data['ambientColor'],
          data['diffuseColor'],
          data['specularColor'],
          data['shininess'])
    elif type == 'Normal':
      p[0] = oi.Normal(p[5])

  ## Parse transformation matrices ##
  def p_translines(p):
    '''translines : transline
                  | transline translines'''
    if len(p) == 3: # translines : transline translines
      p[0] = [p[1]] + p[2]
    else:           # translines : transline
      p[0] = [p[1]]
  def p_transline(p):
    '''transline : TRANSLAT triple
                 | SFACTOR triple
                 | ROT quad'''
    type, data = p[1:]
    if type == 'translation':
      p[0] = oi.Transform.newTranslation(data)
    elif type == 'scaleFactor':
      p[0] = oi.Transform.newScaleFactor(data)
    elif type == 'rotation':
      p[0] = oi.Transform.newRotation(data)

  ## Parse IndexedFaceSets ##
  def p_ifslines(p):
    '''ifslines : ifsline
                | ifsline ifslines'''
    if len(p) == 3: # ifslines : ifsline ifslines
      p[0] = [p[1]] + p[2]
    else:           # ifslines : ifsline
      p[0] = [p[1]]
  def p_ifsline(p):
    '''ifsline : COORDINDEX sqopen singles sqclose
               | NORMINDEX sqopen singles sqclose'''
    p[0] = (p[1], p[3])

  ## Parse Material ##
  def p_matlines(p):
    '''matlines : matline
                | matline matlines'''
    if len(p) == 3: # matlines : matline matlines
      p[0] = [p[1]] + p[2]
    else:           # matlines : matline
      p[0] = [p[1]]
  def p_matline(p):
    '''matline : ACOLOR triple
               | DCOLOR triple
               | SCOLOR triple
               | SHININESS NUMBER'''
    p[0] = (p[1], p[2])

  ## Parse parts of the above ##
  def p_single(p):
    '''single : NUMBER'''
    p[0] = p[1]
  def p_singles(p):
    '''singles : single
               | single COMMA singles'''
    if len(p) == 4: # singles : single singles
      p[0] = [p[1]] + p[3]
    else:           # singles : single
      p[0] = [p[1]]
  def p_triple(p):
    '''triple : NUMBER NUMBER NUMBER'''
    p[0] = p[1:]
  def p_triples(p):
    '''triples : triple
               | triple COMMA triples'''
    if len(p) == 4: # triples : triple triples
      p[0] = [p[1]] + p[3]
    else:           # triples : triple
      p[0] = [p[1]]
  def p_quad(p):
    '''quad : NUMBER NUMBER NUMBER NUMBER'''
    p[0] = p[1:]
  def p_open(p):
    '''open : LBRACE'''
    pass
  def p_close(p):
    '''close : RBRACE'''
    pass
  def p_sqopen(p):
    '''sqopen : LBRACKET'''
    pass
  def p_sqclose(p):
    '''sqclose : RBRACKET'''
    pass

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
