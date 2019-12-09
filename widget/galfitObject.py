import util

class galfitObject:
    def __init__(self, num, start=0, objType=None):
        self.startline = start
        self.endline = len(util.all_pars)
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
        if self.type == 'sky':
            return
        self.label.grid(row=util.count, column=0, sticky='w')
        if self.type != None:
            self.button.grid(row = util.count, column=1, sticky='w')
        util.count += 1
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
        util.all_objects.remove(self)
        util.all_pars = util.all_pars[:self.startline]+util.all_pars[self.endline:]
        writeFile()
        reloadGUI()