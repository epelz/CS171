# Eric Pelz
# CS 171: Introduction to Computer Graphics

from matrix import MatrixExtended

class InventorData():
  def __init__(self, perspectiveCamera, pointLight, separators):
    self.perspectiveCamera = perspectiveCamera
    self.pointLight = pointLight
    self.separators = separators

  def __repr__(self):
    return "[InventorData: %s, %s, %s]" % \
        (self.perspectiveCamera, self.pointLight, self.separators)

  def getSeparators(self):
    return self.separators
  def getNumSeparators(self):
    return len(self.separators)
  def getPerspectiveCamera(self):
    return self.perspectiveCamera
  def getPointLight(self):
    return self.pointLight

class Separator():
  def __init__(self, transforms, material, coordinate3, normal, indexedFaceSet):
    self.transforms = transforms
    self.material = material
    self.coordinate3 = coordinate3
    self.normal = normal
    self.indexedFaceSet = indexedFaceSet
  def __repr__(self):
    return "[Separator: %s, %s, %s, %s, %s]" % \
        (self.transforms, self.material, self.coordinate3, self.normal, self.indexedFaceSet)

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
  def getNormal(self):
    return self.normal
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

class PointLight():
  def __init__(self, location, color):
    self.location = location
    self.color = verifyColor(color)
  def __repr__(self):
    return "[PointLight: location: %s, color: %s]" % (self.location, self.color)

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
  def __init__(self, coordData, normData):
    def splitIntoFaces(data):
      """split data to faces, each separated by -1"""
      faces = [[]]
      for point in data:
        if point >= 0:
          faces[-1].append(int(point))
        else:
          faces.append([])
      return filter(lambda x: x, faces) # filter out any empty lists

    self.cFaces = splitIntoFaces(coordData)
    self.nFaces = splitIntoFaces(normData)
  def __repr__(self):
    return "[IndexedFaceSet: cFaces: %s, nFaces: %s]" % (str(self.cFaces), str(self.nFaces))

  # TODO RENAME IN OTHER FILES
  def getCFaces(self):
    return self.cFaces
  def getNFaces(self):
    return self.nFaces

class Material():
  def __init__(self, aColor, dColor, sColor, shininess):
    self.aColor = verifyColor(aColor)
    self.dColor = verifyColor(dColor)
    self.sColor = verifyColor(sColor)
    self.shininess = shininess
  def __repr__(self):
    return "[Material: aColor: %s, dColor: %s, sColor: %s, shininess: %s]" % \
        (self.aColor, self.dColor, self.sColor, self.shininess)

class Normal():
  def __init__(self, data):
    self.points = data
  def __repr__(self):
    return "[Normal: %s]" % (str(self.points))

  def getPoints(self):
    return self.points

### Helper function(s) ###
def verifyColor(color):
  """Returns the color in input, unless it is invalid"""
  if not all(map(lambda n: n >= 0.0 and n <= 1.0, color)):
      raise TypeError("Invalid color: %s" % (color))
  return color
