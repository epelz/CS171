# Eric Pelz
# CS 171: Introduction to Computer Graphics

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc
import parseOpenInventor
from matrix import MatrixExtended
import sys

def calculatePolygonsFromData(openInventor):
  def calculateMatrixTransform(separator):
    transforms = separator.getTransforms()
    transformProducts = map(lambda transform: transform.multiplyTransformBlock(), transforms)
    transformProducts.reverse()
    return reduce(lambda y,x: x*y, transformProducts)

  # Calculate each matrix transform
  Ci = openInventor.getPerspectiveCamera().getCameraTransformInverse()
  P = openInventor.getPerspectiveCamera().getPerspectiveProjection()

  transformedPolygons = []
  # For each seperator, get polygons and multiply against matrix transforms
  for separator in openInventor.getSeparators():
    O = calculateMatrixTransform(separator)
    # For each polygon, multiply against the matrix transforms
    polygons = separator.getPolygons()
    for polygon in polygons:
      transformedPolygons.append([])
      for point in polygon:
        pointVec = MatrixExtended.getVector(point + [1.0])
        newPoint = P.mult(Ci.mult(O.mult(pointVec)))
        w = newPoint.tolist()[3][0]
        newPoint /= w
        transformedPolygons[-1].append(map(lambda x: x[0],newPoint.tolist()[:2]))
  return transformedPolygons

def matchPointPairs(listOfPoints):
  '''Given a list of points, return pairs of points which connect them together.'''
  lines = []
  for points in listOfPoints:
    lastPoint = None
    firstPoint = None
    for point in points:
      if lastPoint:
        lines += [(lastPoint, point)]
      else:
        firstPoint = point
      lastPoint = point
    lines += [(lastPoint, firstPoint)]
  return lines

def drawLinesToNewCanvas(xMin, xMax, yMin, yMax, xRes, yRes, lineSegments):
  '''Given a grid, line segments, and target image size, returns a matrix of pixel data.'''
  def pointToPixel(x, y):
    '''Converts a point to its location in the pixel space.'''
    xScaling = xRes/(xMax-xMin)
    yScaling = yRes/(yMax-yMin)
    newX = (x - xMin) * xScaling
    newY = (y - yMin) * yScaling
    # rotate by 90 degrees (TODO: Why is this necessary?)
    newX, newY = yRes - newY, newX
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
  # read and parse commandline arguments
  if len(sys.argv) != 3:
    print "Error: Incorrect number of parameters. Please call using:"
    print "\t$ python wireframe.py xRes yRes < input.iv"
    exit(-1)
  xRes, yRes = map(int, sys.argv[1:3])

  # read and parse the OpenInventor file
  data = ''.join(sys.stdin)
  openInventor = parseOpenInventor.parse(data)

  transformedPolygons = calculatePolygonsFromData(openInventor)
  lineSegments = matchPointPairs(transformedPolygons)
  pixelMatrix = drawLinesToNewCanvas(-1, 1, -1, 1, xRes, yRes, lineSegments)

  printPPMFormat(xRes, yRes, pixelMatrix)
