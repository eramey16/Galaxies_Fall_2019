import util

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
        self.label.grid(row=util.count, column=0, sticky='w')
        self.entry.grid(row=util.count, column=1, sticky='w')
        util.count += 1
    
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
        newstring = util.all_pars[self.line][:self.start] + newText + space + util.all_pars[self.line][self.end:]
        util.all_pars[self.line] = newstring
        self.end = self.start+len(newText)+len(space)
        
    def save(self):
        newVal = self.entry.get()
        if newVal != self.prevVal:
            self.writeNewVal()
            self.prevVal = newVal