import numpy as np
import matplotlib.pyplot as plt
import sys
import time
import os
import subprocess
from optparse import OptionParser

from src.RayTrace.ray_setup import get_axs

from OCC.Core.TopoDS import TopoDS_Iterator, topods_Vertex
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TColgp import TColgp_Array1OfPnt, TColgp_Array2OfPnt
from OCC.Core.TColgp import TColgp_HArray1OfPnt, TColgp_HArray2OfPnt
from OCC.Core.BRep import BRep_Builder
from OCC.Extend.DataExchange import read_step_file_with_names_colors
from OCC.Extend.ShapeFactory import make_vertex


def split_filename(filename="../temp_20200408000/not_ignore.txt"):
    name = os.path.basename(filename)
    dir_name = os.path.dirname(filename)
    sub_name = os.path.basename(os.path.dirname(filename))
    rootname, ext_name = os.path.splitext(name)
    return rootname, dir_name, sub_name


if __name__ == "__main__":
    argvs = sys.argv
    parser = OptionParser()
    parser.add_option("--job", dest="job",
                      default="./Project/Job_01/Job_01.tor")
    opt, argc = parser.parse_args(argvs)
    print(argc, opt)

    ticra_tool = r'C:\Program Files\TICRA\TICRA-Tools-19.1.1\bin\ticra-tools.exe'

    root_dir = os.getcwd()
    tor_file = root_dir + opt.job
    rootname, dir_name, sub_name = split_filename(opt.job)
    print(dir_name, sub_name)
    print(rootname)

    os.chdir("{}/input/".format(root_dir))
    os.system(
        "python surf.py --rxy=500.0 500.0 --dir=org_cor/ --surf=m3".format(tor_file))
    os.system("python setup_tor_test.py --tor={}".format(tor_file))
    os.system(
        "python setup_tor_dielectirc.py --tor={} --inpt={:.2f}".format(tor_file, 4.0 * 10**5))
    os.system(
        "python setup_tor_val.py --tor={} --name=radi_system --inpt=250.0".format(tor_file))
    os.system(
        "python setup_tor_val.py --tor={} --name=port_length --inpt=50.0".format(tor_file))
    os.chdir("{}/{}".format(root_dir, dir_name))
    subprocess.call(
        ticra_tool + " batch.gxp {}.out {}.log -nif".format(sub_name, sub_name))
    os.chdir("{}/output/".format(root_dir))
    os.system("python job.py --tor={} --flag=-1 --surf=m1".format(tor_file))
    os.system("python job.py --tor={} --flag=+1 --surf=m2".format(tor_file))
    os.system("python job.py --tor={} --flag=+1 --surf=m3".format(tor_file))
    os.system("python job.py --tor={} --flag=+1 --surf=m2_port1".format(tor_file))
    os.system("python job.py --tor={} --flag=+1 --surf=m2_port2".format(tor_file))
    os.chdir("{}".format(root_dir))
