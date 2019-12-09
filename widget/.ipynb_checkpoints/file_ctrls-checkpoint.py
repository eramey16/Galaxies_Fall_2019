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

# Checks if the parameter file is user defined
# returns the temp file if not
# returns the user-defined file if so
def checkPar():
    if usr_parfile==None: # not usr-defined
        return parfile
    else: # usr-defined
        return usr_parfile

# Reads the parameter file into all_pars
def readFile():
    global all_pars
    p = checkPar()
    with open(p) as f: # read lines
        all_pars = f.readlines()

# Writes the current all_pars to the parameter file
def writeFile():
    global all_pars
    p = checkPar()
    with open(p, 'w') as f: # write lines
        f.writelines(all_pars)

