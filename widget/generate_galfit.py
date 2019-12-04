### generate_galfit.py - displays a GUI for Galfit parameters
### Author: Emily Ramey
### Created: 11/30/19

### packages used
# GUI interface
from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk
# Graphing
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
# OS processes
import os
import subprocess

### file paths
tmp_path = "./.galfit/" # folder for temporary files
parfile = tmp_path+"galfit-example/EXAMPLE/galfit_test.feedme" # param file # maybe download from internet later
original_parfile = tmp_path+"galfit-example/EXAMPLE/galfit.feedme" # parfile to reset if things go awry
fitsfile = tmp_path+"imgblock.fits" # image file
imgfile = tmp_path+"tmp_img.png"

### global constants
W = 5
winX = 1000
winY = 1000
winsize = str(winX)+"x"+str(winY)
titlefont = ("Arial Bold", 20)

### global variables
count = [0]
objTemplate = ['# Object number: 1\n',
        ' 0) sersic                 #  object type\n',
        ' 1) 100         100   1 1  #  position x, y\n',
        ' 3) 2.0         1          #  Integrated magnitude\n',
        ' 4) 100         1          #  R_e (half-light radius)   [pix]\n',
        ' 5) 1           1          #  Sersic index n (de Vaucouleurs n=4) \n',
        ' 6) 0.0000      0          #     ----- \n',
        ' 7) 0.0000      0          #     ----- \n',
        ' 8) 0.0000      0          #     ----- \n',
        ' 9) 1.75        1          #  axis ratio (b/a)  \n',
        '10) -75.0       1          #  position angle (PA) [deg: Up=0, Left=90]\n',
        " Z) 0                      #  output option (0 = resid., 1 = Don't subtract) \n",
        '\n']

buttons = []
all_objects = []

### class definitions
class paramObject: # holds a parameter
    def __init__(self, text, match, line, obj):
        self.val = match.group(1)
        self.text = text # text for label
        self.line = line # line in parfile
        self.start = match.span(1)[0] # starting index in line
        self.end = match.span(2)[0]
        self.end_min = self.end
        #self.startlen = n # initial length in chars
        #self.len = match.span(2)[0] # length in chars
        #self.next = match.span(2)[0]
        self.obj = obj # object referenced
        self.prevVal = val
        
        # buttons and labels
        self.label = Label(btnFrame, text=text)
        self.entry = Entry(btnFrame, width=W, state='normal')
        self.entry.insert(0, self.val)
        #print("ping on creation:", self.val)
        #self.entry.configure(state='disabled')
        #self.button = Button(btnFrame, text="Edit", command=self.btnPressed)
    
    def __eq__(self, other):
        return self.val==other.val and self.line==other.line and self.start==other.start and self.end==other.end
        
    def grid(self): # position widget in grid
        self.label.grid(row=count[0], column=0, sticky='w')
        self.entry.grid(row=count[0], column=1, sticky='w')
        count[0] += 1
    
    def ungrid(self):
        self.label.grid_remove()
        self.entry.grid_remove()
    
    def writeNewVal(self):
        # get new text
        newText = self.entry.get()
        # if the new text is bigger than the current text, do nothing
        # if the new text is smaller than the current text but bigger than the start text, remove the extra
        # if the new text is smaller than the start text, add in the extra space
        left = self.end_min - len(newText) - self.start
        if left <= 0:
            space = " "
        else:
            space = " "*left
            
        '''    
        # check length against previous length
        if left<=0:
            space = ""
        else:
            space = " "*left
        '''
            
        # format new string
        newstring = all_pars[self.line][:self.start] + newText + space + all_pars[self.line][self.end:]
        all_pars[self.line] = newstring
        self.end = self.start+len(newText)+len(space)
        
    def evaluate(self):
        newVal = self.entry.get()
        if newVal != self.prevVal:
            self.writeNewVal()
            self.prevVal = newVal

class galfitObject:
    def __init__(self, num, start=0, objType=None):
        self.startline = start
        self.endline = len(all_pars)
        self.num = int(num)
        self.type = objType
        self.params = []
        if self.num == 0:
            text="Galfit parameters:"
        else:
            text = "Object "+str(self.num)+":"
        self.label = Label(btnFrame, text=text, font=titlefont)
        
    def refresh(self):
        if self.num == 0:
            text="Galfit parameters:"
        else:
            text = "Object "+str(self.num)+":"
        self.label.configure(text=text)
        
    def __eq__(self, other):
        a = self.num == other.num and self.type == other.type
        a = a and self.num == other.num and self.type == other.type
        a = a and self.startline == other.startline and self.endline == other.endline
        a = a and self.params == other.params
        return a
    
    def gridAll(self):
        if self.type == 'sky':
            return
        self.label.grid(row=count[0], column=0, sticky='w')
        count[0] += 1
        for param in self.params:
            param.grid()
    
    def ungridAll(self):
        self.label.grid_remove()
        for param in self.params:
            param.ungrid()
### ideas to fix spacing problem
# instead of deleting whitespace when a write occurs, use a separate function for it and do it each save
    # I'd have to check the space to the # for each thing
    # then check whether the length of the new thing leaves at least one space between the # and it and delete or add in the extra
    # then I'd save again
    # to be really robust I'd save the original space to the # rather than the new one
# reload objects from the array each time a write occurs - let's not

### ideas for adding objects
    #1 - copy an existing object, write the file, and read the file in again
    #2 - copy an existing object, write the file, and read just that object in
    #3 - make my own object (?), write the file, and read just that object in
    # going with option 2 probably
    # the objects are going to need to be re-gridded anyway, best to just reload them all
            
