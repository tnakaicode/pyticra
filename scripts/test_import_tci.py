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

from pyticra.input import CommandInterface

if __name__ == "__main__":
    argvs = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--tci", dest="tci",
                      default="../project/working/project.tci")
    opt = parser.parse_args()
    print(argc, opt)

    dir_name = os.path.dirname(opt.tci) + "/"
    sub_name = os.path.basename(os.path.dirname(opt.tci))
    rootname, ext_name = os.path.splitext(opt.tci)
    print(dir_name, sub_name)
    print(rootname)

    job_name = sub_name
    tor_file = rootname + ".tor"
    tci_file = rootname + ".tci"

    tci_obj = CommandInterface()
    tci_obj.load(tci_file)
    print(tci_obj.parsed)
    print(tci_obj)
