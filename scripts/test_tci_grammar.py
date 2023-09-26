import numpy as np
import matplotlib.pyplot as plt
import pyparsing as p
import sys
import os
import time
import glob
import argparse
from collections import OrderedDict
from linecache import getline, clearcache

from pyticra.base import Grammar


if __name__ == '__main__':
    argvs = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", dest="name", default="freq")
    opt = parser.parse_args()
    print(opt, argvs)

    txt, tor_file = """
COMMAND OBJECT local.coor_sys get_coor_sys ( base : ref(global.coor_sys),  ref : ref(global.coor_sys)) 
COMMAND OBJECT local.coor_sys get_coor_sys ( base : ref(global.coor_sys)) 
QUIT """, "./ticra_ErrorTor/Matched_Feed.tor"

    grm = Grammar()
    tci = grm.command_interface.parse_string(txt)
    print(tci)
    print(tci[0][0])
    print(tci[0][0]["base"])
    tci[0][0]["base"] = "ref(local.coor_sys)"
    print(tci)
    # grm.object_repository.parse_file(tor_file)
