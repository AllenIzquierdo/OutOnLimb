#TODO ADD VELOCITY PREDICTION
#TODO ADD ZONE 1 (early spam) assist
#TOSS HIGH ERROR RESULTS
#
from testfunctions import *
import os
import copy
from pointassist import *

#some chat constants
#[[82, 1319] bottom left
#[486, 1278] top right
#setup timer
startTime = 0
TARGET_COMPARISON_F = False
TARGET_RANGE_EDIT_F = False
initial_timer_dict = {}
delay_timer_dict = {}
delay_timer_flipflop = {}
def startTimerDict(string_index):
    global initial_timer_dict
    global delay_timer_dict
    global delay_timer_flipflop
    initial_timer_dict[string_index] = time.monotonic()

def getTimerDict(string_index):
    global initial_timer_dict
    global delay_timer_dict
    global delay_timer_flipflop
    return time.monotonic() - initial_timer_dict[string_index]

def setTimerDelayDict(string_index, time_to_delay):
    global initial_timer_dict
    global delay_timer_dict
    global delay_timer_flipflop 
    startTimerDict(string_index)
    delay_timer_dict[string_index] = time_to_delay
    delay_timer_flipflop[string_index] = False

def flipflopDelayTimer(string_index):
    global initial_timer_dict
    global delay_timer_dict 
    global delay_timer_flipflop
    if string_index in delay_timer_flipflop.keys():
        timeelasped = getTimerDict(string_index)
        if delay_timer_flipflop[string_index]==False and timeelasped>delay_timer_dict[string_index]:

            delay_timer_flipflop[string_index] = True
            return True
        else:
            return False
    else:
        return False
        
#find target window
target_hwnd = 0
win32gui.EnumWindows(find_FF, target_hwnd)





