#TODO ADD VELOCITY PREDICTION
#TODO ADD ZONE 1 (early spam) assist
#TOSS HIGH ERROR RESULTS
#
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
#tesseract imports

import pytesseract


DEBUG_FLAG = True

#some chat constants
#[[82, 1319] bottom left
#[486, 1278] top right


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
#setup timer
startTime = 0
def timerStart():
    global startTime
    startTime = time.monotonic()
def timeElasped():
    global startTime
    return time.monotonic() - startTime

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
            
def readChatResposne(): #https://stackoverflow.com/questions/28280920/convert-array-of-words-strings-to-regex-and-use-it-to-get-matches-on-a-string for refernce comparing array of strings to string
    global RESPONES
    game_img = capture_window(target_hwnd)
    game_img = game_img[1278:1319,82:486+100]
    #cv.imshow('text', game_img) #debug
    text = pytesseract.image_to_string(game_img)[:-2]
    r = re.compile('|'.join([r'\b%s\b' % w for w in RESPONES]), flags=re.I)
    value = r.findall(text)
    if value:
        print(value)
        return value
    else:
        return -1
    

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
#initiate tesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#find target window
target_hwnd = 0
win32gui.EnumWindows(find_FF, target_hwnd)

target_img = cv.imread('arrow.jpg')
gray_target_img = cv.cvtColor(target_img, cv.COLOR_BGR2GRAY)
find_needle = False;

ahk = AHK('C:\Program Files\AutoHotkey\AutoHotkey.exe')

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
BULLSEYE = "You're right on top of it!"
MISS = 'You sense nothing.'
START = 'You take up your hatchet.'
NEAR = 'You sense something close.'
VERYNEAR = 'You sense something very close.'
#RESPONES = [START, MISS, NEAR, VERYNEAR,BULLSEYE]
RESPONES = ['nothing','something close','very','top']

#start program
while(True):
    command = input('Await your command:')
    #full config setup command
    if command == 'config':
        positions = []
        print('mouse over minigame')
        mousePosLog('q')
        print('mouse over yes1')
        mousePosLog('2')
        print('mouse over button')
        mousePosLog('3')
        print('mouse over chop')
        mousePosLog('4')
        print('mouse over upperleft')
        mousePosLog('5')
        print('mouse over lowerRight')
        mousePosLog('5')
        print('mouse over timer')
        mousePosLog('5')
        #config limits
        print('configuring limits')
        configlimits()
        
        print('mouse over yes2')
        mousePosLog('6')
        
        #save data
        output = open('data.pkl', 'wb')
        pickle.dump(positions, output)
        output.close()
    #if command == 'configlimits':
        
    if command == 'print config':
        print(positions)
        
    if command == 'quit':
        break
    
    #example of clicking
    if command == 'init':
        time.sleep(1)
        mouseMotionClick(positions[I_MINIGAME],10,'right')
        mouseMotionClick(positions[I_YES1],10,'left')
        time.sleep(2)
        mouseMotionClick(positions[I_BUTTON],10,'left')
        mouseMotionClick(positions[I_CHOP],10,'none')
        miny = positions[I_MINY]
        maxy = positions[I_MAXY]
        targetRange = 0.1
        target = 0.5
        target_range = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        timerStart()
        score = 0 # 10 points is donezo
        while(timeElasped()<90):
            #loop to find targets
            pointer_pos, confidence = locatePointer()
            y = pointer_pos[1]
            percent = (y-miny)/(maxy-miny)
            if(target-targetRange)<percent and percent<(target+targetRange):
                prev_percent = percent;
                ahk.click()
                time.sleep(0.7)
                #update pointer pos and report err
                pointer_pos, confidence = locatePointer()
                pointer_pos, confidence = locatePointer()
                y = pointer_pos[1]
                percent = (y-miny)/(maxy-miny)
                percentRounded = round(percent,1) #initinit to nearest tenth
                if percentRounded==0:
                    percentRounded = 0.1
                if percent==1:
                    percentRounded = 0.9
                print('result '+str(percent))
                print('err: ' +str(percent-prev_percent))
                
                #response
                time.sleep(1.7)
                response = readChatResposne()
                tries = 0;
                while response==-1:
                    time.sleep(0.2)
                    response = readChatResposne()
                    tries+=1
                    if tries>4:
                        break;
                #Reposne Actions
                indx = 0;
                if response[0]=='nothing':
                    print('elim around: ' +str(percent))
                    tError = False
                    while indx<len(target_range):
                        if abs(target_range[indx]-percent)<0.16:
                            print('val: '+str(target_range[indx])+' percent: '+str(percent))
                            print('indx '+str(indx)+' target_range: '+str(target_range))
                            elim = target_range.pop(indx)
                            
                        else:
                            indx+=1;
                    
                        
                    ## Added Section Above
                    
                    target = target_range[random.randint(0,len(target_range)-1)]
                    print('\n')

                    
                if response[0]=='something close':
                    Error = False
                    score+=1
                    while indx<len(target_range):
                        if abs(target_range[indx]-percent)>0.27:
                            print('val: '+str(target_range[indx])+' percent: '+str(percent))
                            print('indx '+str(indx)+' target_range: '+str(target_range))
                            elim = target_range.pop(indx)
                            print('eliminted '+str(elim))
                        else:
                            indx+=1;
                    
                        
                    ## Added Section Above
                    
                    target = target_range[random.randint(0,len(target_range)-1)]
                    print('\n')
                    print(target_range)

                if response[0]=='very':
                    Error = False
                    score+=4
                    while indx<len(target_range):
                        if abs(target_range[indx]-percent)>0.17:
                            print('val: '+str(target_range[indx])+' percent: '+str(percent))
                            print('indx '+str(indx)+' target_range: '+str(target_range))
                            elim = target_range.pop(indx)
                            print('eliminted '+str(elim))
                        else:
                            indx+=1;
                    
                        
                    ## Added Section Above
                    
                    target = target_range[random.randint(0,len(target_range)-1)]
                    print('\n')
                    print(target_range)
                if response[0]=='top':
                    score+=10
                
                if score>=10:
                    score=0
                    time.sleep(2.3)
                    mouseMotionClick(positions[I_YES2],10,'left')
                    mouseMotionClick(positions[I_CHOP],10,'none')
                    targetRange = 0.1
                    target = 0.5
                    target_range = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
            
    #example of reading chat
    if command == 'readchat':
        readChatResposne()
        
    #main loop
    if command == 'configlimits':
        configlimits();

        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    """
    if command == 'start':
        while(True):
            #capture ff14 image
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
                #gray scale image processing
            gray_scan_zone = cv.cvtColor(scan_zone, cv.COLOR_BGR2GRAY)
            th, gray_scan_zone = cv.threshold(gray_scan_zone,150,255,cv.THRESH_BINARY)
            result = cv.matchTemplate(gray_scan_zone, gray_target_img, cv.TM_CCOEFF_NORMED)
            minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
            
            #Debug Display
            gray_scan_zone = cv.circle(gray_scan_zone,maxLoc,10,color=(255,255,255))
            #scan_zone = cv.circle(scan_zone,maxLoc,10,color=(255,255,255))
            cv.imshow('test',gray_scan_zone)
            #cv.imshow('test',scan_zone)
            print(maxVal)
            #exit conditions
            if cv.waitKey(1) == ord('q'):
                cv.destroyAllWindows()
                break
        
    """    
        
