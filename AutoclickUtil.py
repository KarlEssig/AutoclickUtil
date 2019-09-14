#! python
import pyautogui
from pynput.keyboard import Key, Listener
import time
import threading
import pickle

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
    #print('{0} pressed'.format(key))

def on_release(key):
    if inputbuffer.acquire(blocking=False):
        global idfunc
        #print('{0} release'.format(key))
        if key == Key.esc:
            #stops listener
            idfunc = -1 #-1 means the main thread will end
            functioncalled.release() #put these at end, should've been done interpretting 
            return False
        elif key == Key.f7 or key == Key.f8 or key == Key.f9 or key == Key.f10 or key == Key.f11 or key == Key.f12:
            functionfinished.acquire()
            if key == Key.f7:                        #unless there's a way to pass the key, so i don't have these if blocks
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
            #do nothing
        elif key == Key.shift:
            #save mouse position
            if protectmousepos.acquire(blocking=False):
                global importmousex,importmousey 
                importmousex, importmousey = pyautogui.position()
                readmousepos.release()
                print("Didn't block")
            else:
                print("Blocked?")
        
    
        inputbuffer.release()
        
    

        
# Collect events until released
class ThreadedMain(threading.Thread): #the main thread of the program, will handle all the function calls from Listener
    def __init__(self, threadid, name):
        threading.Thread.__init__(self)
        self.threadid = threadid
        self.name = name
        self.EXIT = 0         #controls if the main thread will exit
        self.mouseprocedurex = []     #Sequence of mouse events that the autoclicker will run through
        self.mouseprocedurey = []
        self.waitprocedure = []      #Sequence of wait events that the autoclicker will run through 
        self.lengthprocedure = 0     #The # of sequences in the program
        
    def clearVariables(self):        #resets state variables to initial state
        self.mouseprocedurex = []
        self.mouseprocedurey = []
        self.waitprocedure = []
        self.lengthprocedure = 0
        
    def determineFunction(self):
        global idfunc
        print('{0}'.format(idfunc))
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
            #used for clicking in one spot over a period of time
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
    
    def loadFile(self):
        print("Input file name to load")
        inputbuffer.acquire()
        filename = input()
        inputbuffer.release()
        fileobj = open(filename, "rb")
        self.mouseprocedurex = pickle.load(fileobj)
        self.mouseprocedurey = pickle.load(fileobj)
        self.waitprocedure = pickle.load(fileobj)
        self.lengthprocedure = pickle.load(fileobj)
        fileobj.close()
        self.toString()
        
          
    def menu(self):
        print("Hello, welcome to AutoclickUtil!\nThis program uses a KeyListener to asynchronously process commands.\n")
        print("Press F7 to get mouse positions over a user designated amount of seconds")
        print("Press F8 to begin setup for a new simple autoclicker program")
        print("Press F9 to begin setup for a new complex autoclicker program")
        print("Press F10 to run autoclicker program")
        print("Press F11 to save your program to a file")
        print("Press F12 to load a program from a file")
        
    def run(self):
        print("Starting main function.")
        while(self.EXIT == 0):
            print('Exit is {0}'.format(self.EXIT))
            self.menu() 
            functioncalled.acquire()
            self.determineFunction()
            functionfinished.release()
        print("exiting...")
    
    def runAutoclicker(self, number=None):
        if number is None:
            prevposx,prevposy = pyautogui.position()
            while(True):
                i = 0
                while (i < len(self.mouseprocedurex)):
                    pyautogui.moveTo(x=self.mouseprocedurex[i],y=self.mouseprocedurey[i])
                    pyautogui.mouseDown()
                    pyautogui.mouseUp()
                    pyautogui.moveTo(prevposx,prevposy)
                    time.sleep(self.waitprocedure[i])
                    i = i+1
                    if idfunc == -1:
                        self.EXIT = 1
                        return  #if esc is pressed, end autoclicker
        else:
            j = 0
            prevposx,prevposy = pyautogui.position()
            while(j < number):
                #print("iter {0}".format(j))
                j = j + 1
                i = 0
                while (i < len(self.mouseprocedurex)):
                    #print("in move {0}".format(i))
                    pyautogui.moveTo(x=self.mouseprocedurex[i],y=self.mouseprocedurey[i])
                    pyautogui.mouseDown()
                    pyautogui.mouseUp()
                    pyautogui.moveTo(prevposx,prevposy)
                    time.sleep(self.waitprocedure[i])
                    i = i+1
                    if idfunc == -1:
                        self.EXIT = 1
                        return   #if esc is pressed, end autoclicker
        
    """
    def runAutoclicker(self):
        i = 0
        prevposx,prevposy = pyautogui.position()
        while(True):
            while (i < len(self.mouseprocedurex)):
                pyautogui.moveTo(x=self.mouseprocedurex[i],y=self.mouseprocedurey[i])
                pyautogui.mouseDown()
                pyautogui.mouseUp()
                pyautogui.moveTo(prevposx,prevposy)
                time.sleep(self.waitprocedure[i])
                if idfunc == -1:
                    self.EXIT = 1
                    return  #if esc is pressed, end autoclicker
     """               
                    
            
            
        
    def saveMousePosition(self, number):#static length
        #at this point allow changes to importmousex and importmousey
        global importmousex, importmousey
        i = 0
        while (i < number):
            protectmousepos.release()
            readmousepos.acquire()
            print("Saved")
            self.mouseprocedurex.append(importmousex)
            self.mouseprocedurey.append(importmousey)
            i = i + 1
        self.lengthprocedure = number
    
    def saveFile(self):
        print("Input name of file to save to:")
        inputbuffer.acquire()
        filename = input()
        inputbuffer.release()
        fileobject = open(filename, "wb")
        pickle.dump(self.mouseprocedurex, fileobject)
        pickle.dump(self.mouseprocedurey, fileobject)
        pickle.dump(self.waitprocedure, fileobject)
        pickle.dump(self.lengthprocedure,fileobject)
        fileobject.close()
        #use pickle to save relevant variables in main
        
        
    def saveWaitTime(self, number):
        #save wait times between number and number + 1
        i = 0
        inputbuffer.acquire()
        while (i < number):
            print("Input wait time between mouseclicks {0} and {1}".format((i),((i+1)%number)))      
            temp = input()
            try: 
                self.waitprocedure.append(float(temp))
            except:
                continue
            i = i + 1   
        inputbuffer.release()
        
    def toString(self):
        print("Mouse procedure x: {0}".format(self.mouseprocedurex))
        print("Mouse procedure y: {0}".format(self.mouseprocedurey))
        print("Wait procedure: {0}".format(self.waitprocedure))
        
    
    

if __name__ == "__main__":
    listener = Listener(on_release=on_release)
    mainThread = ThreadedMain(1, "Main")
    #print("ah ha, yes")
    mainThread.start()
    listener.start()
    #print("I am a god")
    mainThread.join()
    listener.join()
