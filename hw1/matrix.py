# Eric Pelz
# CS 171: Introduction to Computer Graphics

import numpy as np

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

  # TODO: Make own transformations, since can't use these from numpy
