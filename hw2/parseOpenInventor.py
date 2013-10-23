# Eric Pelz
# CS 171: Introduction to Computer Graphics

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc
from matrix import MatrixExtended

import sys

### OpenInventor classes ###
class InventorData():
  def __init__(self, perspectiveCamera, separators):
    self.perspectiveCamera = perspectiveCamera
    self.separators = separators

  def __repr__(self):
    return "[InventorData: %s, %s]" % (self.perspectiveCamera, self.separators)

  def getSeparators(self):
    return self.separators
  def getNumSeparators(self):
    return len(self.separators)
  def getPerspectiveCamera(self):
    return self.perspectiveCamera

class Separator():
  def __init__(self, transforms, coordinate3, indexedFaceSet):
    self.transforms = transforms
    self.coordinate3 = coordinate3
    self.indexedFaceSet = indexedFaceSet
  def __repr__(self):
    return "[Separator: transforms: %s, coordinate3: %s, indexedfaceset: %s]" % (self.transforms, self.coordinate3, self.indexedFaceSet)

  def getPolygons(self):
    coords = self.coordinate3.getPoints()
    polygons = []
    for indexedFace in self.indexedFaceSet.getFaces():
      polygons.append([coords[idx] for idx in indexedFace])
    return polygons
  def getTransforms(self):
    return self.transforms
  def getCoordinate3(self):
    return self.coordinate3
  def getIndexedFaceSet(self):
    return self.indexedFaceSet

class PerspectiveCamera():
  def __init__(self, pos, orien, nearD, farD, left, right, top, bottom):
    self.pos = pos
    self.orien = orien
    self.nearD = nearD
    self.farD = farD
    self.left = left
    self.right = right
    self.top = top
    self.bottom = bottom
  def __repr__(self):
    return "[PerspectiveCamera:  position: %s, orientation: %s, nearDistance: %s, farDistance: %s, left: %s, right: %s, top: %s, bottom: %s]" % \
      (self.pos, self.orien, self.nearD, self.farD, self.left, self.right, self.top, self.bottom)

  def getCameraTransformInverse(self):
    """Returns (RT)^(-1) = C^(-1); the camera transform."""
    R = MatrixExtended.getRotationMatrix(*self.orien)
    T = MatrixExtended.getTranslationMatrix(*self.pos)
    return T.mult(R).getInverse()

  def getPerspectiveProjection(self):
    """Returns the perspective projection matrix for this camera transform."""
    return MatrixExtended.getPerspectiveProjectionMatrix(
        self.left,
        self.right,
        self.bottom,
        self.top,
        self.nearD,
        self.farD)

class TransformBlock():
  def __init__(self, transformList):
    self.translation, self.rotation, self.scaleFactor = (None, None, None)
    for transform in transformList:
      if transform.transformType == Transform.translation:
        self.translation = transform
      elif transform.transformType == Transform.rotation:
        self.rotation = transform
      elif transform.transformType == Transform.scaleFactor:
        self.scaleFactor = transform
  def __repr__(self):
    return "[TransformBlock: translation: %s, rotation: %s, scaling: %s]" % (self.translation, self.rotation, self.scaleFactor)

  def multiplyTransformBlock(self):
    """Returns a matrix built from this transform block (S=TRS)."""
    result = None
    if self.scaleFactor:
      result = self.scaleFactor.getMatrix()
    if self.rotation:
      if result is not None:
        result = self.rotation.getMatrix().mult(result)
      else:
        result = self.rotation.getMatrix()
    if self.translation:
      if result is not None:
        result = self.translation.getMatrix().mult(result)
      else:
        result = self.translation.getMatrix()
    return result

class Transform():
  # types of transforms
  translation, rotation, scaleFactor = range(3)

  def __init__(self, transformType, data):
    self.transformType = transformType
    self.data = data
  def __repr__(self):
    return "[Transform (%s): %s]" % (self.transformType, str(self.data))
  def getMatrix(self):
    """Returns the transformation matrix this object represents."""
    if self.transformType == self.translation:
      return MatrixExtended.getTranslationMatrix(*self.data)
    elif self.transformType == self.rotation:
      return MatrixExtended.getRotationMatrix(*self.data)
    elif self.transformType == self.scaleFactor:
      return MatrixExtended.getScalingMatrix(*self.data)
  ## Static methods to initialize new transformation matrices ##
  @staticmethod
  def newTranslation(data):
    return Transform(Transform.translation, data)
  @staticmethod
  def newRotation(data):
    return Transform(Transform.rotation, data)
  @staticmethod
  def newScaleFactor(data):
    return Transform(Transform.scaleFactor, data)

