from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import parseOpenInventor
import sys
import math

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

  for separator in openInventor.getSeparators():
    glPushMatrix()

    # TODO: mouse translate and rotation

    # set material parameters
    initMaterial(separator.getMaterial())

    for polygon in separator.getPolygons():
      points, normals = zip(*polygon)

      glPushMatrix()

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

      # draw polygon
      glEnableClientState(GL_VERTEX_ARRAY)
      glEnableClientState(GL_NORMAL_ARRAY)
      glVertexPointerf(points)
      glNormalPointerf(normals)
      glDrawArrays(GL_POLYGON, 0, len(points))
      glDisableClientState(GL_NORMAL_ARRAY)
      glDisableClientState(GL_VERTEX_ARRAY)

      glPopMatrix()

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
  GLUT calls this function when a key is pressed. Here we just quit when ESC or
  'q' is pressed.
  """
  if key == 27 or key == 'q' or key == 'Q':
    exit(0)

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
  do this once.  If you want to use different materials, you'd need to do this
  before every different one you wanted to use.
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
  actually draw the sphere, and OpenGL remembers all of our other settings.
  """
  # Tell openGL to use Gouraud shading:
  glShadeModel(GL_SMOOTH)

  # Enable back-face culling:
  glEnable(GL_CULL_FACE)
  glCullFace(GL_BACK)

  # Enable depth-buffer test.
  glEnable(GL_DEPTH_TEST)

  # Set up projection and modelview matrices ("camera" settings)
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

  # set up world-space to camera (C) matrix
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()
  glTranslatef(*map(lambda x: x * -1, camera.pos)) #
  glRotatef(
      toDeg(camera.orien[3]),
      camera.orien[0],
      camera.orien[1],
      camera.orien[2])

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

  # set up GLUT callbacks.
  glutDisplayFunc(redraw)
  glutReshapeFunc(resize)
  glutKeyboardFunc(keyfunc)

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
