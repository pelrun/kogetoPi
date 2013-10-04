import Tkinter
from PIL import Image, ImageTk
import numpy as np
import math
import sys
import cv2
import pano

class calibrationGui:
  def __init__(self, image):

    self.imageOriginal = image
    self.imageSize = self.imageOriginal.size
    self.imageMin = min(self.imageSize)

    # width, height
    self.canvasSize = (800, 600)
    self.root = Tkinter.Tk()
    self.root.title("Dewarper calibration")
    self.root.protocol('WM_DELETE_WINDOW', self.finish)

    self.w = Tkinter.Canvas(self.root, width=self.canvasSize[0], height=self.canvasSize[1], closeenough=10)
    self.w.bind("<Configure>", func=self.resize)
    self.w.pack(fill='both', expand='yes', side="top")

    self.statusBar = Tkinter.Label(self.root, bd=1, relief='sunken', anchor='w')
    self.statusBar.pack(side='bottom', fill='x')

    self.root2 = Tkinter.Toplevel()
    self.root2.title("Dewarper preview")
    self.root2.protocol('WM_DELETE_WINDOW', self.finish)

    self.previewLabel = Tkinter.Label(self.root2)
    self.previewLabel.pack(anchor='nw')

    Tkinter.Button(self.root2, text="Update", command=self.updatePreview).pack(side="left", anchor="nw")
    self.livePreview = Tkinter.IntVar()
    Tkinter.Checkbutton(self.root2, text='Live Preview',
                        variable=self.livePreview, command=self.update
                        ).pack(side="left", anchor="nw")

    self.r_max = self.w.create_oval(0, 0, 0, 0, width=1, outline='blue', activeoutline='green', fill='', tag='r_max')
    self.r_min = self.w.create_oval(0, 0, 0, 0, width=1, outline='blue', activeoutline='green', fill='', tag='r_min')
    self.angle = self.w.create_line(0, 0, 0, 0, width=1, fill='blue', activefill='green', tag='angle')
    self.centre = self.w.create_oval(0, 0, 0, 0, outline='', fill='blue', activefill='green', tag='centre')

    self.w.tag_bind('r_min', sequence='<B1-Motion>', func=self.scale_min)
    self.w.tag_bind('r_max', sequence='<B1-Motion>', func=self.scale_max)
    self.w.tag_bind('centre', sequence='<B1-Motion>', func=self.move)
    self.w.tag_bind('angle', sequence='<B1-Motion>', func=self.spin)

    self.dewarpRadii = [self.imageMin / 4, self.imageMin / 10]
    self.dewarpCentre = [self.imageSize[0] / 2, self.imageSize[1] / 2]
    self.dewarpAngle = 0

    self.updatePreview()
    self.root.mainloop()

  def finish(self):
    # Cleanup image copies
    self.image = None
    self.tkimage = None

    self.returnValue = self.dictParams()
    self.root.destroy()

  def imagemagickParams(self):
    angle = int(round(math.degrees(self.dewarpAngle)))
    return "-distort DePolar '{0} {1} {2},{3} {4},{5}'".format(self.dewarpRadii[0], self.dewarpRadii[1], self.dewarpCentre[0], self.dewarpCentre[1], angle, 360 + angle)

  def dictParams(self):
    return {'centre':self.dewarpCentre, 'radii':self.dewarpRadii, 'angle':self.dewarpAngle, 'imageSize':self.imageSize}

  def distanceFromXYC(self, centre, xy):
    imageXY = list(c * self.imageRatio for c in xy)
    return int(round(math.sqrt(math.pow(centre[0] - imageXY[0], 2) + math.pow(centre[1] - imageXY[1], 2))))

  def scale_min(self, event):
    newRadius = self.distanceFromXYC(self.dewarpCentre, (event.x, event.y))
    if newRadius < self.dewarpRadii[0]:
      self.dewarpRadii[1] = newRadius
      self.update()

  def scale_max(self, event):
    newRadius = self.distanceFromXYC(self.dewarpCentre, (event.x, event.y))
    if newRadius > self.dewarpRadii[1]:
      self.dewarpRadii[0] = newRadius
      self.update()

  def move(self, event):
    self.dewarpCentre[0] = int(round(event.x * self.imageRatio))
    self.dewarpCentre[1] = int(round(event.y * self.imageRatio))
    self.update()

  def angleFromXYC(self, centre, xy):
    imageXY = list(c * self.imageRatio for c in xy)
    return math.atan2(imageXY[0] - centre[0], imageXY[1] - centre[1])

  def spin(self, event):
    self.dewarpAngle = self.angleFromXYC(self.dewarpCentre, (event.x, event.y))
    self.update()

  def bboxFromXYR(self, centre, radius):
    return tuple(p / self.imageRatio for p in (centre[0] - radius, centre[1] - radius, centre[0] + radius, centre[1] + radius))

  def bboxFromXYA(self, centre, angle):
    x = centre[0] + math.sin(angle) * self.dewarpRadii[0]
    y = centre[1] + math.cos(angle) * self.dewarpRadii[0]
    return tuple(p / self.imageRatio for p in (x, y, centre[0], centre[1]))

  def update(self):
    self.w.coords(self.r_min, self.bboxFromXYR(self.dewarpCentre, self.dewarpRadii[1]))
    self.w.coords(self.r_max, self.bboxFromXYR(self.dewarpCentre, self.dewarpRadii[0]))
    self.w.coords(self.centre, self.bboxFromXYR(self.dewarpCentre, 10))
    self.w.coords(self.angle, self.bboxFromXYA(self.dewarpCentre, self.dewarpAngle))
    self.statusBar['text'] = self.dictParams()
    if self.livePreview.get():
      self.updatePreview()

  def resize(self, event):
    self.canvasSize = (event.width, event.height)

    self.w.delete('image')

    self.image = self.imageOriginal.copy()
    self.image.thumbnail(self.canvasSize)
    self.imageRatio = float(self.imageMin) / min(self.image.size)

    self.tkimage = ImageTk.PhotoImage(self.image)
    self.w.create_image(0, 0, anchor='nw', image=self.tkimage, tag='image')
    self.w.tag_lower('image')

    self.update()

  def updatePreview(self):
    dewarper = pano.Dewarper(destSize[0], destSize[1],
                             self.imageOriginal.size[0], self.imageOriginal.size[1],
                             self.dewarpRadii[1], self.dewarpRadii[0],
                             self.dewarpCentre[0], self.dewarpCentre[1],
                             self.dewarpAngle)

    self.previewTkImage = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(dewarper.unwarp(cvImage), cv2.COLOR_BGR2RGB)))
    self.previewLabel['image'] = self.previewTkImage

if __name__ == "__main__":
  destSize = [800, 200]
  if len(sys.argv) > 1:
    image = Image.open(sys.argv[1])
    cvImage = cv2.cvtColor(np.asarray(image.convert('RGB')), cv2.COLOR_RGB2BGR)

    calData = calibrationGui(image)
    print calData.dictParams()

  else:
    print "Usage: python {0} <image>".format(sys.argv[0])
