# Eric Pelz
# CS 171: Introduction to Computer Graphics

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc
import parseOpenInventor
import lighting
from matrix import MatrixExtended
import itertools
import sys

class Polygon():
  def __init__(self, separator, vertices):
    self.separator = separator
    self.vertices = vertices
  def getSeparator(self):
    return self.separator
  def getVertices(self):
    return self.vertices

class Vertex():
  def __init__(self, point, transformedPoint, normal, color=None):
    self.point = point #world space
    self.transformedPoint = transformedPoint
    self.normal = normal
    self.color = color
  def getPt(self):
    return self.point
  def getTransformedPt(self):
    return self.transformedPoint
  def getNormal(self):
    return self.normal
  def getColor(self):
    return self.color
  def setColorReturn(self, color):
    self.color = color
    return self

def calculatePolygonsFromData(openInventor):
  """Given OpenInventor data, return list of Polygon objects."""
  def calculateCMatrixTransform(separator):
    transforms = separator.getTransforms()
    transformProducts = map(lambda transform: transform.multiplyTransformBlock(), transforms)
    transformProducts.reverse()
    return reduce(lambda y,x: x*y, transformProducts)
  def calculateNMatrixTransform(separator):
    transforms = separator.getTransforms()
    transformProducts = map(lambda transform: transform.multiplyNormalTransform(), transforms)
    transformProducts.reverse()
    return reduce(lambda y,x: x*y, transformProducts)

  # Calculate camera and perspective matrix transforms
  Ci = openInventor.getPerspectiveCamera().getCameraTransformInverse()
  P = openInventor.getPerspectiveCamera().getPerspectiveProjection()

  finalPolygons = []
  # For each seperator, get polygons and multiply against matrix transforms
  for separator in openInventor.getSeparators():
    CO = calculateCMatrixTransform(separator)
    NO = calculateNMatrixTransform(separator)

    # For each polygon, multiply against the matrix transforms and store
    polygons = separator.getPolygons()
    for polygon in polygons:
      vertices = []
      for cPoint, nPoint in polygon:
        # transform point (to world space and NDC space)
        pointVec = MatrixExtended.getVector(cPoint + [1.0])
        pointWorldSpace = CO.mult(pointVec)
        pointTransformed = P.mult(Ci.mult(pointWorldSpace))
        pointTransformed /= pointTransformed.getVectorComponent(3)

        # transform normal
        normalVec = MatrixExtended.getVector(nPoint + [1.0])
        normalTransformed = NO.mult(normalVec)[0:3]
        normalTransformed /= normalTransformed.getVectorNorm()

        # instantiate into a Vertex object
        vertices.append(Vertex(
          pointWorldSpace[0:3],
          pointTransformed[0:3],
          normalTransformed))
      # instantiate into a Polygon object
      finalPolygons.append(Polygon(separator, vertices))
  return finalPolygons

def splitIntoTriangles(polygons):
  """Given a list of polygons, returns triples of points (triangles) to encompass each polygon."""
  def concatList(lst):
    return sum(lst, [])
  def getTriples(polygon):
    pts = polygon.getVertices()
    sep = polygon.getSeparator()

    # split into combinations of three points, and instantiate Polygon objects
    ptss = list(itertools.combinations(pts, 3))
    return map(lambda pts: Polygon(sep, pts), ptss)

  return concatList(map(getTriples, polygons))

def colorTriangles(triangles, openInventor, n):
  """Given a list of triangles (Polygons), returns the triangles with appropriate coloring values."""
  def averageComponents(a, b, c):
    avgs = []
    for i in range(0, len(a)):
      avgs.append((a[i][0] + b[i][0] + c[i][0]) / 3.0)
    return MatrixExtended.getVector(avgs)

  coloredTriangles = []

  if n == 0: # flat shading
    for polygon in triangles:
      vertices = polygon.getVertices()
      separator = polygon.getSeparator()

      # average position and normal for each vertex
      avgVertex = averageComponents(*map(lambda v: v.getPt().tolist(), vertices))
      avgNormal = averageComponents(*map(lambda v: v.getNormal().tolist(), vertices))

      rgb = lighting.calculateLighting(
          avgNormal,
          avgVertex,
          separator.getMaterial(),
          openInventor.getPointLights(),
          MatrixExtended.getVector(openInventor.getPerspectiveCamera().getCameraPosition())
        )
      coloredTriangles.append(map(lambda v: v.setColorReturn(rgb), vertices))
  return coloredTriangles

