from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import parseKeyFrameScript
import sys
import math

class Modifier():
  NONE, PAN, ZOOM, ROTATE = range(4)

class UserInterface():
  def __init__(self):
    self.type = Modifier.NONE
    self.shade = True
    self.prevX = None
    self.prevY = None

    self.panX = 0
    self.panY = 0
    self.zoom = 0
    self.rotateX = 0
    self.rotateY = 0

  def setShade(self, val):
    self.shade = val
  def shouldShade(self):
    return self.shade

  def setZoom(self, x, y):
    self.type = Modifier.ZOOM
    self.prevX = x
    self.prevY = y
  def setPan(self, x, y):
    self.type = Modifier.PAN
    self.prevX = x
    self.prevY = y
  def setRotate(self, x, y):
    self.type = Modifier.ROTATE
    self.prevX = x
    self.prevY = y
  def unset(self):
    self.type = Modifier.NONE

  def update(self, x, y):
    if self.type == Modifier.PAN:
      self.panX += x - self.prevX
      self.panY += y - self.prevY
    elif self.type == Modifier.ZOOM:
      self.zoom += y - self.prevY
    elif self.type == Modifier.ROTATE:
      self.rotateX += x - self.prevX
      self.rotateY += y - self.prevY
    self.prevX = x
    self.prevY = y

  def getPan(self):
    return (self.panX / float(xRes), -1 * self.panY / float(yRes))
  def getZoom(self):
    return -1 * self.zoom / float(yRes)
  def getRotate(self):
    """Returns thetaX, thetaY: the angle of rotation for x and y axes.
    Note: swap components because rotation should be perpendicular to drag line."""
    thetaX = self.rotateX / float(xRes)
    thetaY = self.rotateY / float(yRes)
    return (thetaY, thetaX)

def toDeg(x): return 360.0 * x / (2 * math.pi)

def redraw():
  """
  This function gets called every time the window needs to be updated
  i.e. after being hidden by another window and brought back into view,
  or when the window's been resized.
  You should never call this directly, but use glutPostRedisply() to tell
  GLUT to do it instead.
  """
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  # Load identity matrix for GL_MODELVIEW
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()

  # Get any changes due to mouse motion
  panX, panY = userInterface.getPan()
  zoom = userInterface.getZoom()
  glTranslatef( panX, panY, zoom)

  # set up world-space to camera (C) matrix
  camera = openInventor.getPerspectiveCamera()
  glRotatef(
      -1 * toDeg(camera.orien[3]),
      camera.orien[0],
      camera.orien[1],
      camera.orien[2])
  glTranslatef(
      -1 * camera.pos[0],
      -1 * camera.pos[1],
      -1 * camera.pos[2])

  # perform any rotations due to mouse motion
  rotateX, rotateY = userInterface.getRotate()
  glRotatef(toDeg(rotateX), 1.0, 0.0, 0.0)
  glRotatef(toDeg(rotateY), 0.0, 1.0, 0.0)

  for separator in openInventor.getSeparators():
    glPushMatrix()

    # set material parameters
    initMaterial(separator.getMaterial())

    # set up camera space to NDC space transforms
    for transform in separator.getTransforms():
      if transform.translation:
        glTranslatef(*transform.translation.data)
      if transform.rotation:
        glRotatef(
            toDeg(transform.rotation.data[3]),
            transform.rotation.data[0],
            transform.rotation.data[1],
            transform.rotation.data[2])
      if transform.scaleFactor:
        glScalef(*transform.scaleFactor.data)

    for polygon in separator.getPolygons():
      points, normals = zip(*polygon)

      # draw polygon
      glEnableClientState(GL_VERTEX_ARRAY)
      glEnableClientState(GL_NORMAL_ARRAY)
      glVertexPointerf(points)
      glNormalPointerf(normals)
      if userInterface.shouldShade():
        glDrawArrays(GL_POLYGON, 0, len(points))
      else:
        glDrawArrays(GL_LINE_LOOP, 0, len(points))
      glDisableClientState(GL_NORMAL_ARRAY)
      glDisableClientState(GL_VERTEX_ARRAY)

    glPopMatrix()

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

  # tell GLUT to call the redrawing function, in this case redraw()
  glutPostRedisplay()

