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
parfile = "galfit-example/EXAMPLE/galfit_test.feedme" # param file # maybe download from internet later
original_parfile = "galfit-example/EXAMPLE/galfit.feedme" # parfile to reset if things go awry
tmp_path = "./.galfit/" # folder for temporary files
fitsfile = "imgblock.fits" # image file
imgfile = tmp_path+"tmp_img.png"

### global variables
W = 5
winX = 1000
winY = 1000
winsize = str(winX)+"x"+str(winY)
imgSizeKey = "H)"

### class definitions
class paramObject: # holds a parameter
    def __init__(self, text, gridpos, startval, line, start, n, obj=None):
        self.text = text # text for label
        self.pos = gridpos # position in grid
        self.line = line # line in parfile
        self.start = start # starting index in line
        self.len = n # length in chars
        self.obj = obj # object referenced
        
        # buttons and labels
        self.label = Label(root, text=text)
        self.entry = Entry(root, width=W, state='normal')
        self.entry.insert(0, startval)
        self.entry.configure(state='disabled')
        self.button = Button(root, text="Edit", command=self.btnPressed)
        
    def grid(self): # position widget in grid
        g = self.pos
        self.label.grid(row=g[0], column=g[1], sticky='w')
        self.entry.grid(row=g[0], column=g[1]+1, sticky='w')
        self.button.grid(row=g[0], column=g[1]+2, sticky='w')
        
    def btnPressed(self): # button action
        if(self.entry.cget("state")=='disabled'): # go to edit state
            self.entry.configure(state="normal")
            self.entry.focus()
            self.button.configure(text="Save")
        else: # go to stationary state
            # save new text
            text = self.entry.get()
            left = self.len - len(text)
            if(left<0): # check length against previous length
                messagebox.showerror('Error: Invalid Value', 'Value exceeds maximum characters')
            # format new string
            newstring = all_pars[self.line][:self.start] + text + " "*left + all_pars[self.line][self.start+self.len:]
            all_pars[self.line] = newstring
            # write new params to file
            with open(parfile, 'w') as f:
                f.writelines(all_pars)
            
            # switch buttons
            self.button.configure(text="Edit")
            self.entry.configure(state='disabled')
            
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
        panel = Label(root, image=img)
    else: # if yes, configure the existing one
        panel.configure(image=img)
    # place in window
    panel.image = img
    panel.grid(column=5, row=0, sticky='w')
    return panel

def runGalfit():
    FNULL = open(os.devnull, 'w')
    subprocess.call("./galfit "+parfile, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

def refreshImage(panel=None):
    runGalfit()
    loadImage(panel)

### main program

# create temporary folder
if not os.path.exists(tmp_path):
    os.mkdir(tmp_path)

# read in parameter file
with open(parfile) as f:
    all_pars = f.readlines()

# Dictionary of parameters
# regex : text value
param_matches = {
    # image parameters
    "H\) \d+\s+(\d+)(?:\s+\d+){2}": "Image size x",
    "H\) (?:\d+\s+){3}(\d+)": "Image size y",
    #"A\) (.+\.fits)": "Input image"
    # object parameters
    " 0\) (\S+)": "Object type",
    " 1\) (\S+)(?:\s+\S){3}": "x position",
    " 1\) \S+\s+(\S+)(?:\s+\S+){2}": "y position"
}

### Start building GUI
root = Tk()
root.title("Galfit Parameters")

# build parameter objects from file
all_objects = []
obj = None
count = 0
for i in range(len(all_pars)):
    line = all_pars[i]
    for key in param_matches.keys():
        match = re.match(key, line)
        if match:
            val = match.group(1)
            print(line, val, len(val))
            #param_obj = paramObject(param_matches[key]+":", (0, count), val, )
            #count += 1
    '''        
    # Check image size
    if line.find(imgSizeKey) != -1:
        size = (int(line[8:12]), int(line[18:22]))
        # build labels from line
        img_sizeX = paramObject("Image size x:", (0, 0), size[0], i, 8, 4)
        img_sizeY = paramObject("Image size y:", (1, 0), size[1], i, 18, 4)
        img_sizeX.grid()
        img_sizeY.grid()
        all_objects.append(img_sizeX)
        all_objects.append(img_sizeY)
     '''
    
    
    
    # Look for objects

# load the image
panel = loadImage()

# set up a button to refresh the image
refreshBtn = Button(root, text="Run Galfit!", command = lambda : refreshImage(panel))
refreshBtn.grid(row=6, column=0)

# size and display the finished window
root.geometry(winsize)
root.mainloop()