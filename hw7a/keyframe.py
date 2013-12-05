from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import parseKeyFrameScript
from catmullRomSpline import CRSpline
import sys
import math
import time

class UserInterface():
  def __init__(self):
    self.zoom = 0
    self.rotate = 0
    self.isPlay = True
    self.loopEnabled = True

    self.textInput = None

  def getTextInputString(self):
    return ''.join(self.textInput)
  def getTextInputInt(self):
    return int(self.getTextInputString()) if len(self.textInput) > 0 else 0

  def zoomIn(self):
    self.zoom += 0.1
  def zoomOut(self):
    self.zoom -= 0.1
  def getZoom(self):
    return self.zoom

  def rotateRight(self):
    self.rotate += 0.1
  def rotateLeft(self):
    self.rotate -= 0.1
  def getRotate(self):
    return self.rotate

  def setPlay(self, bool):
    self.isPlay = bool
  def shouldPlay(self):
    return self.isPlay

  def toggleLoop(self):
    self.loopEnabled = not self.loopEnabled
  def shouldLoop(self):
    return self.loopEnabled

def redraw():
  """
  This function gets called every time the window needs to be updated
  i.e. after being hidden by another window and brought back into view,
  or when the window's been resized.
  You should never call this directly, but use glutPostRedisply() to tell
  GLUT to do it instead.
  """
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  quadric = gluNewQuadric()

  radius = 0.15
  height = 3

  # note: arbitrarily chose parameters such that animation fit in frame
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  glFrustum(
      -6,
      6,
      -6,
      6,
      1,
      10)

  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()
  gluLookAt(-5, 0, 5,
      crSpline.translationData[0][0],
      crSpline.translationData[0][1],
      crSpline.translationData[0][2],
      1, userInterface.rotate, 1)

  glPushMatrix()

  ## PERFORM FRAME TRANSFORMATIONS ##
  glTranslatef(*(crSpline.translationData[fr]))
  rotate = crSpline.rotationData[fr]
  glRotatef(
      rotate[3],
      rotate[0],
      rotate[1],
      rotate[2])
  glScalef(*(crSpline.scaleData[fr]))

  ## DRAW I-bar ##
  # middle part of I
  glColor3f(1, 0, 0)
  glPushMatrix()
  gluCylinder(quadric, radius, radius, height, 100, 100)
  glPopMatrix()

  # bottom of I
  glPushMatrix()
  glColor3f(0, 1, 0)
  glRotate(90, 1, 0, 0)
  gluCylinder(quadric, radius, radius, height / 2, 100, 100)
  glColor3f(0, 0.5, 1)
  glRotate(180, 1, 0, 0)
  gluCylinder(quadric, radius, radius, height / 2, 100, 100)
  glPopMatrix()

  # top of I
  glPushMatrix()
  glColor3f(1, 1, 1)
  glRotate(90, 1, 0, 0)
  glTranslate(0, height, 0)
  gluCylinder(quadric, radius, radius, height / 2, 100, 100)
  glColor3f(0.5, 1, 0.5)
  glRotate(180, 1, 0, 0)
  gluCylinder(quadric, radius, radius, height / 2, 100, 100)
  glPopMatrix()
  ## END DRAW I-bar ##

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
  global fr

  ## Parse text input for frame jumping... ##
  if userInterface.textInput is not None:
    changedFrame = False
    if key.isdigit() and int(key) >= 0 and int(key) <= 9:
      userInterface.textInput.append(key)
    elif key == '\x7F' or key == '\x08':
      userInterface.textInput = userInterface.textInput[:-1]
    else:
      if key == '\x0D' and len(userInterface.textInput) > 0:
        frame = userInterface.getTextInputInt()
        if frame < keyFrame.total_num:
          changedFrame = True
          fr = frame
          glutPostRedisplay()

      userInterface.setPlay(True)
      userInterface.textInput = None

    # update terminal output to reflect text input thus far
    if userInterface.textInput is not None:
      sys.stdout.write("...Jump to frame: %-10s (enter to jump)\r" % (userInterface.getTextInputString()))
      sys.stdout.flush()
    elif changedFrame:
      sys.stdout.write("Jumped to frame %-30s\n" % (fr))
      sys.stdout.flush()
    else:
      sys.stdout.write("Jumping to frame cancelled. Continuing from frame %-10s\n" % (fr))
      sys.stdout.flush()

    return

  ## Parse other input... ##
  if key == 27 or key == 'q' or key == 'Q':
    exit(0)
  elif key == 'p' or key == 'P':
    userInterface.setPlay(True)
  elif key == 's' or key == 'S':
    userInterface.setPlay(False)
  elif key == 'l' or key == 'L':
    userInterface.toggleLoop()
  elif key == 'f' or key == 'F':
    if fr < keyFrame.total_num - 1:
      fr += 1
    elif userInterface.shouldLoop():
      fr = 0
    glutPostRedisplay()
  elif key == 'r' or key == 'R':
    if fr > 0:
      fr -= 1
    elif userInterface.shouldLoop():
      fr = keyFrame.total_num - 1
    glutPostRedisplay()
  elif key == 0 or key == '0':
    fr = 0
    glutPostRedisplay()
  elif key == 'j' or key == 'J':
    userInterface.textInput = []
    userInterface.setPlay(False)

    print
    print "Enter the frame number you would like to jump to!"
    print "Type the number directly into the OpenGL window, and press enter to submit."
    print "Note: Valid frame numbers are 0-%d" % (keyFrame.total_num - 1)
    print

def idlefunc():
  """For each iteration, increment counter and re-render (for waves update)."""
  if not userInterface.shouldPlay():
    return

  time.sleep(0.15)

  global fr
  if fr == keyFrame.total_num - 1:
    if userInterface.shouldLoop():
      fr = 0
  else:
    fr += 1

  glutPostRedisplay()

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

  glutCreateWindow("CS171 HW7a")

  initGL()

  # initialize UserInterface to handle mouse/keyboard transformations
  global userInterface
  userInterface = UserInterface()

  # set up GLUT callbacks.
  glutDisplayFunc(redraw)
  glutReshapeFunc(resize)
  glutKeyboardFunc(keyfunc)
  glutIdleFunc(idlefunc)

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

  global crSpline
  crSpline = CRSpline(keyFrame.total_num, keyFrame.frames)

  global fr
  fr = 0

  global xRes, yRes
  xRes, yRes = (500, 500)

  startOpenGL()
