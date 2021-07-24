DEBUG_FLAG = True
#resolutions
w_resolution = 2560 # set this
h_resolution = 1440 # set this
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
import os
from numpy.random.mtrand import randint
#tesseract imports and pathing
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
ahk = AHK('C:\Program Files\AutoHotkey\AutoHotkey.exe')
#img for openCV processing
target_img = cv.imread('arrow.jpg')
gray_target_img = cv.cvtColor(target_img, cv.COLOR_BGR2GRAY)
#ui element positions
I_count = 14
try:
    pkl_file = open('data.pkl', 'rb')
    positions = pickle.load(pkl_file)
    pkl_file.close()
    while(len(positions)<I_count):
        positions.append(None)
    print(positions)
except:
    print('file read error')
    positions = [None]*I_count
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
I_CONGRATS_TOPLEFT = 10
I_CONGRATS_BOTTOMRIGHT= 11
I_CHAT_TOPLEFT = 12
I_CHAT_BOTTOMRIGHT = 13
#chatbox responses
RESPONES = ['nothing','something close','very','top']
def getFF14():
    global target_hwnd
    return target_hwnd
def saveconfig():
    try:
        os.remove('data.pkl')
    except FileNotFoundError:
        print('file not found')
    output = open('data.pkl', 'wb')
    pickle.dump(positions, output)
    output.close()
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
    positions[I_MAXY] = maxy
    positions[I_MINY] = miny
    #save data
    #output = open('data.pkl', 'wb')
    #pickle.dump(positions, output)
    #output.close()
    saveconfig()
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
        #prev thres values, 150 (ok)
    gray_scan_zone = cv.cvtColor(scan_zone, cv.COLOR_BGR2GRAY)
    th, gray_scan_zone = cv.threshold(gray_scan_zone,200,255,cv.THRESH_BINARY)
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
    #game_img = game_img[1278:1319,82:486+100]
    #topleft = [82,1278]
    #bottomright = [586,1319]
    topleft = positions[I_CHAT_TOPLEFT]
    bottomright = positions[I_CHAT_BOTTOMRIGHT]
    value = readBoxKeywords(topleft,bottomright, game_img, RESPONES, DEBUG, SHOW_IMG = True)
    if value:
        if DEBUG:
            print(value)
        return value
    else:
        return [-1]
    
def readBoxKeywords(topleft, bottomright, image, keywords="", DEBUG = False, SHOW_IMG = False): #https://stackoverflow.com/questions/28280920/convert-array-of-words-strings-to-regex-and-use-it-to-get-matches-on-a-string for refernce comparing array of strings to string

    image = image[topleft[1]:bottomright[1],topleft[0]:bottomright[0]]
    image = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    image = cv.threshold(image, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]
    if SHOW_IMG:
        cv.imshow('readBoxKeywords',image)
        cv.waitKey(1)
    text = pytesseract.image_to_string(image) #probably dont need deliminator anymore
    #r = re.compile('|'.join([r'\b%s\b' % w for w in keywords]), flags=re.I)
    #value = r.findall(text)
    value = [None]
    index = 0
    while index < len(keywords):
        if keywords[index] in text:
            value[0] = keywords[index]
            break
        index+=1
    if DEBUG:
        print(text)
        if value:
            print(value[0])
    if value:
        return value
    else:
        return [-1]

def quarymosue():
    while(True):
        if(keyboard.is_pressed('q')):
            break
    x, y = pydirectinput.position()
    pos_vec = [x,y]
    time.sleep(0.25)
    return pos_vec
def defineChatBox(image):
    #for ff14 game_img = capture_window(target_hwnd)
    topleft = [0,0]
    bottomright = [0,0]
    while(True):
        print('topleft of box')
        topleft = quarymosue()
        print(topleft)
        print('bottomright of box')
        bottomright = quarymosue()
        print(bottomright)
        readBoxKeywords(topleft, bottomright, image, SHOW_IMG = True)
        command = input('satisfied y/n:')
        if command == 'y':
            break
    return topleft, bottomright

def mousePosLog(key):
    
    while(True):
        if(keyboard.is_pressed('q')):
            break

    x, y = pydirectinput.position()
    pos_vec = [x,y]
    global positions
    positions.append(pos_vec)
    print(positions)
    time.sleep(0.25)
    return 

def find_FF(hwnd, result):
    win_text = win32gui.GetWindowText(hwnd)
    if win_text == "FINAL FANTASY XIV":
        global target_hwnd
        target_hwnd = hwnd


#capture image /ripped from https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows
def capture_window(hwnd):
    #bmpfilenamename = "out.bmp" #set this
    global w_resolution 
    global h_resolution
    
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w_resolution, h_resolution)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(w_resolution, h_resolution) , dcObj, (0,0), win32con.SRCCOPY)
    #dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)
    # faster image conversion
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h_resolution,w_resolution,4)
    img = img[...,:3] # remove alpha channel with num slicing
    img = np.ascontiguousarray(img) #solves rectangular draw problems?
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    
    return img