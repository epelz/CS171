# Eric Pelz
# CS 171: Introduction to Computer Graphics

class Script():
  def __init__(self, total_num, frames):
    self.total_num = total_num
    self.frames = frames

  def __repr__(self):
    return "[Script: total-num: %s, frames: %s]" % \
        (self.total_num, self.frames)

class Frame():
  def __init__(self, num, translation, rotation, scale):
    self.num = num
    self.translation = translation
    self.rotation = rotation
    self.scale = scale

  def __repr__(self):
    return "[Frame %s: translation: %s, rotation: %s, scale: %s]" % \
        (self.num, self.translation, self.rotation, self.scale)

class Transform():
  # types of transforms
  translation, rotation, scale = range(3)

  def __init__(self, transformType, data):
    self.transformType = transformType
    self.data = data
  def __repr__(self):
    return "[Transform (%s): %s]" % (self.transformType, str(self.data))
  ## Static methods to initialize new transformation matrices ##
  @staticmethod
  def newTranslation(data):
    return Transform(Transform.translation, data)
  @staticmethod
  def newRotation(data):
    return Transform(Transform.rotation, data)
  @staticmethod
  def newScale(data):
    return Transform(Transform.scale, data)
