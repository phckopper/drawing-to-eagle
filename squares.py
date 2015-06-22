#!/usr/bin/env python

'''
Simple "Square Detector" program.

Loads several images sequentially and tries to find squares in each image.

NOW MODIFIED TO PLACE RESISTORS ON EAGLE UHUUUUUUUUUUUU
by @phckopper
'''

import xml.etree.ElementTree as ET
doc = ET.parse('base.sch')
root = doc.getroot()


import numpy as np
import cv2

def aspect_ratio(cnt):
    x,y,w,h = cv2.boundingRect(cnt)
    return float(w)/h

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_squares(img):
    img = cv2.GaussianBlur(img, (9, 9), 0)
    squares = []
    for gray in cv2.split(img):
        for thrs in xrange(20, 200, 2):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            bin, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.025*cnt_len, True)
                if len(cnt) == 4 and 700 > cv2.contourArea(cnt) > 100 and cv2.isContourConvex(cnt) and (4.3 > aspect_ratio(cnt) > 1.8 or 0.7 > aspect_ratio(cnt) > 0.3):
                    up = 0.7 > aspect_ratio(cnt) > 0.3
                    
                    cnt = cnt.reshape(-1, 2)
                    
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.15:
                        squares.append([cnt, up])
    return squares

if __name__ == '__main__':
    import sys
    for fn in sys.argv[1:]:
        print fn
        original_img = cv2.imread(fn)
        img = cv2.resize(original_img, (800, 640)) 
        squares = find_squares(img)
        cv2.drawContours( img, [sq[0] for sq in squares], -1, (0, 255, 0), 3 )


        old = []
        i = 1
        for sq in squares:
            x = sq[0][0][0]
            y = sq[0][0][1]
            is_old = len([j for j in old if (x - 2) < j < (x + 2)]) > 0
            #print is_old

            if not is_old:
                old.append(x)
                print 'appended'

                r = { 
                    'name': "R" + str(i),
                    'library': "resistor",
                    'deviceset': "R-EU_",
                    'device': "0204/7"
                }
                ET.SubElement(root[0][3][4], 'part', attrib=r)

                instance = {
                    'part': "R" + str(i),
                    'gate': "G$1",
                    'x': str(x//3),
                    'y': str(y//3 * -1) 
                }
                if sq[1]:
                    instance['rot'] = "R90"

                ET.SubElement(root[0][3][5][0][1], 'instance', attrib=instance)

                i += 1

                print x//3, y//3


        doc.write(fn.split('.')[0] + '.sch')
        cv2.imshow('squares', img)
        ch = 0xFF & cv2.waitKey()
        if ch == 27:
            break
    cv2.destroyAllWindows()
