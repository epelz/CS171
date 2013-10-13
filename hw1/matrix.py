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
    return MatrixExtended('1 0 0 %f; 0 1 0 %f; 0 0 1 %f; 0 0 0 1' %
      (tx, ty, tz))

  @staticmethod
  def getRotationMatrix(x, y, z, angle):
    """ A static method to return a new rotation matrix based on parameters. """
    xx = x * x
    yy = y * y
    zz = z * z
    e11 = xx + (1-xx)*math.cos(angle)
    e12 = x * y * (1 - math.cos(angle)) - z * math.sin(angle)
    e13 = x * z * (1 - math.cos(angle)) + y * math.sin(angle)
    e21 = x * y * (1 - math.cos(angle)) + z * math.sin(angle)
    e22 = yy + (1 - yy)*math.cos(angle)
    e23 = y * z * (1 - math.cos(angle)) - x * math.sin(angle)
    e31 = x * z * (1 - math.cos(angle)) - y * math.sin(angle)
    e32 = y * z * (1 - math.cos(angle)) + x * math.sin(angle)
    e33 = zz + (1 - zz)*math.cos(angle)
    return MatrixExtended('%f %f %f 0; %f %f %f 0; %f %f %f 0; 0 0 0 1' %
      (e11, e12, e13, e21, e22, e23, e31, e32, e33))

  @staticmethod
  def getScalingMatrix(sx, sy, sz):
    """ A static method to return a new scaling matrix based on parameters. """
    return MatrixExtended('%f 0 0 0; 0 %f 0 0; 0 0 %f 0; 0 0 0 1' %
      (sx, sy, sz))