def drawToNewCanvas(xMin, xMax, yMin, yMax, xRes, yRes, triangles):
  """Given a grid, line segments, and target image size, returns a matrix of pixel data."""
  def pointToPixel(x, y):
    """Converts a point to its location in the pixel space."""
    xScaling = xRes/(xMax-xMin)
    yScaling = yRes/(yMax-yMin)
    newX = (x - xMin) * xScaling
    newY = (y - yMin) * yScaling
    newX, newY = yRes - newY, newX # rotate by 90 degrees (TODO: Why?)
    return (int(newX), int(newY))
  def shouldDrawPolygon(v0, v1, v2):
    """Uses backface culling to determine whether to draw a polygon."""
    normal = (v2 - v1).crossVector(v0 - v1)
    return normal.getVectorComponent(2) > 0
  def raster(verts, outMatrix, zBufferMatrix):
    """Base raster function taken from cs171 website.
    Takes three vertices in arbitrary order, with each
    vertex consisting of an x and y value in the first two data positions, and
    any arbitrary amount of extra data, and calls the passed in function on
    every resulting pixel, with all data values magically interpolated."""
    def f(vert0, vert1, x, y):
      """Helper function f as defined in course text."""
      x0 = vert0[0]
      y0 = vert0[1]
      x1 = vert1[0]
      y1 = vert1[1]
      return float((y0 - y1) * x + (x1 - x0) * y + x0 * y1 - x1 * y0)
    def drawPixel(x, y, data):
      """Given a coordinate and data, draw the point.
      Checks the z-buffer matrix to see if we should indeed draw the point."""
      # ensure (x,y) in bounds
      if x >= 0 and x <= xRes and y >= 0 and y <= yRes:
        # check the z-buffer (use interpolated barycentric z-coordinate)
        if data[2] < zBufferMatrix[x][y]:
          zBufferMatrix[x][y] = data[2]
          outMatrix[x][y] = data[3].getVectorList()

    xMin = xRes + 1
    yMin = yRes + 1
    xMax = yMax = -1

    coords = [ pointToPixel(vert[0], vert[1]) for vert in verts ]

    # find the bounding box
    for c in coords:
      if c[0] < xMin: xMin = c[0]
      if c[1] < yMin: yMin = c[1]
      if c[0] > xMax: xMax = c[0]
      if c[1] > yMax: yMax = c[1]

    # normalizing values for the barycentric coordinates
    # not sure exactly what's going on here, so read the textbook
    fAlpha = f(coords[1], coords[2], coords[0][0], coords[0][1])
    fBeta = f(coords[2], coords[0], coords[1][0], coords[1][1])
    fGamma = f(coords[0], coords[1], coords[2][0], coords[2][1])

    if abs(fAlpha) < .0001 or abs(fBeta) < .0001 or abs(fGamma) < .0001:
      return

    # go over every pixel in the bounding box
    for y in range(max(yMin, 0), min(yMax, yRes)):
      for x in range(max(xMin, 0), min(xMax, xRes)):
        # calculate the pixel's barycentric coordinates
        alpha = f(coords[1], coords[2], x, y) / fAlpha
        beta = f(coords[2], coords[0], x, y) / fBeta
        gamma = f(coords[0], coords[1], x, y) / fGamma

        # if the coordinates are positive, do the next check
        if alpha >= 0 and beta >= 0 and gamma >= 0:
          data = []
          # interpolate the data
          for i in range(len(verts[0])):
            data.append(alpha * verts[0][i] + beta * verts[1][i] + gamma * verts[2][i])

          # and finally, draw the pixel
          if data[2] >= -1:
            drawPixel(x, y, data)

  # initialize new matrix of appropriate size
  pixelMatrix = [[None for _ in range(yRes)] for _ in range(xRes)]
  zBufferMatrix = [[float("infinity") for _ in range(yRes)] for _ in range(xRes)]

  # raster each triangle
  for triangle in triangles:
    vertices = map(lambda v: v.getTransformedPt(), triangle)
    if shouldDrawPolygon(*vertices): # if n_z > 0 (backface culling)
      verts = map(lambda v: v.getTransformedPt().getVectorList() + [v.getColor()], triangle)
      raster(verts, pixelMatrix, zBufferMatrix)

  return pixelMatrix

def printPPMFormat(xRes, yRes, pixelMatrix):
  print "P3"
  print xRes, yRes
  print "255"
  for pixelRow in pixelMatrix:
    for pixel in pixelRow:
      if pixel:
        # calculate the RGB values and assert that they are valid
        colors = map(lambda n: int(255 * n), pixel)
        assert all(map(lambda n: n >= 0 and n <= 255, colors))

        print " ".join(map(str, colors))
      else:
        print "0 0 0"

if __name__=='__main__':
  # read and parse commandline arguments
  if len(sys.argv) != 4:
    print "Error: Incorrect number of parameters. Please call using:"
    print "\t$ python shaded.py n xRes yRes < input.iv"
    exit(-1)
  n, xRes, yRes = map(int, sys.argv[1:4])

  # read and parse the OpenInventor file
  data = ''.join(sys.stdin)
  openInventor = parseOpenInventor.parse(data)

  polygons = calculatePolygonsFromData(openInventor)
  triangles = splitIntoTriangles(polygons)
  coloredTriangles = colorTriangles(triangles, openInventor, n)
  pixelMatrix = drawToNewCanvas(-1, 1, -1, 1, xRes, yRes, coloredTriangles)

  printPPMFormat(xRes, yRes, pixelMatrix)
