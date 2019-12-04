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

### global variables
W = 5
winX = 1000
winY = 1000
winsize = str(winX)+"x"+str(winY)
titlefont = ("Arial Bold", 20)

### class definitions
class paramObject: # holds a parameter
    def __init__(self, text, gridpos, match, line, obj):
        self.val = match.group(1)
        self.text = text # text for label
        self.pos = gridpos # position in grid
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
        self.entry.insert(0, val)
        #self.entry.configure(state='disabled')
        #self.button = Button(btnFrame, text="Edit", command=self.btnPressed)
        
    def grid(self): # position widget in grid
        g = self.pos
        self.label.grid(row=g[0], column=g[1], sticky='w')
        self.entry.grid(row=g[0], column=g[1]+1, sticky='w')
        count += 1
    
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
    def __init__(num, objType, start):
        self.startline = start
        self.endline = len(all_pars)
        self.num = num
        self.type = objType
        self.params = []
    
    def gridAll():
        obj_label = Label(btnFrame, text="Object "+str(obj)+":", font=titlefont)
        obj_label.grid(row=count, column=0, sticky='w')
        count += 1
        for param in self.params:
            param.grid()
            
### ideas to fix spacing problem
# instead of deleting whitespace when a write occurs, use a separate function for it and do it each save
    # I'd have to check the space to the # for each thing
    # then check whether the length of the new thing leaves at least one space between the # and it and delete or add in the extra
    # then I'd save again
    # to be really robust I'd save the original space to the # rather than the new one
# reload objects from the array each time a write occurs - let's not
            
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

def reloadFile():
    with open(parfile) as f:
        all_pars = f.readlines()

def refreshImage(panel=None):
    # save all object states
    for obj in all_objects:
        obj.evaluate()
    
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

def updateParams(firstRun=False):
    all_objects = []
    

### main program

# read in parameter file
with open(parfile) as f:
    all_pars = f.readlines()

reloadFile()

# Dictionary of parameters
param_matches = {
    # image parameters
    genLine("H",4,2): "Image size x",
    genLine("H",4,4): "Image size y",
    # object parameters
    "# Object number: (\d+)": "Object",
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

# First label
imgLabel = Label(btnFrame, text="Galfit parameters:", font=titlefont)
imgLabel.grid(row=0, column=0, sticky='w')

# build parameter objects from file
all_objects = []
obj = 0
obj_type = None
count = 1
for i in range(len(all_pars)):
    line = all_pars[i]
    for key in param_matches.keys():
        # match each regex to each line
        match = re.match(key, line)
        if match:
            #print(match.group(0))
            val = match.group(1) # get parameter value
            # check if it's a new object
            if val in object_types:
                obj += 1
                obj_type = val
                if obj_type=='sky':
                    continue
                obj_label = Label(btnFrame, text="Object "+str(obj)+":", font=titlefont)
                obj_label.grid(row=count, column=0, sticky='w')
                count+=1
            
            #print(line, "\n", param_matches[key], ":", val, "object:", obj, obj_type, "\n")
            # set up parameter object for UI
            if obj_type=='sky':
                continue
            param_obj = paramObject(param_matches[key]+":", (count, 0), match, i, obj)
            #print(param_matches[key], ": val -", val, ", start:", match.span(1)[0], "\n", line, key)
            param_obj.grid()
            all_objects.append(param_obj)
            count += 1

# run galfit and load image
runGalfit()
panel = loadImage()

# set up a button to add an object
addBtn = Button(btnFrame, text="Add an object")
addBtn.grid(row=count, column=0)

# set up a button to refresh the image
refreshBtn = Button(btnFrame, text="Run Galfit!", command = lambda : refreshImage(panel))
refreshBtn.grid(row=count, column=1)
count+=1

# display the finished window
root.mainloop()

#TODO - write a function so you can refresh the text of entries when galfit is run