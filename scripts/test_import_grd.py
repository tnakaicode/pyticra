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
from pyticra.grasp_data import GraspGrid

if __name__ == "__main__":
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--tor", dest="tor",
                      default="../project/working/project.tor")
    opt, argc = parser.parse_args(argvs)
    print(argc, opt)

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

    meta = {}
    meta["e"] = {}
    grd_data = GraspGrid(dir_name + "front_reflector.e.grd", meta["e"])
    grd_data.get_data("e", 0)
    print(meta["e"].keys())

    meta["cur"] = {}
    grd_data = GraspGrid(dir_name + "front_reflector.cur.grd", meta["cur"])
    grd_data.get_data("cur", 0)
    print(meta["cur"].keys())
