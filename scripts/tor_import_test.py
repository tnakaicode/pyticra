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

if __name__ == "__main__":
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--tor", dest="tor",
                      default="../project/working/project.tor")
    opt, argc = parser.parse_args(argvs)
    print(argc, opt)

    tor_file = opt.dir + "/Project.tor"
    tci_file = opt.dir + "/Project.tci"

    tor_obj = ObjectRepository()
    tor_obj.load(tor_file)

    print(tor_obj)
    print(tor_obj.items())
