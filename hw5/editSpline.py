from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import pickle
import numpy as np

def addVertices(v1, v2): return [v1[i] + v2[i] for i in range(len(v1))]
def multVertex(v, c): return map(lambda x: x * c, v)

class Nurbs():
  def __init__(self):
    self.knots = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
    self.vertices = [(-0.5, 0.5), (-0.5, -0.5), (0.5, -0.5), (0.5, 0.5)]
    self.du = 0.005
    self.k = 4

    self.lastCDB = None # last output from Cox de Boor
    self.curSelected = None
    self.control = True
    self.filename = 'output.p'

  def coxDeBoor(self):
    pts = []
    n = len(self.vertices)
    for u in np.arange(0, 1.0, self.du):
      # note: use 1-indexing so formulas are directly applicable
      N = np.zeros(n * (self.k+1)).reshape((n, self.k + 1))
      # base case: k = 0
      for i in range(n):
        N[i][1] = 1 if self.knots[i] <= u and u < self.knots[i+1] else 0
      # recursive cases: k
      for k in range(2, self.k+1):
        for i in range(n):
          num1 = (u - self.knots[i]) * N[i][k - 1]
          den1 = self.knots[i + k - 1] - self.knots[i]
          num2 = 0 if i + 1 >= n else ((self.knots[i + k] - u) * N[i + 1][k - 1])
          den2 = self.knots[i + k] - self.knots[i + 1]

          term1 = 0 if num1 == 0 and den1 == 0 else num1 / float(den1)
          term2 = 0 if num2 == 0 and den2 == 0 else num2 / float(den2)

          N[i][k] = term1 + term2
      assert all(map(lambda x: x >= 0, N.tolist()))
      # calculate the spline of order k
      pt = (0,0)
      for i in range(n):
        pt = addVertices(pt, multVertex(self.vertices[i], N[i][self.k]))
      pts.append((u, pt))
    self.lastCDB = pts
    return pts
  def updateVert(self, x, y):
    self.vertices[self.curSelected] = (x, y)
  def insertKnotCP(self, newKnot):
    """ Inserts a new knot and control point in the appropriate location. """
    assert self.knots[0] <= newKnot

    newKnotLoc = None
    # add new knot in the correct location
    for i in range(len(self.knots)):
      if self.knots[i] >= newKnot:
        self.knots.insert(i, newKnot)
        newKnotLoc = i
        break
    assert newKnotLoc is not None

    # update control points
    oldCP = self.vertices[:]
    self.vertices = []

    n = len(self.knots) - self.k - 1

    # calculate coefficients
    a = np.zeros(n+1)
    for i in range(1,n+1):
      if i <= newKnotLoc - self.k:
        a[i] = 1
      elif i <= newKnotLoc:
        a[i] = (newKnot - self.knots[i]) / (self.knots[i + self.k] - self.knots[i])
      else:
        a[i] = 0

    # calculate points
    self.vertices.append(oldCP[0])
    for i in range(1,n):
      term1 = multVertex(oldCP[i - 1], (1 - a[i]))
      term2 = multVertex(oldCP[i], a[i])
      self.vertices.append(addVertices(term1, term2))
    self.vertices.append(oldCP[n-1])

def redraw():
  """
  This function gets called every time the window needs to be updated
  i.e. after being hidden by another window and brought back into view,
  or when the window's been resized.
  You should never call this directly, but use glutPostRedisply() to tell
  GLUT to do it instead.
  """
  def drawSpline():
    upts = NURBS.coxDeBoor()
    pts = map(lambda x: x[1], upts)

    glLineWidth(2)

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointerf(pts)
    glDrawArrays(GL_LINE_STRIP, 0, len(pts))
    glDisableClientState(GL_VERTEX_ARRAY)

    glLineWidth(1)
  def drawControlPoints():
    glColor3f(0.5, 0.0, 1.0)

    # draw control points as small squares
    for (x,y) in NURBS.vertices:
      glEnableClientState(GL_VERTEX_ARRAY)
      verts = [(x-wid, y-wid), (x-wid, y+wid), (x+wid, y+wid), (x+wid, y-wid)]
      glVertexPointerf(verts)
      glDrawArrays(GL_QUADS, 0, len(verts))
      glDisableClientState(GL_VERTEX_ARRAY)
    # connect control points with thin lines
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointerf(NURBS.vertices)
    glDrawArrays(GL_LINE_STRIP, 0, len(NURBS.vertices))
    glDisableClientState(GL_VERTEX_ARRAY)

    glColor3f(1.0, 1.0, 1.0)

  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  drawSpline()
  if NURBS.control: drawControlPoints()

  glutSwapBuffers()

