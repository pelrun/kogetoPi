import numpy as np
import cv2

class Dewarper:
  def __init__(self, Wd, Hd, Ws, Hs, R1, R2, Cx, Cy, angle):
    self.buildMap(Wd, Hd, Ws, Hs, R1, R2, Cx, Cy, angle)
    pass

  # build the mapping
  # optimised version of https://github.com/kscottz/dewarp/
  def buildMap(self, Wd, Hd, Ws, Hs, R1, R2, Cx, Cy, angle):
    self.map_x = np.zeros((Hd, Wd), np.float32)
    self.map_y = np.zeros((Hd, Wd), np.float32)
    rMap = np.linspace(R1, R1 + (R2 - R1), Hd)
    thetaMap = np.linspace(angle, angle + float(Wd) * 2.0 * np.pi, Wd)
    sinMap = np.sin(thetaMap)
    cosMap = np.cos(thetaMap)
    for y in xrange(0, Hd):
      self.map_x[y] = Cx + rMap[y] * sinMap
      self.map_y[y] = Cy + rMap[y] * cosMap

  def unwarp(self, img):
    output = cv2.remap(img, self.map_x, self.map_y, cv2.INTER_CUBIC)
    return output
