DEBUG_FLAG = True

import win32gui
import cv2 as cv
import numpy as np
import pydirectinput
import win32ui
import win32con
import keyboard
import time
import pickle
from ahk import AHK
import random
import re
import pytesseract
from numpy.random.mtrand import randint
#tesseract imports and pathing
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
ahk = AHK('C:\Program Files\AutoHotkey\AutoHotkey.exe')
#img for openCV processing
target_img = cv.imread('arrow.jpg')
gray_target_img = cv.cvtColor(target_img, cv.COLOR_BGR2GRAY)
#ui element positions
try:
    pkl_file = open('data.pkl', 'rb')
    positions = pickle.load(pkl_file)
    pkl_file.close()
except:
    print('file read error')
I_count = 10 #update whenever adding new values
while len(positions)<I_count:
    positions.append(0)
I_MINIGAME = 0
I_YES1 = 1
I_BUTTON = 2
I_CHOP = 3
I_UPBOUND = 4
I_LOWBOUND = 5
I_TIMER = 6
I_MAXY = 7
I_MINY = 8 #modify I_count whenver adding new values
I_YES2 = 9
#chatbox responses
RESPONES = ['nothing','something close','very','top']

def timerStart():
    global startTime
    startTime = time.monotonic()
def timeElasped():
    global startTime
    return time.monotonic() - startTime

def randomTargetRangeIndex(target_range):
    if len(target_range)==1:
        return 0
    else:
        return randint(0,len(target_range)-1)
    
def configlimits():
    timerStart()
    miny = 10000
    maxy = 0
    while(timeElasped()<3):
        pointer_pos, confidence = locatePointer()
        y = pointer_pos[1]
        if miny>y:
            miny = y
        if maxy<y:
            maxy = y
    print(maxy)
    print(miny)
    global positions
    global I_MINY
    global I_MAXY
    global I_count
    if len(positions)==I_count:
        positions[I_MAXY] = maxy
        positions[I_MINY] = miny
    else:
        positions.append(maxy)
        positions.append(miny)
    #save data
    output = open('data.pkl', 'wb')
    pickle.dump(positions, output)
    output.close()
#ff14 output controls
def mouseMotionClick(xy,rate,clicktype):
    global ahk
    ahk.mouse_move(xy[0],xy[1],speed=rate)
    if clicktype=='right':
        ahk.right_click()
    if clicktype=='left':
        ahk.click()
#ff14 input functions
def locatePointer():
    #capture ff14 image
    global target_hwnd
    global I_UPBOUND
    global I_LOWBOUND
    global positions
    game_img = capture_window(target_hwnd)
    #crop image to scan zone
    topleft = positions[I_UPBOUND]
    bottomright = positions[I_LOWBOUND]
    zone_width = bottomright[0]-topleft[0]
    zone_height = bottomright[1]-topleft[1]
    zone_x = topleft[0]
    zone_y = topleft[1]
    scan_zone = game_img[zone_y:zone_y+zone_height,zone_x:zone_x+zone_width]

    
        #old code for rgb image
    #result = cv.matchTemplate(scan_zone, target_img, cv.TM_CCOEFF_NORMED
    #cv.circle(scan_zone,maxLoc,10,color=(0,255,0))
    #cv.imshow('test',scan_zone)
    #Debug Display 
    #scan_zone = cv.circle(scan_zone,maxLoc,10,color=(255,255,255))
    #cv.imshow('test',scan_zone)
    
        #gray scale image processing
    gray_scan_zone = cv.cvtColor(scan_zone, cv.COLOR_BGR2GRAY)
    th, gray_scan_zone = cv.threshold(gray_scan_zone,150,255,cv.THRESH_BINARY)
    result = cv.matchTemplate(gray_scan_zone, gray_target_img, cv.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
    
    
    #exit conditions
    if DEBUG_FLAG == True:
        gray_scan_zone = cv.circle(gray_scan_zone,maxLoc,10,color=(255,255,255))
        cv.imshow('test',gray_scan_zone)
        cv.waitKey(1)
    return maxLoc, maxVal
            
def readChatResposne(DEBUG = False): #https://stackoverflow.com/questions/28280920/convert-array-of-words-strings-to-regex-and-use-it-to-get-matches-on-a-string for refernce comparing array of strings to string
    global RESPONES
    game_img = capture_window(target_hwnd)
    game_img = game_img[1278:1319,82:486+100]
    #cv.imshow('text', game_img) #debug
    text = pytesseract.image_to_string(game_img)[:-2]
    r = re.compile('|'.join([r'\b%s\b' % w for w in RESPONES]), flags=re.I)
    value = r.findall(text)
    if value:
        if DEBUG:
            print(value)
        return value
    else:
        return [-1]
    

def mousePosLog(key):
    while(True):
        if(keyboard.is_pressed('q')):
            break

    x, y = pydirectinput.position()
    pos_vec = [x,y]
    global positions
    positions.append(pos_vec)
    print(positions)
    #time.sleep(0.25)
    return 

def find_FF(hwnd, result):
    win_text = win32gui.GetWindowText(hwnd)
    if win_text == "FINAL FANTASY XIV":
        global target_hwnd
        target_hwnd = hwnd


#capture image /ripped from https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows
def capture_window(hwnd):
    w = 2560 # set this
    h = 1440 # set this
    #bmpfilenamename = "out.bmp" #set this
    
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)
    #dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)
    # faster image conversion
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h,w,4)
    img = img[...,:3] # remove alpha channel with num slicing
    img = np.ascontiguousarray(img) #solves rectangular draw problems?
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    
    return img