def keyfunc(key, x, y):
  """
  GLUT calls this function when a key is pressed.
  """
  if key == 27 or key == 'q' or key == 'Q':
    exit(0)
  elif key == 'w' or key == 'W':
    userInterface.setShade(False)
    glutPostRedisplay()
  elif key == 'g' or key == 'G':
    userInterface.setShade(True)
    glShadeModel(GL_SMOOTH)
    glutPostRedisplay()
  elif key == 'f' or key == 'F':
    userInterface.setShade(True)
    glShadeModel(GL_FLAT)
    glutPostRedisplay()

def mousefunc(button, state, x, y):
  holdingShift = glutGetModifiers() == GLUT_ACTIVE_SHIFT
  if state == GLUT_UP:
    userInterface.unset()
  elif state == GLUT_DOWN:
    if button == GLUT_MIDDLE_BUTTON and holdingShift:
      userInterface.setZoom(x, y)
    elif button == GLUT_MIDDLE_BUTTON and not holdingShift:
      userInterface.setPan(x, y)
    elif button == GLUT_LEFT_BUTTON:
      userInterface.setRotate(x, y)

def motionfunc(x, y):
  userInterface.update(x, y)

  glutPostRedisplay()

def initLights():
  """
  Sets up an OpenGL light.  This only needs to be called once
  and the light will be used during all renders.
  """
  assert len(openInventor.getPointLights()) < GL_MAX_LIGHTS

  # set up lights
  for i, light in enumerate(openInventor.getPointLights()):
    glLightNum = GL_LIGHT0 + i

    amb = [ 0.0, 0.0, 0.0, 1.0 ]
    diff = light.getColor() + [ 1.0 ]
    spec = light.getColor() + [ 1.0 ]
    lightPos = light.getLocation() + [ 1.0 ]

    glLightfv(glLightNum + i, GL_AMBIENT, amb)
    glLightfv(glLightNum + i, GL_DIFFUSE, diff)
    glLightfv(glLightNum + i, GL_SPECULAR, spec)
    glLightfv(glLightNum + i, GL_POSITION, lightPos)
    glEnable(glLightNum + i)

  # turn on lights
  glEnable(GL_LIGHTING);

def initMaterial(material):
  """
  Sets the OpenGL material state.  This is remembered so we only need to
  do this once.
  """
  emit = [0.0, 0.0, 0.0, 1.0]
  amb  = material.getAmbientColor() + [ 1.0 ] #[0.0, 0.0, 0.0, 1.0]
  diff = material.getDiffuseColor() + [ 1.0 ] #[0.0, 0.0, 1.0, 1.0]
  spec = material.getSpecularColor() + [ 1.0 ] #[1.0, 1.0, 1.0, 1.0]
  shiny = material.getShininess() #20.0

  glMaterialfv(GL_FRONT, GL_AMBIENT, amb)
  glMaterialfv(GL_FRONT, GL_DIFFUSE, diff)
  glMaterialfv(GL_FRONT, GL_SPECULAR, spec)
  glMaterialfv(GL_FRONT, GL_EMISSION, emit)
  glMaterialf(GL_FRONT, GL_SHININESS, shiny)

def initGL():
  """
  Set up OpenGL state.  This does everything so when we draw we only need to
  actually draw the object, and OpenGL remembers all of our other settings.
  """
  # Tell openGL to use Gouraud shading:
  glShadeModel(GL_SMOOTH)

  # Enable back-face culling:
  glEnable(GL_CULL_FACE)
  glCullFace(GL_BACK)

  # Enable depth-buffer test.
  glEnable(GL_DEPTH_TEST)

  camera = openInventor.getPerspectiveCamera()
  # set up perspective (P) matrix
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  glFrustum( # multiplies current matrix by perspective matrix
      camera.left,
      camera.right,
      camera.bottom,
      camera.top,
      camera.nearD,
      camera.farD)

  # set light parameters
  initLights()

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

  glutCreateWindow("CS171 HW4")

  initGL()

  # initialize UserInterface to handle mouse/keyboard transformations
  global userInterface
  userInterface = UserInterface()

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
  if len(sys.argv) != 1:
    print "Error: Incorrect number of parameters. Please call using:"
    print "\t$ python keyframe.py < <script-file-name>"
    exit(-1)

  # read and parse the OpenInventor file
  data = ''.join(sys.stdin)
  global keyFrame
  keyFrame = parseKeyFrameScript.parse(data)

  print keyFrame

  #startOpenGL()
