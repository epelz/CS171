from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import parseOpenInventor
import sys
import math
import pygame
from matrix import MatrixExtended

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
    if separator.hasMaterial():
      initMaterial(separator.getMaterial())
    else:
      glEnable(GL_TEXTURE_2D)
      tex = initTexture(separator.getTexture2Path())

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
      points, points2 = zip(*polygon)
      # Note: points2 is normals if material, or is textures otherwise

      # if material, then draw shaded
      if separator.hasMaterial():
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointerf(points)
        glNormalPointerf(points2)
        if userInterface.shouldShade():
          glDrawArrays(GL_POLYGON, 0, len(points))
        else:
          glDrawArrays(GL_LINE_LOOP, 0, len(points))
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
      # if no material, then use textures
      else:
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glVertexPointerf(points)
        glTexCoordPointer(2, GL_FLOAT, 0, points2)
        glDrawArrays(GL_POLYGON, 0, len(points))
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    glPopMatrix()

  genWaves()

  glutSwapBuffers()

def genWaves():
  """ Generates and renders water waves which reflect a texture. """
  def f(x, y, phi):
    """ Height function for a given point (x, y) with phase shift phi.
    H = beta * cos(alpha * (x^2 + y^2) - phi)
      = beta * cos(alpha * r^2 - phi)
    """
    return beta * math.cos(alpha * (x ** 2 + y ** 2) - phi)
  def N(x, y, phi):
    """ Returns the normal vector for a given (x,y) with phase shift phi.
    Analytically, this is simply the normal vector which is perpendicular
    to both (x and y) tangent vectors of the height function. """
    vec = MatrixExtended.getVector([
        2 * alpha * beta * x * math.sin( alpha * (x ** 2 + y ** 2) - phi),
        2 * alpha * beta * y * math.sin( alpha * (x ** 2 + y ** 2) - phi),
        1])
    return vec.getVectorUnit().getVectorList()
  def expression(xi,yi):
    """For a given x and y index, return its corresponding point and normal."""
    x = xi * delta
    y = yi * delta
    phi = (w * it)
    # note: flip x and y so that on floor of space
    return ([x, -1.5 + 0.15 * f(x, y, phi), -y], N(x, y, phi))
#    return ([x, y, -1.5 + 0.05 * f(x, y, phi)], N(x, y, phi))

  ## wave constants
  radiusSize = 2          # maximum wave radius size
  delta = 0.15            # size of triangles to render
  alpha = 2 * math.pi / 2 # alpha parameter in height function
  beta = 0.15             # beta parameter in height function
  w = 1                   # coefficient to phase shift in height function

  ## split the maximum radius into multiple parts, and generate corresponding
  ## points and normal vectors.
  numParts = int(radiusSize / delta)
  waveDict = dict([((xi,yi), expression(xi, yi))
                for xi in range(-numParts, numParts + 1)
                for yi in range(-numParts, numParts + 1)])
  ## based on these points and normal vectors, split into renderable triangles
  # note: using triangles rather than polygons because they're more efficient
  triangles = []
  for xi in range(-numParts, numParts):
    for yi in range(-numParts, numParts):
      triangles.append(
          [waveDict[(xi, yi)],
           waveDict[(xi+1, yi)],
           waveDict[(xi+1, yi+1)]])
      triangles.append(
          [waveDict[(xi, yi)],
           waveDict[(xi+1, yi+1)],
           waveDict[(xi, yi+1)]])

  ## initialize the texture and render the waves
  glPushMatrix()
  tex = initTexture('sky.png')

  glEnable(GL_TEXTURE_GEN_S)
  glEnable(GL_TEXTURE_GEN_T)
  glBindTexture(GL_TEXTURE_2D, tex)

  for triangle in triangles:
    points, normals = zip(*triangle)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glVertexPointerf(points)
    glNormalPointerf(normals)
    glDrawArrays(GL_TRIANGLES, 0, len(points))
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)

  glDisable(GL_TEXTURE_GEN_S)
  glDisable(GL_TEXTURE_GEN_T)

  glPopMatrix()

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

def idlefunc():
  """For each iteration, increment counter and re-render (for waves update)."""
  global it
  it += 1

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

def initTexture(imagePath):
  """
  Sets the OpenGL texture state. Returns the texture so can use later.
  """
  texture = pygame.image.load(imagePath)
  textureData = pygame.image.tostring(texture, "RGBA", 1)
  tWidth = texture.get_width()
  tHeight = texture.get_height()

  glTex = glGenTextures(1)
  glBindTexture(GL_TEXTURE_2D, glTex)
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tWidth, tHeight, 0, GL_RGBA,
      GL_UNSIGNED_BYTE, textureData)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
  glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
  glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)

  return glTex


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
  if openInventor.hasLights():
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

  glutCreateWindow("CS171 HW6")

  initGL()

  # initialize UserInterface to handle mouse/keyboard transformations
  global userInterface
  userInterface = UserInterface()

  # track number of iterations that have gone by, for wave rendering
  global it
  it = 0

  # set up GLUT callbacks.
  glutDisplayFunc(redraw)
  glutReshapeFunc(resize)
  glutKeyboardFunc(keyfunc)
  glutMouseFunc(mousefunc)
  glutMotionFunc(motionfunc)
  glutIdleFunc(idlefunc)

  glutMainLoop()

  return 1

if __name__=='__main__':
  # read and parse commandline arguments
  if len(sys.argv) != 3:
    print "Error: Incorrect number of parameters. Please call using:"
    print "\t$ python oglRenderer.py xRes yRes < input.iv"
    exit(-1)
  global xRes, yRes
  xRes, yRes = map(int, sys.argv[1:3])

  # read and parse the OpenInventor file
  data = ''.join(sys.stdin)
  global openInventor
  openInventor = parseOpenInventor.parse(data)

  startOpenGL()
