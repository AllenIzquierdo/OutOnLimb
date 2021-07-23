#TODO ADD VELOCITY PREDICTION
#TODO ADD ZONE 1 (early spam) assist
#TOSS HIGH ERROR RESULTS
#
from testfunctions import *




#some chat constants
#[[82, 1319] bottom left
#[486, 1278] top right
#setup timer
startTime = 0
TARGET_COMPARISON_F = False
TARGET_RANGE_EDIT_F = False
NUM_OF_TIMERS = 10
initial_timer_dict = {}
delay_timer_dict = {}
def startTimerDict(string_index):
    initial_timer_dict[string_index] = time.monotonic()

def getTimerDict(string_index):
    return time.monotonic() - initial_timer_dict[string_index]

def setTimerDelayDict(string_index, time_to_delay):
    startTimerDict(string_index)
    delay_timer_dict[string_index] = time_to_delay



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
        
    if command == 'print config':
        print(positions)
        
    if command == 'quit':
        break
    
    #example of clicking
    if command == 'init':
        #time.sleep(1)
        mouseMotionClick(positions[I_MINIGAME],10,'right')
        mouseMotionClick(positions[I_YES1],10,'left')
        #time.sleep(2)
        mouseMotionClick(positions[I_BUTTON],10,'left')
        mouseMotionClick(positions[I_CHOP],10,'none')
        miny = positions[I_MINY]
        maxy = positions[I_MAXY]
        targetRange = 0.1
        target = 0.5
        target_range = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
        timerStart()
        score = 0 # 10 points is donezo
        cur_time = 0
        wins = 0
        attempts = 0
        loopTimeOut = 75
        while(True):
            pointer_pos, cv_confidence = locatePointer()
                #update OPENCV IMAGE
            if target == 0.1 or target==0.2 and timeElasped()<loopTimeOut:
                bool_enableTargetEdit = True
                prev_time = cur_time
                cur_time = time.monotonic()
                frame_time = cur_time-prev_time
                print('CVFPS: ' + str(1/frame_time))
                #print("CVFPS: %3.2f, Frametime(ms): %3.2f" % (1/frame_time,frame_time*1000))
                
                y = pointer_pos[1]
                percent = (y-miny)/(maxy-miny)
                
                if TARGET_COMPARISON_F:
                    if(target-targetRange)<percent and percent<(target+targetRange):
                        bool_enableTargetEdit = True
                        prev_percent = percent;
                        ahk.click()
                        setTimerDelayDict('delayPointerCheck', frame_time)
                      
                y = pointer_pos[1]
                percent = (y-miny)/(maxy-miny)
                print('result '+str(percent))
                targeterror = percent-prev_percent
                print('err: ' +str(targeterror))
                if abs(targeterror)>0.2:
                    bool_enableTargetEdit = False;
                 
                #response #originally 2readchat 1.2 for reset
                #time.sleep(2.4)
                response = [-1]
                """ #isloated the performance killer
                response = readChatResposne(True)
                
                tries = 0;
                while response==-1:
                    #time.sleep(0.2)
                    response = readChatResposne()
                    tries+=1
                    if tries>4:
                        response = ['big err']
                        break;
                if abs(targeterror)>0.2:
                    bool_enableTargetEdit = False;
                #Reposne Actions
                """
                        
                ######
                ## Manages Mapping of Hidden Zone by text response
                ## 
                ##
                #####
                if TARGET_RANGE_EDIT_F:
                    if abs(targeterror)>0.2:
                        bool_enableTargetEdit = False;
                    #Reposne Actions
                    indx = 0;
                    if response[0]=='nothing':
                        print('elim around: ' +str(percent))
                        if bool_enableTargetEdit:
                            while indx<len(target_range):
                                if abs(target_range[indx]-percent)<0.16:
                                    print('val: '+str(target_range[indx])+' percent: '+str(percent))
                                    print('indx '+str(indx)+' target_range: '+str(target_range))
                                    target_range.pop(indx)
                                else:
                                    indx+=1
                            Target = random.choice(target_range)
                            print(target_range)
                            print('\n')
                        
                    if response[0]=='something close':
                        score+=1
                        if bool_enableTargetEdit:
                            while indx<len(target_range):
                                if abs(target_range[indx]-percent)>0.27:
                                    print('val: '+str(target_range[indx])+' percent: '+str(percent))
                                    print('indx '+str(indx)+' target_range: '+str(target_range))
                                    target_range.pop(indx)
                                else:
                                    indx+=1
                            #prev_target = target
                            #while prev_target==target and len(target_range)>1: #suspect code
                            #    target = target_range[randomTargetRangeIndex(target_range)]
                            #    print('stuck in inf loop~355')
                            target = random.choice(target_range)                       
                            print(target_range)
                            print('\n')
                        

                    if response[0]=='very':
                        score+=4
                        if bool_enableTargetEdit:
                            while indx<len(target_range):
                                if abs(target_range[indx]-percent)>0.17:
                                    print('val: '+str(target_range[indx])+' percent: '+str(percent))
                                    print('indx '+str(indx)+' target_range: '+str(target_range))
                                    target_range.pop(indx)
                                else:
                                    indx+=1;
                            #target = target_range[randomTargetRangeIndex(target_range)]
                            target = target #lets try to keep the same target for these guys
                            print(target_range)
                            print('\n')
                
                #######
                ## SCORING And RESETTING
                ##
                ########
                if response[0]=='top':
                    score+=10
                
                if score>=10 and timeElasped()>60 or attempts>=10 or score>=10 or timeElasped()>75:
                    
                    wins+=1
                    time.sleep(0.8)
                    print('wins:' + str(wins))
                    if wins==4 or timeElasped()>60 or attempts>=10:
                        time.sleep(1)
                        I_NO = copy.copy(positions[I_YES2])
                        I_NO[0] = I_NO[0]+75
                        mouseMotionClick(I_NO,10,'left')
                        time.sleep(1)
                        mouseMotionClick(positions[I_MINIGAME],10,'right')
                        mouseMotionClick(positions[I_YES1],10,'left')
                        time.sleep(2)
                        mouseMotionClick(positions[I_BUTTON],10,'left')
                        mouseMotionClick(positions[I_CHOP],10,'none')
                        miny = positions[I_MINY]
                        maxy = positions[I_MAXY]
                        timerStart()
                        wins = 0
                    else:
                        mouseMotionClick(positions[I_YES2],10,'left')
                        mouseMotionClick(positions[I_CHOP],1,'none')
                    attempts=0
                    score = 0
                    targetRange = 0.1
                    target = 0.5
                    target_range = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    #example of reading chat
    if command == 'readchat':
        readChatResposne()
        
    #main loop
    if command == 'configlimits':
        configlimits();
        
