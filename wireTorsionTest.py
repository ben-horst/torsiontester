import time
from datetime import datetime
import os
import matplotlib.pyplot as plt
import mtt03
import servo_control
import keyboard
import threading
import queue

def getNow():
    n = datetime.now()
    now = n.strftime("%d/%m/%Y %H:%M:%S")
    return now

def castCheck(num):
    try:
        num = int(num)
    except ValueError:
        print("Invalid input, please enter integer.")
        return False
    else:
        return True

def getInput(prompt):
    inputBool = False
    while inputBool == False:
        value = input(prompt)
        inputBool = castCheck(value)
    return int(value)

def createDir(folderName):
    path = folderName
    if not os.path.exists(path): # check whether directory already exists
        os.mkdir(path)

def printHeader(logFile):
    logFile.write("Test: "+testName+"\n")
    logFile.write("Start time: "+startTime+"\n")
    logFile.write("Speed: "+str(speed)+"\n")#+" degrees/s"+"\n")
    logFile.write("Reading\t"+"Angle [pos]\t"+"Angle [deg]\t"+"Current Deg\t"+"Torque\t"+"Torque Unit\t"+"Speed [deg/s]\n")

def getMotorSpeed(degPerSec): # TODO: WRITE THIS FUNCTION! WRITE THIS FUNCTION! WRITE THIS FUNCTION! WRITE THIS FUNCTION!
    motorSpeed = degPerSec # update this once motor is calibrated
    return motorSpeed

def predictNextPoint(set):  #takes a set of points and predicts what the next point should be 
    diffs = []
    for i in range(len(set)-1):
        diffs.append(set[i+1] - set[i])
    avg_diff = sum(diffs) / len(diffs)
    next_val = set[-1] + avg_diff
    return next_val
    
def filterRawPositionData(new_point, last_20_filtered, in_bad):   #takes a new raw point takes last 20 filtered position points, and returns the filtered point
    #If the values are greater than 1194 or less than -194, it's in the weird part of the servo's reporting
    if new_point > 1185:   # a little buffer before the 1194 point where it reports weird data
        in_bad = True
    elif new_point < -185:  #once it's back here, things are good again
        in_bad = False
    if in_bad:
        filtered_point = predictNextPoint(last_20_filtered)
    else:
        filtered_point = new_point
    return filtered_point, in_bad

def servoDeg(value): # calculates angle in degrees from angle value
    angle = 360 * (value + 250) / 1500 
    return round(angle,2)

def absDeg(value, startValue, rev=0):
    if value >= startValue:
        angle = value-startValue
    elif value < startValue:
        angle = value-startValue+360#value+startValue
    else:
        angle = -1000
    angle += rev*360
    return round(angle,2)

def labelPlot(torqueUnit):
    plt.title = 'Twist Angle vs. Torque'
    plt.xlabel('Twist Angle [deg]')
    plt.ylabel('Torque ['+ torqueUnit+']')

def getSpeed(angles,times):
    angleDelta = angles[-1] - angles[-2]
    timeDelta = times[-1] - times[-2]
    return angleDelta/timeDelta

inputSpeed  = getInput("Enter speed of rotation (degrees/s): ")
speed = getMotorSpeed(inputSpeed) 
testName = input("Enter the test name: ")
print(str(testName)+" will run at a speed of "+str(speed))#+" (degrees/s)")
createDir(testName)

startTime = getNow()
sTime = time.time()
print("Test has started at "+startTime+".")

# testing end
torque = mtt03.MTT03('COM5') # setup mark-10 torque gauge - CHANGE COM PORT WHEN NECESSARY
startTorque = torque.read()
torqueVals = [float(startTorque.split()[0])]
torqueUnits = [startTorque.split()[1]]
timeVals = [0]

servo = servo_control.BusServo('COM6', 1) # setup servo - CHANGE COM PORT WHEN NECESSARY
startPos = servo.readPosition()
startDeg = servoDeg(startPos)
print("Start Position: "+str(startPos))
print("Start Angle: "+str(startDeg))
servo.commandSpeed(speed)
angleVals = [0]
filteredAngleVals = [0]
degVals = [0]
counter = [0]
in_bad_servo_region = False
passed_bad_region = False
passed_starting = False

# open plot
plt.plot(angleVals, torqueVals)
plt.pause(0.001) # 1 ms pause
labelPlot(torqueUnits[0])
tCount = 1 # for debugging
revCount = 0

with open(testName+"/"+testName+".log","w") as testFile:
    printHeader(testFile)

    while True:
        #angleVals.append(servoDeg(servo.readPosition(),startAngle))
        servoPos = servo.readPosition() 
        angleVals.append(servoPos)
        if len(angleVals) >= 20:
            filteredPos, in_bad_servo_region = filterRawPositionData(servoPos, filteredAngleVals[-20:-1], in_bad_servo_region)
        else:
            filteredPos = servoPos
        passed_bad_region |= in_bad_servo_region
        filteredAngleVals.append(filteredPos)
        currentDeg = servoDeg(filteredPos)
        passed_starting = (currentDeg > (startDeg) and currentDeg < (startDeg + 10))
        print(currentDeg)
        if (passed_bad_region and passed_starting):
            revCount += 1
            passed_bad_region = False
            passed_starting = False
        degVals.append(absDeg(currentDeg,startDeg,revCount))
        #degVals.append(currentDeg)
        torqueNow = torque.read()
        counter.append(tCount)
        torqueVals.append(float(torqueNow.split()[0]))
        #torqueVals.append(tCount)
        torqueUnits.append(torqueNow.split()[1])
        timeVals.append(time.time()-sTime)
        plt.plot(degVals, torqueVals) # real plot
        #plt.plot(counter,torqueVals)
        #plt.plot(counter, degVals) # for debugging angleVals
        plt.pause(0.001)
        testFile.write(str(tCount)+"\t"+str(angleVals[-1])+"\t"+str(degVals[-1])+"\t"+str(currentDeg)+"\t"+str(torqueVals[-1])+"\t"+torqueUnits[-1]+"\t"+str(getSpeed(angleVals,timeVals))+"\n")
        #print(angleVals[-1])
        #print(revCount)
        tCount += 1
        if keyboard.is_pressed("q"): # quit the test with 
            break
        
    endTime = getNow()
    servo.commandSpeed(0) # turn servo off
    time.sleep(0.1)
    servo.commandPosition(120, 3000)
    print("Test has completed at "+endTime+".")
    testFile.write("Test has completed at "+endTime+"."+"\n")