class Coordinate3():
  def __init__(self, data):
    self.points = data
  def __repr__(self):
    return "[Coordinate3: %s]" % (str(self.points))

  def getPoints(self):
    return self.points

class IndexedFaceSet():
  def __init__(self, data):
    # split data to faces, each separated by -1
    faces = [[]]
    for point in data:
      if point >= 0:
        faces[-1].append(int(point))
      else:
        faces.append([])
    faces = filter(lambda x: x, faces) # filter out any empty lists
    self.faces = faces
  def __repr__(self):
    return "[IndexedFaceSet: %s]" % (str(self.faces))

  def getFaces(self):
    return self.faces

### Parser specific functions ###
tokens = ('PCAMERA', 'POS', 'ORIENT', 'NDIST', 'FDIST', 'LEFT', 'RIGHT', \
    'TOP', 'BOTTOM', 'SEPARATOR', 'TRANSFORM', 'TRANSLAT', 'ROT', 'SFACTOR', \
    'COORD3', 'POINT', 'IFACESET', 'COORDINDEX', 'COMMA', 'LBRACE', 'RBRACE', \
    'LBRACKET', 'RBRACKET', 'NUMBER')

def simpleLexer():
    # set up regex for number parsing
    reals = r'-?(\d*\.\d+|\d+)'

    t_PCAMERA = 'PerspectiveCamera'
    t_POS = 'position'
    t_ORIENT = 'orientation'
    t_NDIST = 'nearDistance'
    t_FDIST = 'farDistance'
    t_LEFT = 'left'
    t_RIGHT = 'right'
    t_TOP = 'top'
    t_BOTTOM = 'bottom'

    t_SEPARATOR = 'Separator'
    t_TRANSFORM = 'Transform'
    t_TRANSLAT = 'translation'
    t_ROT = 'rotation'
    t_SFACTOR = 'scaleFactor'

    t_COORD3 = 'Coordinate3'
    t_POINT = 'point'
    t_IFACESET = 'IndexedFaceSet'
    t_COORDINDEX = 'coordIndex'
    t_COMMA = ','
    t_LBRACE = '{'
    t_RBRACE = '}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'

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
        # Note: assumes one camera and at least one separator
        camera = None
        separators = []
        for group in p[1]:
          if isinstance(group, PerspectiveCamera):
            camera = group
          elif isinstance(group, Separator):
            separators.append(group)
        p[0] = InventorData(camera, separators)
    def p_blocks(p):
        '''blocks : block
                  | block blocks'''
        if len(p) == 3: # blocks : block blocks
          p[0] = [p[1]] + p[2]
        else:           # blocks : block
          p[0] = [p[1]]
    def p_block(p):
        '''block : camerablock
                 | sepblock'''
        p[0] = p[1]

    ## Parse camera block ##
    def p_camerablock(p):
        '''camerablock : PCAMERA open cameralines close'''
        # split and instantiate new object
        data = dict(p[3])
        p[0] = PerspectiveCamera(
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

    ## Parse separator block ##
    def p_sepblock(p):
        '''sepblock : SEPARATOR open sepitems close'''
        # split into transforms/coordinate3/faceSet and instantiate new object
        # Note: assumes one coordinate3, one indexedFaceSet, and multiple transforms
        transforms = []
        coordinate3 = None
        indexedFaceSet = None
        for group in p[3]:
          if isinstance(group, Coordinate3):
            coordinate3 = group
          elif isinstance(group, IndexedFaceSet):
            indexedFaceSet = group
          else:
            transforms.append(group)
        p[0] = Separator(transforms, coordinate3, indexedFaceSet)
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
                   | IFACESET open ifslines close'''
        type = p[1]
        if type == 'Transform':
          p[0] = TransformBlock(p[3])
        elif type == 'Coordinate3':
          p[0] = Coordinate3(p[5])
        elif type == 'IndexedFaceSet':
          p[0] = IndexedFaceSet(p[3])

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
          p[0] = Transform.newTranslation(data)
        elif type == 'scaleFactor':
          p[0] = Transform.newScaleFactor(data)
        elif type == 'rotation':
          p[0] = Transform.newRotation(data)

    ## Parse IndexedFaceSets ##
    def p_ifslines(p):
        '''ifslines : ifsline
                    | ifsline ifslines'''
        if len(p) == 3: # ifslines : ifsline ifslines
          p[0] = [p[1]] + p[2]
        else:           # ifslines : ifsline
          p[0] = p[1]
    def p_ifsline(p):
        '''ifsline : COORDINDEX sqopen singles sqclose'''
        p[0] = p[3]

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
