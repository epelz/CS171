# Eric Pelz
# CS 171: Introduction to Computer Graphics
from matrix import MatrixExtended

global tension
tension = 0.5

class CRSpline():
  def __init__(self, numFrames, keyFrames):
    self.numFrames = numFrames
    self.keyFrames = keyFrames

    # interpolate all transformation data
    self.translationData = self.interpolate(
        map(lambda kf: {'data': kf.translation.data, 'num': kf.num}, keyFrames)
    )
    self.rotationData = self.interpolate(
        map(lambda kf: {'data': kf.rotation.data, 'num': kf.num}, keyFrames)
    )
    self.scaleData = self.interpolate(
        map(lambda kf: {'data': kf.scale.data, 'num': kf.num}, keyFrames)
    )

  def interpolate(self, frameData):
    data = []
    kfLength = len(frameData)
    for i in range(kfLength):
      # find four frames to interpolate
      if i == 0:
        kf0 = frameData[kfLength - 2]
        kf1 = frameData[kfLength - 1]
      elif i == 1:
        kf0 = frameData[kfLength - 1]
        kf1 = frameData[0]
      else:
        kf0 = frameData[i - 2]
        kf1 = frameData[i - 1]
      kf2 = frameData[i]
      if i == kfLength - 1:
        kf3 = frameData[0]
      else:
        kf3 = frameData[i + 1]

      d0 = kf0['data']
      d1 = kf1['data']
      d2 = kf2['data']
      d3 = kf3['data']

      frameStart = kf2['num']
      frameEnd = kf3['num'] if kf3['num'] > frameStart else self.numFrames
      frameWidth = frameEnd - frameStart

      u = 0
      du = 1 / float(frameWidth)
      for frame in range(frameStart, frameEnd):
        assert len(data) == frame # assert this new data is the next frame

        mat1 = MatrixExtended([1, u, u * u, u * u * u])
        mat2 = MatrixExtended([
          [0, 1, 0, 0],
          [-tension, 0, tension, 0],
          [2 * tension, tension - 3, 3 - 2 * tension, -tension],
          [-tension, 2 - tension, tension - 2, tension]])
        mat3 = MatrixExtended([d0, d1, d2, d3])

        result = mat2.mult(mat3)
        result = mat1.mult(result)
        data.append(result.tolist()[0])

        u += du

    return data
