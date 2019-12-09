# GUI interface
from tkinter import Menu
from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk
# Graphing
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

import util as u
from paramObject import ParamObject
from galfitObject import GalfitObject

class Widget:
    