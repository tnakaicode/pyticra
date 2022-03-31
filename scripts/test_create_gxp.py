from os import name
import numpy as np
import matplotlib.pyplot as plt
import json
import glob
import sys
import time
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
from linecache import getline, clearcache
import argparse

from pyticra.input import Project

if __name__ == "__main__":
    argvs = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", dest="dir", default="./temp_000/")
    parser.add_argument("--name", dest="name",default="Project")
    opt = parser.parse_args()
    print(argc, opt)

    prj = Project(name=opt.name)
    prj.create(opt.dir)
