import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time
import glob
import shutil
import argparse
from linecache import getline, clearcache

from pyticra.base import Grammar

if __name__ == '__main__':
    argvs = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", dest="name", default="freq")
    opt = parser.parse_args()
    print(opt, argvs)

    grm = Grammar()
    tor_file = "./project/working/project.tor"
    try:
        grm.object_repository.parse_file(tor_file)
    except Exception as e:
        print(e)

    dir_name = "c:/Program Files/TICRA/TICRA-Tools-23.0/TutorialCases/"
    # print(glob.glob(dir_name + "/*"))
    print(os.listdir(dir_name))
    for i, name in enumerate(os.listdir(dir_name)):

        tor_file = dir_name + name + "/working/" + name + ".tor"
        try:
            grm.object_repository.parse_file(tor_file)
            print(i, name)
        except Exception as e:
            print(i, name, e)
        shutil.copyfile(tor_file, "./torfile/" + name + ".tor")


#  0 Analysis_and_Optimisation_of_PUC
#  1 Analysis_of_PUC
#  2 Array_Fed_Reflector
#  3 BoR_MoM_with_Offset_Feed
#  4 CouplingBetweenTwoAntennas
#  5 Dielectric_Waveguide_Filter
#  6 Diffraction_Scattering_in_CATR
#  7 Diplexer
#  8 Dual_Gridded_Refl
#  9 Dual_Gridded_Refl_with_Stiffeners
# 10 Dual_Gridded_Refl_with_Support_Ring
# 11 Dual_Refl_with_Blockage
# 12 Dual_Refl_with_Panels_and_Struts
# 13 Dual_Refl_with_Shaped_Surfaces
# 14 Ext_Command_Plugin
# 15 FrontEnd_Design_Cassegrain
# 16 Helixes_Radome_Satellite
# 17 Horn_with_Lens
# 18 Intro_Optimisation
# 19 Lens_Refractor
# 20 Matched_Feed Expected end of text, found 'mode'  (at char 5559), (line:186, col:1)
# 21 MGTD_Dual_Reflector
# 22 NASA_Almond
# 23 Offset_Reflector_in_Radome
# 24 Optimisation_of_Reflectarray
# 25 Optim_and_Analysis_of_Multibeam_Direct_Radiating_Array
# 26 Optim_and_analysis_of_multibeam_reflector
# 27 Optim_of_QZ_in_CATR
# 28 Orthomode_Transducer Expected end of text, found 'rwg'  (at char 11295), (line:440, col:1)
# 29 Parameter_Sweep
# 30 Parametric_Helix_Antenna
# 31 Patch_Antenna_with_Dielectric
# 32 Platform_Scattering_from_CubeSat __init__() takes from 2 to 3 positional arguments but 4 were given
# 33 Potter_Horn
# 34 PUC3D_tutorial
# 35 QuasiOpticalFrame
# 36 Reflector_with_Corrugated_Horn
# 37 Ridge_Waveguide_Devices Expected end of text, found 'Horn'  (at char 730), (line:35, col:1)
# 38 Setup_and_Analysis_of_Reflectarray
# 39 Single_Offset_Shaped_Reflector_for_Cosecant_Beam
# 40 Single_Refl_with_Three_Struts
# 41 Single_Shaped_Reflector_in_CP_and_Tabulated_Rim
# 42 Sing_Refl_Shap_LeastSquares
# 43 Sing_Refl_Shap_rim_indent_curv_cons
# 44 Standard_Gain_Horn_with_Waveguide_Input
# 45 UQ_Analysis_of_Multibeam_Direct_Radiating_Array
# 46 UQ_axial_horn Expected end of text, found 'axial'  (at char 1093), (line:52, col:1)
# 47 UQ_Large_Deployable_Mesh_Reflector
# 48 UQ_Patch_Antenna
# 49 UQ_Reflectarray
# 50 User_Terminal_Antenna Expected end of text, found 'port'  (at char 2144), (line:80, col:1)
# 51 Waveguide_Fed_Horn_with_Offset_Reflector
