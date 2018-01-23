import cv2

import numpy as np

img = cv2.imread('images/nesa.jpg', 0)

img = cv2.medianBlur(img, 5)
cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
height, width, channels = cimg.shape
#proba
#idemo opet

circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20,
                           param1=300, param2=50, minRadius=0, maxRadius=0)

circles = np.int16(np.around(circles))
for i in circles[0, :]:
    # draw the outer circle
    cv2.circle(cimg, (i[0], i[1]), i[2], (0,255,0), 2)
    # draw the center of the circle
    cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)

blackImg = np.zeros((height,width,channels), np.uint8)

for circle in circles[0,:]:
    for i in range(0,height):
        for j in range(0,width):
            tmpCenter = np.array((circle[0], circle[1]))
            tmpCoord = np.array((j, i))
            # normTupple = ((i  - circle[0]), (j - circle[1]))
            if np.linalg.norm(tmpCoord-tmpCenter) < circle[2]:
                blackImg[i,j] = img[i,j]

edges = cv2.Canny(blackImg,100,200)
minLineLength = 50
maxLineGap = 10
lines = cv2.HoughLinesP(edges,1,np.pi/180,5, minLineLength, maxLineGap)
for x1,y1,x2,y2 in lines[0]:
    cv2.line(edges,(x1,y1),(x2,y2),(255,0,0),5)

cv2.imshow('detected circles',edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
