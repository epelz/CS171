"""Simple test cases for the custom matrix library"""

from matrix import MatrixExtended
import unittest

class TestOne(unittest.TestCase):
  def test(self):
    """Simple test"""
    self.assertEqual(1, 1)
    self.assertEqual(4, 4)

  def testTwo(self):
    """Simple test two"""
    self.assertFalse(1==2)

  # TODO: Make test cases
  # TODO: Test the transformation matrices as well

if __name__ == "__main__":
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(TestOne)
  unittest.TextTestRunner(verbosity=2).run(suite)
