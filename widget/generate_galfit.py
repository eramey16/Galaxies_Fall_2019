### generate_galfit.py - displays a GUI for Galfit parameters
### Author: Emily Ramey
### Created: 11/30/19

### packages used
# GUI interface
from tkinter import Menu
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

### frontend global variables
W = 5
winX = 1000
winY = 1000
winsize = str(winX)+"x"+str(winY)
titlefont = ("Arial Bold", 20)

### file paths
tmp_path = ".galfit/" # folder for temporary files
usr_parfile = None
parfile = tmp_path+"galfit-example/EXAMPLE/galfit_test.feedme" # param file # maybe download from internet later
original_parfile = tmp_path+"galfit-example/EXAMPLE/galfit.feedme" # parfile to reset if things go awry
fitsfile = tmp_path+"imgblock.fits" # image file
imgfile = tmp_path+"tmp_img.png"

# backend global variables
count = 0
all_pars = []
all_objects = []
all_buttons = []
objTemplate = ['# Object number: 1\n',
        ' 0) sersic                 #  object type\n',
        ' 1) 50          50    1 1  #  position x, y\n',
        ' 3) 2.0         1          #  Integrated magnitude\n',
        ' 4) 100         1          #  R_e (half-light radius)   [pix]\n',
        ' 5) 1           1          #  Sersic index n (de Vaucouleurs n=4) \n',
        ' 6) 0.0000      0          #     ----- \n',
        ' 7) 0.0000      0          #     ----- \n',
        ' 8) 0.0000      0          #     ----- \n',
        ' 9) .5          1          #  axis ratio (b/a)  \n',
        '10) 90          1          #  position angle (PA) [deg: Up=0, Left=90]\n',
        " Z) 0                      #  output option (0 = resid., 1 = Don't subtract) \n",
        '\n']

### class definitions
class paramObject: # holds a parameter
    def __init__(self, text, match, line, obj):
        self.val = match.group(1)
        self.text = text # text for label
        self.line = line # line in parfile
        self.start = match.span(1)[0] # starting index in line
        self.end = match.span(2)[0]
        self.end_min = self.end
        self.obj = obj # object referenced
        self.prevVal = self.val
        
        # buttons and labels
        self.label = Label(btnFrame, text=text)
        self.entry = Entry(btnFrame, width=W, state='normal')
        self.entry.insert(0, self.val)
        #self.entry.configure(state='disabled')
        #self.button = Button(btnFrame, text="Edit", command=self.btnPressed)
        
    def grid(self): # position widget in grid
        global count
        self.label.grid(row=count, column=0, sticky='w')
        self.entry.grid(row=count, column=1, sticky='w')
        count += 1
    
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
            
        # format new string
        newstring = all_pars[self.line][:self.start] + newText + space + all_pars[self.line][self.end:]
        all_pars[self.line] = newstring
        self.end = self.start+len(newText)+len(space)
        
    def save(self):
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
        self.button = Button(btnFrame, text="Remove object", command=lambda:self.remove())
    
    def gridAll(self):
        global count
        if self.type == 'sky':
            return
        self.label.grid(row=count, column=0, sticky='w')
        if self.type != None:
            self.button.grid(row = count, column=1, sticky='w')
        count += 1
        for param in self.params:
            param.grid()
    
    def ungridAll(self):
        self.label.grid_remove()
        for param in self.params:
            param.ungrid()
    
    def saveAll(self):
        for param in self.params:
            param.save()
        writeFile()
    
    def remove(self):
        global all_objects
        global all_pars

        all_objects.remove(self)
        all_pars = all_pars[:self.startline]+all_pars[self.endline:]
        writeFile()
        reloadGUI()
            
### function definitions
def checkPar():
    if usr_parfile==None:
        return parfile
    else:
        return usr_parfile

def readFile():
    global all_pars
    p = checkPar()
    
    with open(p) as f:
        all_pars = f.readlines()

def writeFile():
    global all_pars
    p = checkPar()
    with open(p, 'w') as f:
        f.writelines(all_pars)

def countOne():
    global count
    count += 1

def readImage(panel=None):
    #print("read image called")
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
    return panel

