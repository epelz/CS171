# Eric Pelz
# CS 171: Introduction to Computer Graphics

"""Simple test cases for the custom matrix library"""

from matrix import MatrixExtended
import unittest

class TestMatrixExtended(unittest.TestCase):
  """ A bunch of tests for the MatrixExtended class. """
  def setUp(self):
    self.matrix1 = MatrixExtended([
      [1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]])
    self.matrix2 = MatrixExtended([
      [5, 3, 1],
      [9, 7, 2],
      [1, 3, 5]])
    self.matrixIdentity = MatrixExtended([
      [1, 0, 0],
      [0, 1, 0],
      [0, 0, 1]])
    self.vector1 = MatrixExtended.getVector([1, 2, 3])
    self.vector2 = MatrixExtended.getVector([5, 3, -1])

  def assertEqualMatrices(self, matrix1, matrix2):
    """Asserts that two matrices are equal (rounds to 3 decimal places)"""
    return self.assertTrue((matrix1.round(3) == matrix2.round(3)).all())

  def testMatrixMultiplication(self):
    """Tests the multiplication of various matrices."""
    ## matrix * matrix
    self.assertEqualMatrices(
      self.matrix1 * self.matrix2,
      MatrixExtended([
        [26, 26, 20],
        [71, 65, 44],
        [116, 104, 68]]))
    self.assertEqualMatrices(
      self.matrix1.mult(self.matrixIdentity),
      self.matrix1)
    ### matrix * vector
    self.assertEqualMatrices(
      self.matrix2.mult(self.vector1),
      MatrixExtended.getVector([14, 29, 22]))

  def testDotProduct(self):
    """Tests the dot product of various vectors."""
    self.assertEqual(self.vector1.dotVector(self.vector1), 14)
    self.assertEqual(self.vector1.dotVector(self.vector2), 8)

  def testTranspose(self):
    """Tests the transpose of a matrix."""
    self.assertEqualMatrices(
      self.matrix1.getTranspose(),
      MatrixExtended([
        [1, 4, 7],
        [2, 5, 8],
        [3, 6, 9]]))
    self.assertEqualMatrices(
      self.matrixIdentity.getTranspose(),
      self.matrixIdentity)

  def testInverse(self):
    """Tests the inverse of a matrix."""
    ## check inverse
    self.assertEqualMatrices(
      self.matrix2.getInverse(),
      MatrixExtended([
        [29/36.0, -12/36.0, -1/36.0],
        [-43/36.0, 24/36.0, -1/36.0],
        [20/36.0, -12/36.0, 8/36.0]]))
    ## inverse * matrix = identity
    self.assertEqualMatrices(
      self.matrix2.getInverse().mult(self.matrix2),
      self.matrixIdentity)

  def testAddition(self):
    """Tests addition of matrices."""
    self.assertEqualMatrices(
      self.matrix1 + self.matrix2,
      MatrixExtended([
        [6, 5, 4],
        [13, 12, 8],
        [8, 11, 14]]))
  def testScalingMultiplication(self):
    """Tests scalar multiplication of matrices."""
    self.assertEqualMatrices(
      self.matrix1 * 4,
      MatrixExtended([
        [4, 8, 12],
        [16, 20, 24],
        [28, 32, 36]]))

if __name__ == "__main__":
  suite = unittest.TestLoader().loadTestsFromTestCase(TestMatrixExtended)
  unittest.TextTestRunner(verbosity=2).run(suite)
