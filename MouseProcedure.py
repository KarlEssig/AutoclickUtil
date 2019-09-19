#!python
import pyautogui
import time
class MouseProcedureClass():  #Defines a specific mouse procedure - the x,y coordinates of the mouse position, and the wait inbetween these clicks
    def __init__(self,procx,procy,length):
        self.mouseprocedurex = procx
        self.mouseprocedurey = procy
        self.waitprocedure = []
        for i in range(0,length):
            self.waitprocedure.append(0)
        self.lengthprocedure = length
    
    def clearVariables(self):
        self.mouseprocedurex = []
        self.mouseprocedurey = []
        self.waitprocedure = []
        self.lengthprocedure = 0
    
    def run(self):  #runs through this specific program
        i = 0
        while (i < len(self.mouseprocedurex)):
            prevposx,prevposy = pyautogui.position()
            pyautogui.moveTo(x=self.mouseprocedurex[i],y=self.mouseprocedurey[i])
            pyautogui.mouseDown()
            pyautogui.mouseUp()
            pyautogui.moveTo(prevposx,prevposy)
            time.sleep(self.waitprocedure[i])
            i = i + 1
    def setWait(self,wait):
        self.waitprocedure = wait
        
    def toString(self):
        print("Mouse procedure x: {0}".format(self.mouseprocedurex))
        print("Mouse procedure y: {0}".format(self.mouseprocedurey))
        print("Wait procedure: {0}".format(self.waitprocedure))
            