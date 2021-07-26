DEBUG_FLAG = False

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
I_count = 12
I_MINIGAME = 0
I_YES1 = 1
I_BUTTON = 2
I_CHOP = 3
I_UPBOUND = 4
I_EDGE = 5
I_LOWBOUND = 6
I_TIMER = 7
I_MAXY = 8
I_MINY = 9 #modify I_count whenver adding new values
I_YES2 = 10
I_HEALTH = 11
try:
    pkl_file = open('data.pkl', 'rb')
    positions = pickle.load(pkl_file)
    pkl_file.close()
    print(positions)
except:
    print('file read error')
    positions = [None]*I_count
#chatbox responses
RESPONES = ['nothing','something close','very','top']

def getFF14():
    global target_hwnd
    return target_hwnd
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
    print('mouse over upperleft')
    mousePosLog(I_UPBOUND)
    print('mouse over edge')
    mousePosLog(I_EDGE)
    print('mouse over lowerRight')
    mousePosLog(I_LOWBOUND)

    timerStart()
    miny = 10000
    maxy = 0
    timerStart()
    while(timeElasped()<3):
        y,health,gray_scan_line = locatePointer()
        if miny > y:
            miny = y
        if maxy < y:
            maxy = y
        
    global positions
    global I_MINY
    global I_MAXY
    global I_count
    if len(positions) < I_count:
        positions.append(miny)
        positions.append(miny)
    else:
        positions[I_MAXY] = maxy
        positions[I_MINY] = miny
    #save data
    #output = open('data.pkl', 'wb')
    #pickle.dump(positions, output)
    #output.close()
    try:
        os.remove('data.pkl')
    except FileNotFoundError:
        print('file not found')
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
    game_img = capture_window(target_hwnd)#largest performance eater by far
        #crop image to scan zone for pointer
    top = positions[I_UPBOUND][1]
    bottom = positions[I_LOWBOUND][1]
    edge = positions[I_EDGE][0]
    scan_zone = game_img[top:bottom,edge:edge+1]
    gray_scan_zone = cv.cvtColor(scan_zone, cv.COLOR_BGR2GRAY)
    th, gray_scan_zone = cv.threshold(gray_scan_zone,230,255,cv.THRESH_BINARY)
    gray_scan_line = gray_scan_zone[:,0]
    location = np.argmax(gray_scan_line)
    # retrusn locaiton=-1 on target not found
    if(gray_scan_line[location]==0):
        location = -1

    #obtain health info
    healthpos = positions[I_HEALTH]
    health =  game_img[healthpos[1],healthpos[0],1]
    #exit conditions
    if DEBUG_FLAG == True:
        #gray_scan_zone = cv.circle(gray_scan_zone,maxLoc,10,color=(255,255,255))
        cv.imshow('test',gray_scan_zone)
        cv.waitKey(1)
    return location,health,gray_scan_line
            
def readChatResposne(DEBUG = False): #https://stackoverflow.com/questions/28280920/convert-array-of-words-strings-to-regex-and-use-it-to-get-matches-on-a-string for refernce comparing array of strings to string
    global RESPONES
    game_img = capture_window(target_hwnd)
    game_img = game_img[1278:1319,82:486+100]
    game_img = cv.cvtColor(game_img,cv.COLOR_BGR2GRAY)
    game_img = cv.threshold(game_img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]
    #cv.imshow('hellotext',game_img)
    #cv.waitKey(1)
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
    

def mousePosLog(index):
    while(True):
        if(keyboard.is_pressed('q')):
            break

    x, y = pydirectinput.position()
    pos_vec = [x,y]
    global positions
    positions[index] = pos_vec
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
    #WARNING BIG PROBLEM MAYBE
    #img = np.ascontiguousarray(img) #solves rectangular draw problems?
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    
    return img