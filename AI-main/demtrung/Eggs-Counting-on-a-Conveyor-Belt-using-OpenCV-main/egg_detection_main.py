import numpy as np
import pprint
import sys
import datetime  # DateTime Importing
import math  # Maths Library for mathematical functions
import cv2  # Python Image Processing Library
import matplotlib.pyplot as plt  # Plotting Taks
from getdist import plots, MCSamples

from PyQt5.QtWidgets import QApplication
from dialogs.settings_dialog import Settings

# We will use all these variables 

width = 0
height = 0
eggCount = 0
exitCounter = 0
OffsetRefLines = 50  # Adjust ths value according to your usage
ReferenceFrame = None
distance_tresh = 200
radius_min = 0
radius_max = 0
area_min = 0
area_max = 0

# Making object of classes from above file

app = QApplication(sys.argv)
set = Settings()



def reScaleFrame(frame, percent=75):
    width = int(frame.shape[1] * percent // 100)
    height = int(frame.shape[0] * percent // 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)


def CheckInTheArea(coordYContour, coordYEntranceLine, coordYExitLine):
    if ((coordYContour <= coordYEntranceLine) and (coordYContour >= coordYExitLine)):
        return 1
    else:
        return 0


def CheckEntranceLineCrossing(coordYContour, coordYEntranceLine):
    absDistance = abs(coordYContour - coordYEntranceLine)

    if ((coordYContour >= coordYEntranceLine) and (absDistance <= 3)):
        return 1
    else:
        return 0


def getDistance(coordYEgg1, coordYEgg2):
    dist = abs(coordYEgg1 - coordYEgg2)
    return dist


cap = cv2.VideoCapture('2.mp4')
#cap = cv2.VideoCapture(0)

fgbg = cv2.createBackgroundSubtractorMOG2()

while True:
    (grabbed, frame) = cap.read()

    # This if condition will execute only when code ends, properly

    if not grabbed:
        print('Egg count: ' + str(eggCount))
        print('\n End of the video file...')
        break

    radius_min, radius_max = set.getRadius()
    area_min, area_max = set.getArea()

    if radius_min == '':
        radius_min = 0
    if radius_max == '':
        radius_max = 0

    if area_min == '':
        area_min = 0
    if area_max == '':
        area_max = 0

    frame40 = reScaleFrame(frame, percent=40)

    height = np.size(frame40, 0)
    width = np.size(frame40, 1)

    fgmask = fgbg.apply(frame40)

    hsv = cv2.cvtColor(frame40, cv2.COLOR_BGR2HSV)

    th, bw = cv2.threshold(hsv[:, :, 2], 0, 255,
                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    morph = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

    dist = cv2.distanceTransform(morph, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)

    borderSize = set.getBorderSizeValue()  # Taking it from PyQt5 Class

    distborder = cv2.copyMakeBorder(dist, borderSize, borderSize, borderSize, borderSize,
                                    cv2.BORDER_CONSTANT | cv2.BORDER_ISOLATED, 0)

    gap = 10
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * (borderSize - gap) + 1, 2 * (borderSize - gap) + 1))
    kernel2 = cv2.copyMakeBorder(kernel2, gap, gap, gap, gap,
                                 cv2.BORDER_CONSTANT | cv2.BORDER_ISOLATED, 0)

    distTempl = cv2.distanceTransform(kernel2, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)

    nxcor = cv2.matchTemplate(distborder, distTempl, cv2.TM_CCOEFF_NORMED)

    mn, mx, _, _ = cv2.minMaxLoc(nxcor)
    th, peaks = cv2.threshold(nxcor, mx * 0.5, 255, cv2.THRESH_BINARY)
    peaks8u = cv2.convertScaleAbs(peaks)


    #_, contours, hierarchy = cv2.findContours(peaks8u, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contours, hierarchy = cv2.findContours(peaks8u, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)


    peaks8u = cv2.convertScaleAbs(peaks)  # to use as mask

    coordYEntranceLine = (height // 2) + OffsetRefLines
    coordYMiddleLine = (height // 2)
    coordYExitLine = (height // 2) - OffsetRefLines
    cv2.line(frame40, (0, coordYEntranceLine), (width, coordYEntranceLine), (255, 0, 0), 2)
    cv2.line(frame40, (0, coordYMiddleLine), (width, coordYMiddleLine), (0, 255, 0), 6)
    cv2.line(frame40, (0, coordYExitLine), (width, coordYExitLine), (255, 0, 0), 2)

    flag = False
    egg_list = []
    egg_index = 0

    for i in range(len(contours)):
        contour = contours[i]

        (x, y), radius = cv2.minEnclosingCircle(contour)  # Taking Center & Radius
        radius = int(radius)
        (x, y, w, h) = cv2.boundingRect(contour)

        # Execute it if you want understanding of above cv2.minEnclosingCircle
        # cv2.rectangle(frame40,(x,y),(x+w,y+h),(0,255,0),2)

        egg_index = i

        egg_list.append([x, y, flag])

        if len(contour) >= 5:

            if (radius <= int(radius_max) and radius >= int(radius_min)):

                # print("radius: ", radius)
                # pprint.pprint(hierarchy)

                ellipse = cv2.fitEllipse(contour)

                (center, axis, angle) = ellipse

                coordXContour, coordYContour = int(center[0]), int(center[1])  # Computer the center coordinates

                # Centroid Formula Calculation

                coordXCentroid = (2 * coordXContour + w) // 2
                coordYCentroid = (2 * coordYContour + h) // 2

                ax1, ax2 = int(axis[0]) - 2, int(axis[1]) - 2

                orientation = int(angle)
                area = cv2.contourArea(contour)

                if area >= int(area_min) and area <= int(area_max):

                    # print('egg list: ' + str(egg_list) + ' index: ' + str(egg_index))

                    if CheckInTheArea(coordYContour, coordYEntranceLine,
                                      coordYExitLine):  # Checking Done Always Inside the Boundary

                        cv2.ellipse(frame40, (coordXContour, coordYContour), (ax1, ax2), orientation, 0, 360,
                                    (255, 0, 0), 2)  # blue around the real egg

                        cv2.circle(frame40, (coordXContour, coordYContour), 1, (0, 255, 0), 15)  # green Center Marked

                        cv2.putText(frame40, str(int(area)), (coordXContour, coordYContour), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, 0, 1, cv2.LINE_AA)

                    for k in range(len(egg_list)):
                        egg_new_X = x
                        egg_new_Y = y

                        dist = getDistance(egg_new_Y,
                                           egg_list[k][1])

                        if dist > distance_tresh:  # distance_tresh = 200
                            egg_list.append([egg_new_X, egg_new_Y, flag])

                    if CheckEntranceLineCrossing(egg_list[egg_index][1], coordYMiddleLine) and not egg_list[egg_index][
                        2]:
                        eggCount += 1
                        egg_list[egg_index][2] = True

                cv2.putText(frame40, "Eggs Counted: {}".format(str(eggCount)), (8, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (250, 0, 255), 2)

    cv2.imshow("Original Frame", frame40)
    # cv2.imshow("Background Mask", fgmask)
    # cv2.imshow("HSV", hsv)
    # cv2.imshow("Thresh",bw)
    cv2.imshow("Th", peaks)
    cv2.imshow("copymakeBorder", distborder)
    cv2.imshow("Distance_trans", distTempl)

    key = cv2.waitKey(1)

    if key == 27:
        break

# cleanup the camera and close any open windows
cap.release()
cv2.destroyAllWindows()