# shared global variables
inter_pos = []
cv_confidence = 0;
prev_percent = 0
#start program
while(True):
    command = input('Await your command:')
    #full config setup command
    if command == 'testtimer':
        setTimerDelayDict('test1', 5)

    if command == 'config':
        try:
            os.remove('data.pkl')
        except FileNotFoundError:
            print('file not found')
        print('mouse over minigame')
        mousePosLog(I_MINIGAME)
        print('mouse over yes1')
        mousePosLog(I_YES1)
        print('mouse over button')
        mousePosLog(I_BUTTON)
        print('mouse over chop')
        mousePosLog(I_CHOP)
        print('mouse over health')
        mousePosLog(I_HEALTH)
        print('mouse over upperleft')
        mousePosLog(I_UPBOUND)
        print('mouse over edge')
        mousePosLog(I_EDGE)
        print('mouse over lowerRight')
        mousePosLog(I_LOWBOUND)
        print('mouse over timer')
        mousePosLog(I_TIMER)
        #config limits
        print('configuring limits')
        configlimits()
        print('mouse over yes2')
        mousePosLog(I_YES2)
        #save data
        output = open('data.pkl', 'wb')
        pickle.dump(positions, output)
        output.close()
        
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
        targetRange = 0.15
        cur_time = 0
        
        chatReadDelay = 2.8
        #variables to be reset every loop
        targets = generateSearchPoints(0,1,includeExtremes=True)
        target = targets.pop(0)
        hotspotlevel = 0 
        hotspotlocations = [0,0]
        timerStart()
        score = 0 # 10 points is donezo
        wins = 0
        attempts = 0
        loopTimeOut = 75
        idle_pointer_percent = 0
        targetAquiredFlag = False
        MONITOR_RESET_FLAG = False
        health = 1
        gamerestartDelay = 1.2
        gamestartDelay = 0.9
        time.sleep(gamestartDelay)
        while(True):
            if(keyboard.is_pressed('q')):
                break
            
                #update OPENCV IMAGE
            y, health, gray_scale_line= locatePointer()
                #reset process
            if  attempts>=10 or timeElasped()>75 or health<120:
                wins+=1
                time.sleep(0.8)
                print('wins:' + str(wins))
                if wins==4 or timeElasped()>60 or attempts>=10:
                    time.sleep(1)
                    I_NO = copy.copy(positions[I_YES2])
                    I_NO[0] = I_NO[0]+80
                    mouseMotionClick(I_NO,14,'left')
                    time.sleep(1)
                    mouseMotionClick(positions[I_MINIGAME],10,'right')
                    mouseMotionClick(positions[I_YES1],10,'left')
                    time.sleep(2)
                    mouseMotionClick(positions[I_BUTTON],10,'left')
                    mouseMotionClick(positions[I_CHOP],10,'none')
                    miny = positions[I_MINY]
                    maxy = positions[I_MAXY]
                    timerStart()
                    time.sleep(gamestartDelay)
                    wins = 0
                else:
                    mouseMotionClick(positions[I_YES2],10,'none')
                    time.sleep(gamerestartDelay)
                    ahk.click();
                    time.sleep(0.1)
                    mouseMotionClick(positions[I_CHOP],1,'none')
                target_hotspot = -1 #reset hotspot for next loop
                #MONITOR_RESET_FLAG = False
                attempts=0
                score = 0
                targets = generateSearchPoints(0,1,includeExtremes=True)
                target = targets.pop(0)
                hotspotlevel = 0 
                hotspotlocations = [0,0]
                MONITOR_RESET_FLAG = False
                targetAquiredFlag = False

                #protect against errors
            prev_time = cur_time
            cur_time = time.monotonic()
            frame_time = cur_time-prev_time
            percent = (y-miny)/(maxy-miny)
            
            if(target-targetRange)<percent and percent<(target+targetRange):
                prev_percent = percent;
                if targetAquiredFlag == False:
                    ahk.click()
                    setTimerDelayDict('locatepointer', chatReadDelay)
                    targetAquiredFlag = True
            
            if target<=0.2:
                ahk.click()
                

            #prevents timer spam with flipflop logic
            if MONITOR_RESET_FLAG:
                if percent!=idle_pointer_percent:
                    targetAquiredFlag = False
                    MONITOR_RESET_FLAG = False
                
            #find pointer->retrive chat log->update target information
            if flipflopDelayTimer('locatepointer') or timeElasped()>75 or health<120:
                print('reading chat')
                targeterror = percent-target
                print('result: '+str(round(percent,3))+' err: ' +str(round(targeterror,3)) + ' target ' +str(round(target,3)))
                idle_pointer_percent = percent;
                
                #retrieve chat feedback
                response = readChatResposne()
                tries = 0;
                while response==-1:
                    time.sleep(0.2)
                    response = readChatResposne()
                    tries+=1
                    if tries>4:
                        response = ['big err']
                        break;
                #response #originally 2readchat 1.2 for reset
                ## Updates Target_Range information and assigns new target
                indx = 0;
                print(response[0]);
                if response[0]=='nothing':
                    score+=0
                if response[0]=='something close':
                    score+=1
                    if hotspotlevel<1:
                        hotspotlevel = 1
                        targets = generateSearchPoints(-2, 2, hitmarker=percent, rangemarker=0.4)
                        hotspotlocations[0] = percent
                if response[0]=='very':
                    score+=4
                    if hotspotlevel<2:
                        hotspotlevel = 2
                        targets = generateSearchPoints(-2, 2, hitmarker=percent, rangemarker=0.2)
                        hotspotlocations[1] = percent
                if response[0]=='top':
                    score+=10

                if len(targets)>0:
                    target = targets.pop(0)
                else:
                    if hotspotlocations[1]:
                        target = hotspotlocations[1]
                attempts+=1
                print('score :' + str(score) + ' timer: ' + str(round(timeElasped())) + ' attempts: '+str(attempts))
                MONITOR_RESET_FLAG = True
                #######
                ## SCORING And RESETTING
                ##
                ########
                print('health: '+str(health))
                print("CVFPS: %3.2f, Frametime(ms): %3.2f" % (1/frame_time,frame_time*1000))
                print('Next Target :' + str(target))
                print(targets)
                if(abs(targeterror)>0.3):
                    print(gray_scale_line)
                print('\n')
    #example of reading chat
    if command == 'readchat':
        readChatResposne()
        
    #main loop
    if command == 'configlimits':
        configlimits();
    if command == 'readhp':
        game_img = capture_window(getFF14())#largest performance eater by far
        healthpos = positions[I_HEALTH]
        print(game_img[healthpos[1],healthpos[0],1])
        
        
        
        
        
        