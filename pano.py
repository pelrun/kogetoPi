import numpy as np
import cv2

class Dewarper:
  def __init__(self, Wd, Hd, Ws, Hs, R1, R2, Cx, Cy, angle, interpolation=cv2.INTER_CUBIC):
    self.interpolation = interpolation

    self.buildMap(Wd, Hd, Ws, Hs, R1, R2, Cx, Cy, angle)
    pass

  # build the mapping
  # optimised version of https://github.com/kscottz/dewarp/
  def buildMap(self, Wd, Hd, Ws, Hs, R1, R2, Cx, Cy, angle):
    map_x = np.zeros((Hd, Wd), np.float32)
    map_y = np.zeros((Hd, Wd), np.float32)
    rMap = np.linspace(R1, R1 + (R2 - R1), Hd)
    thetaMap = np.linspace(angle, angle + float(Wd) * 2.0 * np.pi, Wd)
    sinMap = np.sin(thetaMap)
    cosMap = np.cos(thetaMap)
    for y in xrange(0, Hd):
      map_x[y] = Cx + rMap[y] * sinMap
      map_y[y] = Cy + rMap[y] * cosMap
    (self.map1, self.map2) = cv2.convertMaps(map_x, map_y, cv2.CV_16SC2)

  def unwarp(self, img):
    output = cv2.remap(img, self.map1, self.map2, self.interpolation)
    return output
