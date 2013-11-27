# Eric Pelz
# CS 171: Introduction to Computer Graphics

from matrix import MatrixExtended

class InventorData():
  def __init__(self, perspectiveCamera, pointLights, separators):
    self.perspectiveCamera = perspectiveCamera
    self.pointLights = pointLights
    self.separators = separators

  def __repr__(self):
    return "[InventorData: %s, %s, %s]" % \
        (self.perspectiveCamera, self.pointLights, self.separators)

  def getSeparators(self):
    return self.separators
  def getNumSeparators(self):
    return len(self.separators)
  def getPerspectiveCamera(self):
    return self.perspectiveCamera
  def getPointLights(self):
    return self.pointLights
  def hasLights(self):
    return len(self.pointLights) > 0

class Separator():
  def __init__(self, transforms, material, coordinate3, normal, indexedFaceSet, 
      texture2, tcoordinate2):
    self.transforms = transforms
    self.material = material
    self.coordinate3 = coordinate3
    self.normal = normal
    self.indexedFaceSet = indexedFaceSet
    self.texture2 = texture2
    self.tcoordinate2 = tcoordinate2
  def __repr__(self):
    return "[Separator: %s, %s, %s, %s, %s, %s, %s]" % \
        (self.transforms, self.material, self.coordinate3, self.normal, self.indexedFaceSet, self.texture2, self.tcoordinate2)

  def getPolygons(self):
    """Returns the (coordinate,normal) or (coordinate, texcoords) for each polygon.
    Assumes 1:1 mapping of vertex to normals"""
    coords = self.coordinate3.getPoints()
    cFaces = self.indexedFaceSet.getCFaces()

    if self.normal:
      coords2 = self.normal.getPoints()
      faces2 = self.indexedFaceSet.getNFaces()
    else:
      coords2 = self.tcoordinate2.getPoints()
      faces2 = self.indexedFaceSet.getTFaces()
    assert len(cFaces) == len(faces2)

    polygons = []
    for faceNum in range(len(cFaces)):
      assert len(cFaces[faceNum]) == len(faces2[faceNum])
      polygons.append(zip(
        [coords[idx] for idx in cFaces[faceNum]],
        [coords2[idx] for idx in faces2[faceNum]]))
    #import sys; print >>sys.stderr, polygons
    return polygons
  def getTransforms(self):
    return self.transforms
  def getCoordinate3(self):
    return self.coordinate3
  def getNormal(self):
    return self.normal
  def getIndexedFaceSet(self):
    return self.indexedFaceSet
  def getTransformedNormal(self):
    return (self.transforms.multiplyNormalTransform()).mult(self.normal)
  def getMaterial(self):
    return self.material
  def hasMaterial(self):
    return self.material is not None
  def getTexture2Path(self):
    return self.texture2.getFilename()
  def getTextureCoordinate2(self):
    return self.tcoordinate2

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

  def getCameraPosition(self):
    return self.pos
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

  def getLocation(self):
    return self.location
  def getColor(self):
    return self.color

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
  def multiplyNormalTransform(self):
    """Returns the matrix Transpose(Inverse(R * S)), which is used to transform normals."""
    result = None
    if self.scaleFactor:
      result = self.scaleFactor.getMatrix()
    if self.rotation:
      if result is not None:
        result = self.rotation.getMatrix().mult(result)
      else:
        result = self.rotation.getMatrix()
    return (result.getI()).getT()

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

class Texture2():
  def __init__(self, filename):
    self.filename = filename
  def __repr__(self):
    return "[Texture2: %s]" % (str(self.filename))

  def getFilename(self):
    return self.filename

class TextureCoordinate2():
  def __init__(self, data):
    self.points = data
  def __repr__(self):
    return "[TextureCoordinate2: %s]" % (str(self.points))

  def getPoints(self):
    return self.points

class Coordinate3():
  def __init__(self, data):
    self.points = data
  def __repr__(self):
    return "[Coordinate3: %s]" % (str(self.points))

  def getPoints(self):
    return self.points

class IndexedFaceSet():
  def __init__(self, coordData, normData, textureData):
    def splitIntoFaces(data):
      """split data to faces, each separated by -1"""
      faces = [[]]
      for point in data:
        if point >= 0:
          faces[-1].append(int(point))
        else:
          faces.append([])
      return filter(lambda x: x, faces) # filter out any empty lists

    self.cFaces = splitIntoFaces(coordData) if coordData is not None else None
    self.nFaces = splitIntoFaces(normData) if normData is not None else None
    self.tFaces = splitIntoFaces(textureData) if textureData is not None else None
  def __repr__(self):
    return "[IndexedFaceSet: cFaces: %s, nFaces: %s, tFaces: %s]" % (str(self.cFaces), str(self.nFaces), str(self.tFaces))
  def getCFaces(self):
    return self.cFaces
  def getNFaces(self):
    return self.nFaces
  def getTFaces(self):
    return self.tFaces

class Material():
  def __init__(self, aColor, dColor, sColor, shininess):
    self.aColor = verifyColor(aColor)
    self.dColor = verifyColor(dColor)
    self.sColor = verifyColor(sColor)
    self.shininess = shininess
  def __repr__(self):
    return "[Material: aColor: %s, dColor: %s, sColor: %s, shininess: %s]" % \
        (self.aColor, self.dColor, self.sColor, self.shininess)

  def getSpecularColor(self):
    return self.sColor
  def getDiffuseColor(self):
    return self.dColor
  def getAmbientColor(self):
    return self.aColor
  def getShininess(self):
    return self.shininess

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
