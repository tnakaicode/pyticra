import numpy as np
import matplotlib.pyplot as plt
import json
import glob
import sys
import time
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
from linecache import getline, clearcache
from optparse import OptionParser

from pyticra.Object import ObjectRepository
from pyticra.input import Project

if __name__ == "__main__":
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--tor", dest="tor",
                      default="../project/working/project.tor")
    opt, argc = parser.parse_args(argvs)
    print(argc, opt)

    prj = Project()
    prj.create("./temp_000/")
