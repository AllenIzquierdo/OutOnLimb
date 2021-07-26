from numpy.f2py.auxfuncs import iscomplexarray
from dearpygui._dearpygui import add_line_series
from mouseinfo import position
DEBUG_FLAG = False

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
import copy
from numpy.random.mtrand import randint
#tesseract imports and pathing
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
ahk = AHK('C:\Program Files\AutoHotkey\AutoHotkey.exe')

#img for openCV processing
target_img = cv.imread('arrow.jpg')
gray_target_img = cv.cvtColor(target_img, cv.COLOR_BGR2GRAY)

#ui element positions
I_count = 16
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
I_IMG_Y_INDEXES = 12
I_IMG_X_INDEXES = 13
I_CHAT_TOPLEFT = 14
I_CHAT_BOTTOMRIGHT = 15

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
    global positions
    global I_MINY
    global I_MAXY
    global I_count
    global xarray
    global yarray
    global I_IMG_X_INDEXES
    global I_IMG_Y_INDEXES
    print('mouse over upperleft')
    mousePosLog(I_UPBOUND)
    print('mouse over edge')
    mousePosLog(I_EDGE)
    print('mouse over lowerRight')
    mousePosLog(I_LOWBOUND)
    p1 = np.array(copy.copy(positions[I_UPBOUND]))
    p2 = np.array(copy.copy(positions[I_EDGE]))
    p1 = np.flip(p1)
    p2 = np.flip(p2)
    p3 = []
    p3.append(p2[0] + p2[0]-p1[0])
    p3.append(p1[1])
    A,B,C = calc_parabola_vertex(p1,p2,p3)
    yi = np.arange(p1[0],p3[0]+1)
    yi = yi.astype(int)
    parabolaoutput = A*yi**2+B*yi+C
    parabolaoutput = parabolaoutput.round()
    parabolaoutput = parabolaoutput.astype(int)
    positions[I_IMG_Y_INDEXES] = yi
    positions[I_IMG_X_INDEXES] = parabolaoutput
    print(positions[I_IMG_Y_INDEXES])
    print(positions[I_IMG_X_INDEXES])

    timerStart()
    miny = 10000
    maxy = 0
    timerStart()
    yarray = []
    while(timeElasped()<3):
        y,health,gray_scan_line = locatePointer()
        if y==-1:
            continue
        if miny > y:
            miny = y
        if maxy < y:
            maxy = y
        yarray.append(y)
    xarray = list(range(1,len(yarray)))
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
def calc_parabola_vertex(p1, p2, p3):
        '''
        Adapted and modifed to get the unknowns for defining a parabola:
        http://stackoverflow.com/questions/717762/how-to-calculate-the-vertex-of-a-parabola-given-three-points
        '''
        x1 = p1[0]
        x2 = p2[0]
        x3 = p3[0]
        y1 = p1[1]
        y2 = p2[1]
        y3 = p3[1]
        denom = (x1-x2) * (x1-x3) * (x2-x3);
        A     = (x3 * (y2-y1) + x2 * (y1-y3) + x1 * (y3-y2)) / denom;
        B     = (x3*x3 * (y1-y2) + x2*x2 * (y3-y1) + x1*x1 * (y2-y3)) / denom;
        C     = (x2 * x3 * (x2-x3) * y1+x3 * x1 * (x3-x1) * y2+x1 * x2 * (x1-x2) * y3) / denom;

        return A,B,C
def locatePointer():
    #capture ff14 image
    global target_hwnd
    global I_UPBOUND
    global I_LOWBOUND
    global positions
    game_img = capture_window(target_hwnd)#largest performance eater by far
        #crop image to scan zone for pointer
    gray_game_img = cv.cvtColor(game_img, cv.COLOR_BGR2GRAY)
    th, gray_scan = cv.threshold(gray_game_img,230,255,cv.THRESH_BINARY)
    index = 0
    xindexes = positions[I_IMG_X_INDEXES]
    yindexes = positions[I_IMG_Y_INDEXES]
    gray_scan_line = [None]*len(xindexes)
    while index<len(xindexes):
        gray_scan_line[index] = gray_scan[yindexes[index],xindexes[index]]
        index+=1
    location = np.argmax(gray_scan_line)
    #print(gray_scan_line)
    # retrusn locaiton=-1 on target not found
    if(gray_scan_line[location]==0):
        location = -1

    #obtain health info
    healthpos = positions[I_HEALTH]
    health =  game_img[healthpos[1],healthpos[0],1]
    #exit conditions
    return location,health,gray_scan_line

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
    #WARNING BIG PROBLEM MAYBE
    #img = np.ascontiguousarray(img) #solves rectangular draw problems?
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    
    return img