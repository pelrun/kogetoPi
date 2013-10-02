import Tkinter
from PIL import Image, ImageTk
import math

class dewarpGui:
  def __init__(self):

    self.imageFile = "image.jpg"

    # width, height
    self.canvasSize = (800, 600)
    self.root = Tkinter.Tk()
    self.root.title("Dewarp calibration")
    self.root.protocol('WM_DELETE_WINDOW', self.finish)

    self.w = Tkinter.Canvas(self.root, width=self.canvasSize[0], height=self.canvasSize[1], closeenough=10)
    self.w.bind("<Configure>", func=self.resize)
    self.w.pack(fill='both', expand='yes')

    self.statusBar = Tkinter.Label(self.root, bd=1, relief='sunken', anchor='w')
    self.statusBar.pack(side='bottom', fill='x')

#    Tkinter.Entry(self.root, textvariable=self.imageFile).pack(side='left', fill='x', expand='yes')
#    Tkinter.Button(self.root, text="OK", width=10, command=None).pack(side='right')
#    Tkinter.Button(self.root, text="Cancel", width=10, command=None).pack(side='right')
#    Tkinter.Button(self.root, text="...", width=5, command=None).pack(side='right')

    self.r_max = self.w.create_oval(0, 0, 0, 0, width=1, outline='blue', activeoutline='green', fill='', tag='r_max')
    self.r_min = self.w.create_oval(0, 0, 0, 0, width=1, outline='blue', activeoutline='green', fill='', tag='r_min')
    self.angle = self.w.create_line(0, 0, 0, 0, width=1, fill='blue', activefill='green', tag='angle')
    self.centre = self.w.create_oval(0, 0, 0, 0, outline='', fill='blue', activefill='green', tag='centre')

    self.w.tag_bind('r_min', sequence='<B1-Motion>', func=self.scale_min)
    self.w.tag_bind('r_max', sequence='<B1-Motion>', func=self.scale_max)
    self.w.tag_bind('centre', sequence='<B1-Motion>', func=self.move)
    self.w.tag_bind('angle', sequence='<B1-Motion>', func=self.spin)

    self.loadImage(self.imageFile)

    self.dewarpRadii = [self.imageMin / 4, self.imageMin / 10]
    self.dewarpCentre = [self.imageSize[0] / 2, self.imageSize[1] / 2]
    self.dewarpAngle = 0

    self.root.mainloop()

  def finish(self):
    print self.statusBar["text"]
    self.root.destroy()

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
    angle = int(round(math.degrees(self.dewarpAngle)))
    self.statusBar["text"] = "-distort DePolar '{0} {1} {2},{3} {4},{5}'".format(self.dewarpRadii[0], self.dewarpRadii[1], self.dewarpCentre[0], self.dewarpCentre[1], angle, 360 + angle)

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

  def loadImage(self, filename):
    self.imageOriginal = Image.open(filename)
    self.imageSize = self.imageOriginal.size
    self.imageMin = min(self.imageSize)

ui = dewarpGui()