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

  def test(self):
    # TODO: Remove this before using
    return self.getT()

  #---- Static functions to return transformation matrices ----
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
