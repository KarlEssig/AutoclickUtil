#! python
""" Created by Karl Essig """
import pyautogui
from pynput.keyboard import Key, Listener
import time
import threading
import pickle
from MouseProcedure import MouseProcedureClass

#Semaphores for multi-threading
functioncalled = threading.Semaphore(0) #controls when a valid function is called from key listener
functionfinished = threading.Semaphore(1) #controls when the function has ended and the KeyListener can listen for new key inputs
inputbuffer = threading.Semaphore(1) #if this is locked, the main thread is using the keyboard for input
protectmousepos = threading.Semaphore(0) #importmousex and importmousey are alright to write from keylistener
readmousepos = threading.Semaphore(0)    #importmousex and importmousey are alright to read from threadedMain
#bounded semaphore?

#global variables
idfunc = 0    #provides a mapping from KeyListener key to a function in MainThread                       
importmousex, importmousey = 0,0    #When the enter key is released, save the current mouse position

def on_press(key):
    return

def on_release(key):
    if inputbuffer.acquire(blocking=False):
        global idfunc
        if key == Key.esc:
            print("Pressed ESC!")
            idfunc = -1 
            functioncalled.release()
            return False
        elif key == Key.f7 or key == Key.f8 or key == Key.f9 or key == Key.f10 or key == Key.f11 or key == Key.f12:
            functionfinished.acquire()
            if key == Key.f7:                      
                idfunc = 1
                print("What is going on withhhh {0}".format(idfunc))
                functioncalled.release()
            elif key == Key.f8:
                idfunc = 2
                functioncalled.release()
            elif key == Key.f9:
                idfunc = 3
                functioncalled.release()
            elif key == Key.f10:
                idfunc = 4
                functioncalled.release()
            elif key == Key.f11:
                idfunc = 5
                functioncalled.release()
            elif key == Key.f12:
                idfunc = 6
                functioncalled.release()
        elif key == Key.shift:
            if protectmousepos.acquire(blocking=False):
                global importmousex,importmousey 
                importmousex, importmousey = pyautogui.position()
                readmousepos.release()
            else:
                print("Blocked?")
        inputbuffer.release()

        
class ThreadedMain(threading.Thread): #the main thread of the program, will handle all the function calls from Listener
    def __init__(self, threadid, name):
        threading.Thread.__init__(self)
        self.threadid = threadid
        self.name = name
        self.EXIT = 0         #controls if the main thread will exit
        self.MouseProcedureList = list()
        self.lengthList = 0
        
    def clearVariables(self):        #resets state variables to initial state
        self.MouseProcedure = list()
        self.lengthList = 0
        
    def determineFunction(self):
        global idfunc
        if idfunc == -1:
            self.EXIT = 1
        elif idfunc == 1:
            print("Input amount of seconds:") 
            inputbuffer.acquire()
            secamt = input()
            inputbuffer.release()
            print("Number of seconds = {0}".format(secamt))
            self.getMousePosition(secamt)
        elif idfunc == 2:
            self.clearVariables()
            print("Go to the application and press shift on where you want to click")
            self.saveMousePosition(1)
            self.saveWaitTime(1)
            self.toString()
        elif idfunc == 3:
            self.clearVariables()
            print("Input number of mouse clicks to record.")
            inputbuffer.acquire()
            mouseamt = input()  
            inputbuffer.release()
            print("Go to application and go through the mouse clicks, pressing shift for each one")
            self.saveMousePosition(int(mouseamt))
            self.saveWaitTime(int(mouseamt))
            self.toString()
        elif idfunc == 4:
            print("Input number of iterations, or -1 for infinite")
            inputbuffer.acquire()
            iter = input()
            inputbuffer.release()
            intiter = int(iter)
            if intiter == -1:
                self.runAutoclicker()
            else:
                self.runAutoclicker(intiter)
        elif idfunc == 5:
            self.saveFile()
        elif idfunc == 6:
            self.loadFile()
            
    def getMousePosition(self,secamt): #number of seconds that user designated
        i = 0
        while i < int(secamt):
            mouseX,mouseY = pyautogui.position()
            i = i + 1
            print("{0}: Position(X,Y): {1},{2}".format(i,mouseX,mouseY))
            time.sleep(1)
    
    def loadFile(self): #
        print("Input file name to load")
        inputbuffer.acquire()
        filename = input()
        inputbuffer.release()
        fileobj = open(filename, "rb")
        self.MouseProcedureList = pickle.load(fileobj)
        fileobj.close()
        self.toString()
          
    def menu(self):  #The menu printed out to the user
        print("Hello, welcome to AutoclickUtil!\nThis program uses a KeyListener to asynchronously process commands.\n")
        print("Press F7 to get mouse positions over a user designated amount of seconds")
        print("Press F8 to begin setup for a new simple autoclicker program")
        print("Press F9 to begin setup for a new complex autoclicker program")
        print("Press F10 to run autoclicker program")
        print("Press F11 to save your program to a file")
        print("Press F12 to load a program from a file")
        
    def run(self):   #Manages when a key has been pressed for a new function, and when a function has finished, and when the main program should finish
        print("Starting main function...")
        while(self.EXIT == 0):
            self.menu() 
            functioncalled.acquire()
            self.determineFunction()
            functionfinished.release()
        print("exiting...")
    
    def runAutoclicker(self, number=None):  #Runs the Mouse Procedures on the computer.
        global idfunc
        print("Pressing esc at any point will cancel the current mouse procedure after a few seconds.")
        if number is None:   
            while(True):
                self.MouseProcedureList[0].run()
                if idfunc == -1:
                    print("Here")
                    idfunc = 0
                    return  #if esc is pressed, end current procedure
        else:
            j = 0
            while(j < number):
                j = j + 1
                self.MouseProcedureList[0].run()
                if idfunc == -1:
                    idfunc = 0
                    return   #if esc is pressed, end current procedure
        return                
                     
    def saveMousePosition(self, number):#Saves the mouse procedure in a mouse procedure object
        global importmousex, importmousey
        i = 0
        mouseprocedurex = []
        mouseprocedurey = []
        while (i < number):
            protectmousepos.release()
            readmousepos.acquire()
            print("Saved")
            mouseprocedurex.append(importmousex)
            mouseprocedurey.append(importmousey)
            i = i + 1
        newmouseprocedure = MouseProcedureClass(mouseprocedurex,mouseprocedurey,number)
        self.MouseProcedureList.append(newmouseprocedure)
        
    
    def saveFile(self): #Saves the mouse Procedures to a file
        print("Input name of file to save to:")
        inputbuffer.acquire()
        filename = input()
        inputbuffer.release()
        fileobject = open(filename, "wb")
        pickle.dump(self.MouseProcedureList,fileobject)
        fileobject.close()
        
    def saveWaitTime(self, number): #Saves the wait procedure to a mouse procedure object in the procedure list
        i = 0
        waitprocedure = []
        inputbuffer.acquire()
        while (i < number):
            print("Input wait time between mouseclicks {0} and {1}".format((i),((i+1)%number)))      
            temp = input()
            try: 
                waitprocedure.append(float(temp))
            except:
                continue
            i = i + 1   
        inputbuffer.release()
        self.MouseProcedureList[0].setWait(waitprocedure)
        
    def toString(self):
        print(self.MouseProcedureList[0].toString())

        
if __name__ == "__main__":
    listener = Listener(on_release=on_release)
    mainThread = ThreadedMain(1, "Main")
    mainThread.start()
    listener.start()
    mainThread.join()
    listener.join()
