import sys
import cv2
import pano

def dewarp(filename, params):
  dewarper = pano.Dewarper(*params)
  capture = cv2.VideoCapture(filename)
  cv2.namedWindow("preview", cv2.CV_WINDOW_AUTOSIZE)
  while True:
    (retval, im) = capture.read()
    if im is None:
      break
    frame = dewarper.unwarp(im)
    cv2.imshow("preview", frame)
    cv2.waitKey(1)

if __name__ == "__main__":
  params = [800, 200, 1280, 720, 134, 251, 644, 387, -2.85]

  if len(sys.argv) > 1:
    dewarp(sys.argv[1], params)
  else:
    print "Usage: python {0} <video>".format(sys.argv[0])
