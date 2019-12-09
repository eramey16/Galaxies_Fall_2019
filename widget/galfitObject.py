import util as u
from tkinter import *

class GalfitObject:
    def __init__(self, frame, num, start=0, objType=None):
        self.startline = start
        self.endline = len(u.all_pars)
        self.num = int(num)
        self.type = objType
        self.params = []
        if self.num == 0:
            text="Galfit parameters:"
        else:
            text = "Object "+str(self.num)+":"
        self.label = Label(frame, text=text, font=titlefont)
        self.button = Button(frame, text="Remove object", command=lambda:self.remove())
    
    def gridAll(self):
        if self.type == 'sky':
            return
        self.label.grid(row=u.count, column=0, sticky='w')
        if self.type != None:
            self.button.grid(row = u.count, column=1, sticky='w')
        u.count += 1
        for param in self.params:
            param.grid()
    
    def ungridAll(self):
        self.label.grid_remove()
        for param in self.params:
            param.ungrid()
    
    def saveAll(self):
        for param in self.params:
            param.save()
        u.writeFile()
    
    def remove(self):
        u.all_objects.remove(self)
        u.all_pars = u.all_pars[:self.startline]+u.all_pars[self.endline:]
        u.writeFile()
        reloadGUI()