### function definitions
def loadImage(panel=None):
    # first save as png
    with fits.open(fitsfile) as f:
        data = f[0].data
        plt.imsave(imgfile, data)
    # load in png and display
    img = ImageTk.PhotoImage(Image.open(imgfile))
    # check if image panel exists
    if(panel==None): # if no, make one
        panel = Label(imgFrame, image=img)
    else: # if yes, configure the existing one
        panel.configure(image=img)
    # place in window
    panel.image = img
    panel.grid(column=0, row=0, sticky='w')
    return panel

def runGalfit():
    FNULL = open(os.devnull, 'w')
    subprocess.call("./galfit "+parfile, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

def loadFile():
    with open(parfile) as f:
        all_pars = f.readlines()
    return all_pars

def refreshImage(panel=None):
    # save all object states
    for obj in all_objects:
        for param in obj.params:
            param.evaluate()
    
    # write new params to file
    with open(parfile, 'w') as f:
        f.writelines(all_pars)
    
    # run the program
    runGalfit()
    # reload the image
    loadImage(panel)

# generates a line matching select value of numVals parameters
# num is the line number
def genLine(num, numVals=2, select=1):
    numstring = str(num)+"\) "
    for i in range(1,numVals+1):
        if i==select or i==select+1:
            numstring+="(\S+)\s+"
        else:
            numstring+="\S+\s+"
    if select==numVals:
        numstring+="(\S+)"
    return numstring

def readParams(pars):
    objects = []
    obj = galfitObject(0,2)
    objects.append(obj)
    
    for i in range(len(pars)):
        line = pars[i]
        for key in param_matches.keys():
            # match each regex to each line
            match = re.match(key, line)
            if match:
                val = match.group(1) # get parameter value
                # check if it's a new object
                if key == newObjKey:
                    obj.endline = i-1
                    obj = galfitObject(val, i)
                    objects.append(obj)
                    continue
            
                # check if it's an object type
                if val in object_types:
                    obj.type = val
                # skip sky for now
                if obj.type=='sky':
                    continue

                # set up generic parameter object
                param_obj = paramObject(param_matches[key]+":", match, i, obj)
                obj.params.append(param_obj)
    return objects

def reloadUI(all_objects):
    new_objects = readParams(all_pars)
    
    count[0] = 0
    for obj in all_objects:
        obj.ungridAll()
    
    for btn in buttons:
        btn.grid_remove()
    
    for obj in new_objects:
        obj.gridAll()
    
    for i in range(len(buttons)):
        buttons[i].grid(row=count[0], column=i)
    count[0]+=1
    
    all_objects = new_objects
    #return new_objects
# this is broken and I don't know why
# maybe I'll just change all_pars, write it, and hope for the best

def addObject():
    objTemplate[0] = objTemplate[0][:-2]+str(all_objects[-1].num+1)+objTemplate[-1]
    obj = readParams(objTemplate)[1]
    
    for line in objTemplate:
        all_pars.append(line)
    
    obj.startline = len(all_objects)
    obj.endline = len(all_objects)+len(objTemplate)-1
    obj.num = all_objects[-1].num+1
    #all_objects.append(obj)
    #print(len(all_objects))
    reloadUI(all_objects)
    
### main program

# read in parameter file
all_pars = loadFile()

# Dictionary of parameters
newObjKey = "# Object number: (\d+)"
param_matches = {
    # image parameters
    genLine("H",4,2): "Image size x",
    genLine("H",4,4): "Image size y",
    # object parameters
    newObjKey: "Object",
    " "+genLine(0,1,1): "Object type",
    " "+genLine(1,4,1): "x position",
    " "+genLine(1,4,2): "y position",
    " "+genLine(3): "Integrated magnitude",
    " "+genLine(4): "Half-light radius (pix)",
    " "+genLine(5): "Sersic index",
    " "+genLine(9): "Axis ratio (b/a)",
    genLine(10): "Position angle"
}

object_types = ["sersic", "expdisk", "sky"]

### Start building GUI
root = Tk()
root.title("Galfit GUI")
root.geometry(winsize)

# Frame for buttons
btnFrame = Frame(root, width=winX/2, height=winY)
btnFrame.grid(row=0, column=0)
btnFrame.grid_propagate(0)
# Frame for image
imgFrame = Frame(root, width=winX/2, height=winY)
imgFrame.grid(row=0, column=1)
imgFrame.grid_propagate(0)

# build parameter objects from file
obj = galfitObject(0, 2)
all_objects.append(obj)

for i in range(len(all_pars)):
    line = all_pars[i]
    for key in param_matches.keys():
        # match each regex to each line
        match = re.match(key, line)
        if match:
            val = match.group(1) # get parameter value
            # check if it's a new object
            if key == newObjKey:
                obj.endline = i-1
                obj = galfitObject(val, i)
                all_objects.append(obj)
                continue
            
            # check if it's an object type
            if val in object_types:
                obj.type = val
            
            # set up parameter object for UI
            if obj.type=='sky':
                continue
            param_obj = paramObject(param_matches[key]+":", match, i, obj)
            
            obj.params.append(param_obj)

for obj in all_objects:
    if obj.type != "sky":
        obj.gridAll()

reloadUI(all_objects)
#print(len(all_objects))

# run galfit and load image
runGalfit()
panel = loadImage()

# set up a button to add an object
addBtn = Button(btnFrame, text="Add an object", command=addObject)
addBtn.grid(row=count[0], column=0)

# set up a button to refresh the image
refreshBtn = Button(btnFrame, text="Run Galfit!", command = lambda : refreshImage(panel))
refreshBtn.grid(row=count[0], column=1)
count[0]+=1
buttons.append(addBtn)
buttons.append(refreshBtn)

# display the finished window
root.mainloop()

#TODO - write a function so you can refresh the text of entries when galfit is run