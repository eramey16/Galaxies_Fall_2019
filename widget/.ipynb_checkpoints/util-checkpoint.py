### file_ctrls.py - methods for file I/O in galfit widget
### Author: Emily Ramey
### Date: 12/09/19

### file paths
tmp_path = ".galfit/" # folder for temporary files
usr_parfile = None
parfile = tmp_path+"galfit-example/EXAMPLE/galfit_test.feedme" # param file # maybe download from internet later
original_parfile = tmp_path+"galfit-example/EXAMPLE/galfit.feedme" # parfile to reset if things go awry
fitsfile = tmp_path+"imgblock.fits" # image file
imgfile = tmp_path+"tmp_img.png"

# global variables
count = 0
all_pars = []
all_objects = []
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
