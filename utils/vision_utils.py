import cv2
import numpy as np


def isolate_point(img, lowerHSV, higherHSV, area_thresh=100):
    isolated = isolate_color(img.copy(), lowerHSV, higherHSV)
    gray = cv2.cvtColor(isolated, cv2.COLOR_BGR2GRAY)

    cnts = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[1]

    cnts = sorted(cnts, key=lambda c: cv2.contourArea(c), reverse=True)
    if len(cnts) == 0:
        print("No contours found! Returning...")
        return None

    cnt = cnts[0]
    if cv2.contourArea(cnt) < area_thresh:
        print("Not enough area. Returning...")
        return None

    # compute the center of the contour
    M = cv2.moments(cnt)
    if M["m10"] == 0 or M["m00"] == 0 or M["m01"] == 0:
        print("Failed to get Moment of contour!")

    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])

    return cX, cY


def find_squares(img):
    def angle_cos(p0, p1, p2):
        d1, d2 = (p0 - p1).astype('float'), (p2 - p1).astype('float')
        return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1) * np.dot(d2, d2)))

    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv2.split(img):
        for thrs in range(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                _retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            bin, contours, _hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in range(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)
    return squares


def isolate_color(img, lowerHSV, higherHSV):
    """
    :param img: Image to isolate teh color of
    :param lowerHSV: [lowerHue, lowerSat, lowerVal]
    :param higherHSV: [upperHue, upperSat, upperVal]
    :return: Isolated image
    """

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    if lowerHSV[0] > higherHSV[0]:
        # If the HSV values wrap around, then intelligently mask it

        upper1 = [180, higherHSV[1], higherHSV[2]]
        mask1  = cv2.inRange(hsv, np.array(lowerHSV), np.array(upper1))

        lower2 = [0, lowerHSV[1], lowerHSV[2]]
        mask2  = cv2.inRange(hsv, np.array(lower2), np.array(higherHSV))

        mask = mask1 + mask2

    else:
        mask  = cv2.inRange(hsv, np.array(lowerHSV), np.array(higherHSV))


    final = cv2.bitwise_and(img, img, mask=mask)
    return final