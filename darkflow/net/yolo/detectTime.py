import cv2
import numpy as np
from math import hypot
from math import atan2
from math import degrees
from math import floor

def getTime(img):
    try:
        height, width, channels = img.shape

        #pretvaranje u grayscale i podesavanje adaptivnog praga
        cimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        adaptiveImg = cv2.adaptiveThreshold(cimg, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 10)

        #pronalazenje krugova na slici
        circles = cv2.HoughCircles(adaptiveImg,cv2.HOUGH_GRADIENT,1,width/4,
                                    param1=300, param2=50, minRadius=int(width/4),maxRadius=int(width/2))
        try:
            circles = np.uint16(np.around(circles))
        except:
            return None

        """#iscrtavanje prvog kruga
        for i in circles[0]:
            # kruznica
            cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
            # centar kruga
            cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)"""

        #izdvajanje krugova od interesa i invertovanje piksela (crni->beli i obrnuto)
        circleX, circleY, circleRad = circles[0][0]

        """cv2.circle(img,(circleX,circleY),int(circleRad*0.2),(0,255,0),2)
        cv2.circle(img,(circleX,circleY),int(circleRad*0.4),(0,255,0),2)
        cv2.circle(img,(circleX,circleY),int(circleRad*0.8),(0,255,0),2)"""

        #filter okoline 0 < AREA < 0.2 * radius
        circle_img2 = np.ones((height,width), np.uint8)
        cv2.circle(circle_img2,(circleX,circleY),int(circleRad * 0.2),0,thickness=-1)

        #filter okoline AREA < 0.8 * radius
        circle_img = np.zeros((height,width), np.uint8)
        cv2.circle(circle_img,(circleX,circleY),int(circleRad * 0.8),1,thickness=-1)

        #filter okoline AREA < 0.4 * radius
        circle_img1 = np.zeros((height,width), np.uint8)
        cv2.circle(circle_img1,(circleX,circleY),int(circleRad * 0.4),1,thickness=-1)

        adaptiveImg = cv2.bitwise_not(adaptiveImg)
        invImg = adaptiveImg.copy()

        adaptiveImg = cv2.bitwise_and(adaptiveImg, adaptiveImg, mask=circle_img)
        adaptiveImg = cv2.bitwise_and(adaptiveImg, adaptiveImg, mask=circle_img2)

        invImg = cv2.bitwise_and(invImg, invImg, mask=circle_img1)
        invImg = cv2.bitwise_and(invImg, invImg, mask=circle_img2)

        #zatvaranje - dilacija + erozija (bolje izdvajanje belih elemenata)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        invImg = cv2.dilate(invImg, kernel, iterations=1)
        invImg = cv2.erode(invImg, kernel, iterations=1)

        adaptiveImg = cv2.dilate(adaptiveImg, kernel, iterations=1)
        adaptiveImg = cv2.erode(adaptiveImg, kernel, iterations=1)

        '''pronalazenje kontura kazaljki'''
        # uklonjen cenatar i oklonjena okolina sata (radius * 0.2 < AREA < radius * 0.4)
        imgContorues, contours, hierarchy = cv2.findContours(invImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        rows,cols = img.shape[:2]

        epsilonMin = circleRad * 0.01
        clockContours = []
        clockContourOrientation = []
        clockContourWidth = []
        for contour in contours:
            center, size, angle = cv2.minAreaRect(contour)
            conWidth, conHeight = size

            topmost = tuple(contour[contour[:,:,1].argmin()][0])
            bottommost = tuple(contour[contour[:,:,1].argmax()][0])
            topDiff = hypot(topmost[0]-circleX, topmost[1]-circleY)
            bottomDiff = hypot(bottommost[0]-circleX, bottommost[1]-circleY)

            leftmost = tuple(contour[contour[:,:,0].argmin()][0])
            rightmost = tuple(contour[contour[:,:,0].argmax()][0])
            leftDiff = hypot(leftmost[0]-circleX, leftmost[1]-circleY)
            rightDiff = hypot(rightmost[0]-circleX, rightmost[1]-circleY)

            if topDiff >= (circleRad * 0.4) - epsilonMin and topDiff <= (circleRad * 0.4) + epsilonMin:
                if bottomDiff >= (circleRad * 0.2) - epsilonMin and bottomDiff <= (circleRad * 0.2) + epsilonMin:
                    clockContours.append(contour)
                    clockContourOrientation.append('top')
                    if conWidth > conHeight:
                        clockContourWidth.append(conWidth)
                    else:
                        clockContourWidth.append(conHeight)
            elif bottomDiff >= (circleRad * 0.4) - epsilonMin and bottomDiff <= (circleRad * 0.4) + epsilonMin:
                if topDiff >= (circleRad * 0.2) - epsilonMin and topDiff <= (circleRad * 0.2) + epsilonMin:
                    clockContours.append(contour)
                    clockContourOrientation.append('bottom')
                    if conWidth > conHeight:
                        clockContourWidth.append(conWidth)
                    else:
                        clockContourWidth.append(conHeight)
            elif leftDiff >= (circleRad * 0.4) - epsilonMin and leftDiff <= (circleRad * 0.4) + epsilonMin:
                if rightDiff >= (circleRad * 0.2) - epsilonMin and rightDiff <= (circleRad * 0.2) + epsilonMin:
                    clockContours.append(contour)
                    clockContourOrientation.append('left')
                    if conWidth > conHeight:
                        clockContourWidth.append(conWidth)
                    else:
                        clockContourWidth.append(conHeight)
            elif rightDiff >= (circleRad * 0.4) - epsilonMin and rightDiff <= (circleRad * 0.4) + epsilonMin:
                if leftDiff >= (circleRad * 0.2) - epsilonMin and leftDiff <= (circleRad * 0.2) + epsilonMin:
                    clockContours.append(contour)
                    clockContourOrientation.append('right')
                    if conWidth > conHeight:
                        clockContourWidth.append(conWidth)
                    else:
                        clockContourWidth.append(conHeight)

        """imgContorues = img.copy()
        cv2.drawContours(imgContorues, clockContours, -1, (0, 0, 255), 2)

        cv2.imshow('detected lines and circle',imgContorues)
        cv2.waitKey(0)"""

        #konture nad celom slikom (0.2 * radius < AREA < 0.8 * radius)
        imgAllContorues, allContours, allContHierarchy = cv2.findContours(adaptiveImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        """imgAllContorues = img.copy()
        cv2.drawContours(imgAllContorues, allContours, -1, (0, 0, 255), 2)

        cv2.imshow('detected lines and circle',imgAllContorues)
        cv2.waitKey(0)"""

        fullClockContours = []
        fullClockMaxPoints = []
        fullClockWidths = []
        for fullContour in allContours:
            fullCenter, fullSize, fullAngle = cv2.minAreaRect(fullContour)
            fullConWidth, fullConHeight = size
            fullTopmost = tuple(fullContour[fullContour[:,:,1].argmin()][0])
            fullBottommost = tuple(fullContour[fullContour[:,:,1].argmax()][0])
            fullLeftmost = tuple(fullContour[fullContour[:,:,0].argmin()][0])
            fullRightmost = tuple(fullContour[fullContour[:,:,0].argmax()][0])
            for clockContour in clockContours:
                clockCenter, clockSize, clockAngle = cv2.minAreaRect(clockContour)
                clockConWidth, clockConHeight = size
                clockTopmost = tuple(clockContour[clockContour[:,:,1].argmin()][0])
                clockBottommost = tuple(clockContour[clockContour[:,:,1].argmax()][0])
                if fullTopmost == clockTopmost or fullTopmost == clockBottommost:
                    fullClockContours.append(fullContour)
                    idx1 = clockContours.index(clockContour)
                    tmpWidth = clockContourWidth[idx1]
                    fullClockWidths.append(tmpWidth)
                    tempIndex=clockContours.index(clockContour)
                    tempSmer=clockContourOrientation[tempIndex]
                    if tempSmer == 'top':
                        fullClockMaxPoints.append(fullTopmost)
                    elif tempSmer == 'bottom':
                        fullClockMaxPoints.append(fullBottommost)
                    elif tempSmer == 'left':
                        fullClockMaxPoints.append(fullLeftmost)
                    else:
                        fullClockMaxPoints.append(fullRightmost)
                elif fullBottommost == clockTopmost or fullBottommost == clockBottommost:
                    fullClockContours.append(fullContour)
                    tempIndex=clockContours.index(clockContour)
                    tempSmer=clockContourOrientation[tempIndex]
                    idx1 = clockContours.index(clockContour)
                    tmpWidth = clockContourWidth[idx1]
                    fullClockWidths.append(tmpWidth)
                    if tempSmer == 'top':
                        fullClockMaxPoints.append(fullTopmost)
                    elif tempSmer == 'bottom':
                        fullClockMaxPoints.append(fullBottommost)
                    elif tempSmer == 'left':
                        fullClockMaxPoints.append(fullLeftmost)
                    else:
                        fullClockMaxPoints.append(fullRightmost)

        """imgAllContorues = img.copy()
        cv2.drawContours(imgAllContorues, fullClockContours, -1, (0, 0, 255), 2)"""


        #podela nadjenih tacaka i izdvajanje po najduzem rastojanju
        maxDiffs = []

        if len(fullClockContours) > 10:
            return None

        for tmpPoint in fullClockMaxPoints:    
            tmpX = tmpPoint[0]
            tmpY = tmpPoint[1]
            tmpMaxDiff = hypot(tmpX-circleX, tmpY-circleY)
            maxDiffs.append(tmpMaxDiff)

        #spajanje slicnih linija u jednu
        maxPoints_Copy = list(fullClockMaxPoints)
        maxDiffs_Copy = list(maxDiffs)

        extraDiffs = []
        extraPoints = []
        extraWidths = []
        epsilon = circleRad * 0.05

        for maxDiff in maxDiffs:
            for tmpDiff in maxDiffs_Copy:
                if tmpDiff != maxDiff and abs(tmpDiff - maxDiff) <= epsilon:
                    idx = maxDiffs.index(maxDiff)
                    tmpIdx = maxDiffs_Copy.index(tmpDiff)                        
                    diff_fin = hypot(fullClockMaxPoints[idx][0]-maxPoints_Copy[tmpIdx][0], fullClockMaxPoints[idx][1]-maxPoints_Copy[tmpIdx][1])
                    if diff_fin <= epsilon and diff_fin != 0:
                        if tmpDiff not in extraDiffs:
                            extraDiffs.append(maxDiff)
                            extraPoints.append(fullClockMaxPoints[idx])
                            extraWidths.append(fullClockWidths[idx])

        #oduzimanje viska
        finalDiffs = [-1 for x in range(3)]
        finalPoints = [-1 for x in range(3)]
        finalWidths = [-1 for x in range(3)]
        finalDiffs = list(set(maxDiffs) - set(extraDiffs))
        finalPoints = list(set(fullClockMaxPoints) - set(extraPoints))
        finalWidths = list(set(fullClockWidths) - set(extraWidths))

        #sortiranje duzina linija i rasporeda tacaka
        hourPoint = []
        minutePoint = []
        secondPoint = []

        finalDiffs=sorted(finalDiffs)

        maxContureWidth = []
        br=0
        for point in finalPoints[0:]:
            tmpX = point[0]
            tmpY = point[1]
            tmpDiff = hypot(tmpX-circleX, tmpY-circleY)
            if tmpDiff == finalDiffs[0]:
                hourPoint = [tmpX, tmpY]
            elif tmpDiff == finalDiffs[1]:
                minutePoint = [tmpX, tmpY]
                maxContureWidth.append(finalWidths[br])
            elif tmpDiff == finalDiffs[2]:
                secondPoint = [tmpX, tmpY]
                maxContureWidth.append(finalWidths[br])
            br+=1

        if len(maxContureWidth) > 2:
            if maxContureWidth[0] < maxContureWidth[1]:
                temp = minutePoint
                minutePoint = secondPoint
                secondPoint = temp

        if len(finalDiffs)<2:
            return None

        #odredjivanje uglova kazaljki i samog vremena
        hourAngle = 180 - degrees(atan2(circleY-hourPoint[1], circleX-hourPoint[0])) % 360
        minuteAngle = 180 - degrees(atan2(circleY-minutePoint[1], circleX-minutePoint[0])) % 360

        #matematicki uglovi
        if len(finalDiffs) == 3:
            secondAngle = 180 - degrees(atan2(circleY-secondPoint[1], circleX-secondPoint[0])) % 360

        #print(hourAngle)
        #print(minuteAngle)

        #if len(finalDiffs) == 3:
            #print(secondAngle)

        #satni uglovi
        hourAngle = 90 - floor(hourAngle)
        if hourAngle < 0:
            hourAngle += 360

        hours = floor(hourAngle/30)
        #print(hours)

        #minutni uglovi
        minuteAngle = 90 - floor(minuteAngle)
        if minuteAngle < 0:
            minuteAngle += 360

        minutes = floor(minuteAngle/6)
        #print(minutes)
        seconds = None
        #sekundski uglovi
        if len(finalDiffs) == 3:
            secondAngle = 90 - floor(secondAngle)

            if secondAngle < 0:
                secondAngle += 360

            seconds = floor(secondAngle/6)
            #print(seconds)

        if hours < 10:
            hourString = '0' + str(hours)
        else:
            hourString = str(hours)

        if minutes < 10:
            minuteString = '0' + str(minutes)
        else:
            minuteString = str(minutes)        
        
        if type(seconds)==type(None):
            return (hourString + ":" + minuteString)
        else:
            if seconds < 10:
                secondString = '0' + str(seconds)
            else:
                secondString = str(seconds)
            return (hourString + ":" + minuteString + ":" + secondString)   

        """#iscrtavanje linija
        for point in finalPoints:    
            if point[0] != -1:
                cv2.line(img,(point[0],point[1]),(circleX,circleY),(0,0,255),2)    

        cv2.imshow('detected lines and circle',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()"""  
    except:
        return None