# Eric Pelz
# CS 171: Introduction to Computer Graphics

import numpy as np
import math

class MatrixExtended(np.matrix):
  """ An extended matrix class for use in CS171. Mostly the numpy matrix class,
      but some changes to help with the CS171 assignments. """
  def __new__(cls, data):
    """ Initialize as a numpy matrix, but cast to be our class type. """
    obj = np.matrix(data).view(cls)
    return obj

  def getInverse(self):
    return self.getI()
    #return np.linalg.inv(self)

  def getTranspose(self):
    return self.getT()

  def mult(self, mat2):
    return np.dot(self, mat2)

  def dotVector(self, vec2):
    # assumes vectors are of the form MatrixExtended([[1],[2],[3]])
    return sum([self[i][0] * vec2[i][0] for i in range(len(self))]).tolist()[0][0]

  def crossVector(self, vec2):
    # assumes vectors are of the form MatrixExtended([[1],[2],[3]])
    return MatrixExtended(np.cross(self.getTranspose(), vec2.getTranspose())).getTranspose()

  def multiplyVectorComponents(self, vec2):
    # assumes vectors are of the form MatrixExtended([[1],[2],[3]])
    return MatrixExtended.getVector(
        map(lambda (x,y): x[0]*y[0], zip(self.tolist(),vec2.tolist())))

  def getVectorComponent(self, i):
    # assumes vectors are of the form MatrixExtended([[1],[2],[3]])
    return self.tolist()[i][0]

  def getVectorNorm(self):
    # assumes vectors are of the form MatrixExtended([[1],[2],[3]])
    return sum(map(lambda x: x[0] ** 2, self.tolist())) ** 0.5

  def mapVector(self, f):
    # assumes vectors are of the form MatrixExtended([[1],[2],[3]])
    return MatrixExtended.getVector(map(lambda x: f(x[0]), self.tolist()))

  def getVectorList(self):
    # assumes vectors are of the form MatrixExtended([[1],[2],[3]])
    return map(lambda x: x[0], self.tolist())

  #---- Static functions to return new matrices ----
  @staticmethod
  def getVector(lstOfValues):
    """ A static method to return a vector with the given list of values. """
    return MatrixExtended([[v] for v in lstOfValues])

  @staticmethod
  def getTranslationMatrix(tx, ty, tz):
    """ A static method to return a new translation matrix based on parameters. """
    return MatrixExtended([
      [1, 0, 0, tx],
      [0, 1, 0, ty],
      [0, 0, 1, tz],
      [0, 0, 0, 1]])

  @staticmethod
  def getRotationMatrix(x, y, z, angle):
    """ A static method to return a new rotation matrix based on parameters. """
    # impossible to have a rotational matrix around (0, 0 ,0)
    if x == 0 and y == 0 and z == 0:
      raise Exception("Cannot have a rotation matrix around (0, 0, 0)")

    # normalize vector
    vec = MatrixExtended([x, y, z])
    length = np.linalg.norm(vec)
    x /= length
    y /= length
    z /= length

    # some shortcuts for readability
    xx = x * x
    yy = y * y
    zz = z * z
    C = math.cos
    S = math.sin

    # calculate matrix elements
    e11 = xx + (1 - xx) * C(angle)
    e12 = x * y * (1 - C(angle)) - z * S(angle)
    e13 = x * z * (1 - C(angle)) + y * S(angle)
    e21 = x * y * (1 - C(angle)) + z * S(angle)
    e22 = yy + (1 - yy) * C(angle)
    e23 = y * z * (1 - C(angle)) - x * S(angle)
    e31 = x * z * (1 - C(angle)) - y * S(angle)
    e32 = y * z * (1 - C(angle)) + x * S(angle)
    e33 = zz + (1 - zz) * C(angle)

    return MatrixExtended([
      [e11, e12, e13, 0],
      [e21, e22, e23, 0],
      [e31, e32, e33, 0],
      [0, 0, 0, 1]])

  @staticmethod
  def getScalingMatrix(sx, sy, sz):
    """ A static method to return a new scaling matrix based on parameters. """
    return MatrixExtended([
      [sx, 0, 0, 0],
      [0, sy, 0, 0],
      [0, 0, sz, 0],
      [0, 0, 0, 1]])

  @staticmethod
  def getPerspectiveProjectionMatrix(l, r, b, t, n, f):
    """ A static method to retun a new perspective projection matrix based on parameters. """
    e11 = 2 * n / (r - l)
    e13 = (r + l) / (r - l)
    e22 = (2 * n) / (t - b)
    e23 = (t + b) / (t - b)
    e33 = -1 * (f + n) / (f - n)
    e34 = (-2 * f * n) / (f - n)

    return MatrixExtended([
      [e11, 0, e13, 0],
      [0, e22, e23, 0],
      [0, 0, e33, e34],
      [0, 0, -1, 0]])
