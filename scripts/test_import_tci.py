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
    parser.add_argument("--tci", dest="tci",
                        default="../project/working/project.tci")
    opt = parser.parse_args()
    print(opt)

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
    #print(tci_obj)
    for command in tci_obj.parsed:
        print(command.__str__())
    tci_obj.save(tci_file, batch_mode=False)
