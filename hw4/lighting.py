# Eric Pelz
# CS 171: Introduction to Computer Graphics

import openInventor
from matrix import MatrixExtended

## some helper functions ##
def zeroClipFloat(x):
  return x if x > 0.0 else 0.0

def zeroClip(X):
  return X.mapVector(lambda x: x if x > 0.0 else 0.0)

def oneClip(X):
  return X.mapVector(lambda x: x if x < 1.0 else 1.0)

def unit(x):
  norm = x.getVectorNorm()
  return x / norm if norm != 0.0 else 0.0

def vectorize(x):
  return MatrixExtended.getVector(x)

## general lighting function ##
def calculateLighting(
    n, # surface normal (nx, ny, nz)
    v, # point in space (x, y, z)
    material,
    lights, # [light0, light1, ...]
    cameraPos, # (x, y, z)
    ):
  sColor = vectorize(material.getSpecularColor()) # (r, g, b)
  dColor = vectorize(material.getDiffuseColor()) # (r, g, b)
  aColor = vectorize(material.getAmbientColor()) # (r, g, b)
  shiny = material.getShininess()

  # start off the diffuse and specular at pitch black
  diffuse = vectorize([0.0, 0.0, 0.0])
  specular = vectorize([0.0, 0.0, 0.0])
  # copy ambient color
  ambient = MatrixExtended(aColor)

  for light in lights:
    # get position and color from light
    lPosition = vectorize(light.getLocation()) # (x, y, z)
    lColor = vectorize(light.getColor()) # (r, g, b)

    # calculate the addition this light makes to diffuse part
    ddiffuse = zeroClip(lColor * (n.dotVector(unit(lPosition - v))))
    diffuse += ddiffuse

    # calculate the specular exponent
    k = zeroClipFloat(n.dotVector(unit(unit(cameraPos - v) + unit(lPosition - v))))

    # calculate the addition to the specular highlight
    dspecular = zeroClip(lColor * (k ** shiny))
    specular += dspecular

  # after working on all the lights, clamp the diffuse value to 1
  d = oneClip(diffuse)

  # note that d, dColor, specular, and sColor are all (r,g,b)
  rgb = oneClip(ambient + d.multiplyVectorComponents(dColor) + specular.multiplyVectorComponents(sColor))

  # assert that RGB values are valid
  assert all(map(lambda n: n >= 0 and n <= 1, rgb))

  return rgb
