import numpy as np
import matplotlib.pyplot as plt
import json
import glob
import sys
import time
import os
import argparse
from linecache import getline, clearcache
from mpl_toolkits.axes_grid1 import make_axes_locatable

from pyticra.input import ObjectRepository, CommandInterface
from pyticra.grasp_data import GraspGrid

if __name__ == "__main__":
    argvs = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--tor", dest="tor",
                        default="../project/working/project.tor")
    opt = parser.parse_args()
    print(opt)

    dir_name = os.path.dirname(opt.tor) + "/"
    sub_name = os.path.basename(os.path.dirname(opt.tor))
    rootname, ext_name = os.path.splitext(opt.tor)
    print(dir_name, sub_name)
    print(rootname)

    job_name = sub_name
    tor_file = rootname + ".tor"
    tci_file = rootname + ".tci"

    tor_obj = ObjectRepository()
    tor_obj.load(tor_file)
    for obj_name in tor_obj.keys():
        print(tor_obj[obj_name])
    tor_obj.save(tor_file)