def runGalfit():
    #print("run galfit called")
    FNULL = open(os.devnull, 'w')
    p = checkPar()
    subprocess.call("./galfit "+p, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

def loadImage(panel=None):
    # save all object states
    for obj in all_objects:
        obj.saveAll()
    
    # run the program
    runGalfit()
    # reload the image
    return readImage(panel)

# generates a line matching select value of numVals parameters
# num is the line number
def readParams():
    global all_objects
    # build parameter objects from file
    obj = galfitObject(0, 2)
    all_objects.append(obj)
    for i in range(len(all_pars)):
        line = all_pars[i]
        for key in param_matches.keys():
            # match each regex to each line
            match = re.match(key, line)
            if match:
                # make it output to tmp directory
                if param_matches[key]=="outfile":
                    changeOutfile(i, match)
                    continue

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
    
def changeOutfile(line, match):
    start, end = match.span(1)
    newline = all_pars[line][:start]+fitsfile+all_pars[line][end:]
    all_pars[line] = newline
    writeFile()

def makeCanvas():
    global btnFrame1
    global btnFrame
    global btnCanvas
    
    btnFrame1.destroy()
    #btnCanvas.destroy()
    #scrollbar.destroy()
    
    btnFrame1 = Frame(root, width=winX/2, height=winY)
    btnFrame1.pack(side=LEFT, fill=BOTH)
    # make canvas
    btnCanvas = Canvas(btnFrame1)
    btnCanvas.pack(side=LEFT, fill=BOTH)

    ### set up the scroll bar
    scrollbar = Scrollbar(btnFrame1, command=btnCanvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y, expand=True)

    btnCanvas.configure(yscrollcommand=scrollbar.set)
    btnCanvas.bind('<Configure>', on_configure)
    btnCanvas.bind_all('<MouseWheel>',lambda event : on_mousewheel(event))
    on_configure(0)

    btnFrame = Frame(btnCanvas)
    btnFrame.pack(side=LEFT, fill=BOTH)
    btn_id = btnCanvas.create_window((0,0), window=btnFrame, anchor='nw')

def on_mousewheel(event):
    global btnCanvas
    #print(event)
    btnCanvas.yview_scroll(-1*np.sign(event.delta), "units")

def addButtons():
    global count
    global addBtn
    global refreshBtn
    
    # set up a button to add an object
    addBtn = Button(btnFrame, text="Add an object", command=addObject)
    addBtn.grid(row=count, column=0)

    # set up a button to refresh the image
    refreshBtn = Button(btnFrame, text="Run Galfit!", command = lambda : loadImage(panel))
    refreshBtn.grid(row=count, column=1)
    count+=1
    
    return addBtn, refreshBtn

def reloadGUI():
    global all_pars
    global all_objects
    global count
    
    # remove current entries and buttons
    for obj in all_objects:
        obj.ungridAll()
    
    # restart count
    count = 0
    # refresh the canvas object
    makeCanvas()
    
    # refresh params & objects
    all_pars = []
    all_objects = []
    readFile()
    readParams()
    for obj in all_objects:
        obj.gridAll()
    
    # add buttons
    addButtons()
    # load new image
    loadImage(panel)

def addObject():
    global all_pars
    
    # Make new object
    objTemplate[0] = objTemplate[0][:-2]+str(all_objects[-1].num+1)+objTemplate[-1]
    for line in objTemplate: # add it to parameters
        all_pars.append(line)
    writeFile()
    
    reloadGUI()

def on_configure(event):
    global btnCanvas
    # update scrollregion after starting 'mainloop'
    # when all widgets are in canvas
    btnCanvas.configure(scrollregion=btnCanvas.bbox('all'))
    
def saveParAs():
    global usr_parfile
    filename = filedialog.asksaveasfilename(title="Select file", filetypes=(("FEEDME file", "*.feedme"), ("All files", "*.*")))
    p = checkPar()
    subprocess.call(["cp", p, filename])
    usr_parfile = filename
    for obj in all_objects:
        obj.saveAll()

def saveImg():
    filename = filedialog.asksaveasfilename(title="Select file", filetypes=(("FITS file","*.fits"),("PNG","*.png"), ("JPG", "*.jpg")))
    if ".fits" in filename:
        subprocess.call(["cp", fitsfile, filename])
    else:
        with fits.open(fitsfile) as f:
            data = f[0].data
            plt.imsave(filename, data)

def loadPar():
    global usr_parfile
    filename = filedialog.askopenfilename(filetypes = (("FEEDME file","*.feedme"),("all files","*.*")))
    usr_parfile = filename
    reloadGUI()

def savePar():
    if usr_parfile==None:
        saveParAs()
    else:
        for obj in all_objects:
            obj.saveAll()
    
            
### main program

# read in parameter file
readFile()

# Dictionary of parameters
newObjKey = "# Object number: (\d+)"
param_matches = {
    # image parameters
    genLine("B", 1, 1): "outfile",
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
btnFrame1 = Frame(root, width=winX/2, height=winY)
btnFrame1.pack(side=LEFT, fill=Y)
#btnFrame.place(relx=0, rely=0, anchor="center")
#btnFrame1.grid_propagate(0)
# Frame for image
imgFrame = Frame(root, width=winX/2, height=winY)
imgFrame.pack(side=RIGHT, fill=Y)
#imgFrame.place(relx=.5, rely=0, anchor="center")
#imgFrame.grid_propagate(0)

btnCanvas = Canvas(btnFrame1)
btnCanvas.pack(side=LEFT, fill=BOTH)

### set up the scroll bar
scrollbar = Scrollbar(btnFrame1, command=btnCanvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

btnCanvas.configure(yscrollcommand=scrollbar.set)
btnCanvas.bind('<Configure>', on_configure)
btnCanvas.bind_all('<MouseWheel>',lambda event : on_mousewheel(event))

btnFrame = Frame(btnCanvas)
btnFrame.pack(side=LEFT, fill=Y)
btn_id = btnCanvas.create_window((0,0), window=btnFrame, anchor='nw')

### Create a menu
menu = Menu(root)
new_item = Menu(menu)
new_item.add_command(label='Load parameter file', command=loadPar)
new_item.add_command(label='Save parameter file', command=savePar)
new_item.add_command(label='Save parameter file as', command=saveParAs)
new_item.add_command(label="Save image file", command=saveImg)
menu.add_cascade(label='File', menu=new_item)
root.config(menu=menu)

### read in parameters
readParams()

for obj in all_objects:
    if obj.type != "sky":
        obj.gridAll()

# run galfit and load image
runGalfit()
panel = loadImage()
panel.place(relx=.3, rely=.3, anchor="center")

addBtn, refreshBtn = addButtons()

# display the finished window
root.mainloop()

subprocess.call(["cp", original_parfile, parfile])

#TODO - write a function so you can refresh the text of entries when galfit is run