def resize(w, h):
  """
  GLUT calls this function when the windows is resized.
  All we do here is change the OpenGL viewport so it will always draw in the
  largest square that can fit the window.
  """
  if h == 0:
    h = 1

  # ensuring our windows is a square
  if w > h:
    w = h
  else:
    h = w

  # reset the current viewport and perspective transformation
  glViewport(0, 0, w, h)

  # TODO: FIX RESIZING!
  global xRes, yRes
  xRes = w
  yRes = h

  # tell GLUT to call the redrawing function, in this case redraw()
  glutPostRedisplay()

def pixelToCoord(x, y):
  cx = (2.0 * x / float(xRes)) - 1
  cy = -((2.0 * y / float(yRes)) - 1)
  return (cx, cy)

def keyfunc(key, x, y):
  if key == 27 or key == 'q' or key == 'Q':
    exit(0)
  elif key == 'c' or key == 'C':
    NURBS.control = not NURBS.control
    if not NURBS.control:
      NURBS.curSelected = None
    glutPostRedisplay()
  elif key == 'e' or key == 'E':
    pickle.dump(NURBS, open(NURBS.filename, "wb"))
    print "NURBS state exported as \"%s\"." % (NURBS.filename)

def mousefunc(button, state, x, y):
  def dist(pt1, pt2):
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)
  def trySelectControlPoint():
    """ Checks if a user clicked on a control point. If so, then select it."""
    nx, ny = pixelToCoord(x, y)
    # check control points to see if one was clicked
    for i, (vx, vy) in enumerate(NURBS.vertices):
      if abs(nx - vx) < 1.25*wid and abs(ny - vy) < 1.25*wid:
        NURBS.curSelected = i
  def findKnotValue():
    """ Finds the value of a new knot. Assumes the user clicked "near" a curve,
        and therefore finds the point on the curve that is closest to the click. Uses
        this u value to approximate the value of the new knot."""
    closestU = None
    closestDist = None
    for (u,pt) in NURBS.lastCDB:
      dst = dist(pixelToCoord(x,y),pt)
      if closestDist is None or dst < closestDist:
        closestU = u
        closestDist = dst
    return closestU

  # If disable control point manipulation, then return.
  if not NURBS.control: return

  if state == GLUT_DOWN:
    if button == GLUT_LEFT_BUTTON:
      trySelectControlPoint()
    elif button == GLUT_RIGHT_BUTTON:
      newKnot = findKnotValue()
      NURBS.insertKnotCP(newKnot)
      glutPostRedisplay()

  elif state == GLUT_UP:
    NURBS.curSelected = None

def motionfunc(x, y):
  if NURBS.curSelected is not None:
    nx, ny = pixelToCoord(x, y)
    NURBS.updateVert(nx, ny)

    glutPostRedisplay()

def startOpenGL():
  """
  Main entrance point
  Sets up some stuff then passes control to glutMainLoop() which never
  returns.
  """
  glutInit(sys.argv)

  # Get a double-buffered, depth-buffer-enabled window, with an
  # alpha channel.
  glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

  glutInitWindowSize(xRes, yRes)

  glutCreateWindow("CS171 HW5")

  # set up GLUT callbacks.
  glutDisplayFunc(redraw)
  glutReshapeFunc(resize)
  glutKeyboardFunc(keyfunc)
  glutMouseFunc(mousefunc)
  glutMotionFunc(motionfunc)

  glutMainLoop()

  return 1

if __name__=='__main__':
  # read and parse commandline arguments
  global NURBS
  if len(sys.argv) == 3:
    NURBS = Nurbs()
  elif len(sys.argv) == 4:
    # try to load file. If it doesn't exist, then we'll make it after exporting.
    try:
      NURBS = pickle.load(open(sys.argv[3], "rb"))
    except IOError:
      NURBS = Nurbs()
      NURBS.filename = sys.argv[3]
  else:
    print "Error: Incorrect number of parameters. Please call using:"
    print "\t$ python editSpline.py xRes yRes [<spline-file>]"
    exit(-1)

  global xRes, yRes
  xRes, yRes = map(int, sys.argv[1:3])

  # control point width
  global wid
  wid = min(xRes, yRes) / 25000.0

  startOpenGL()
