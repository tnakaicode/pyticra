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

from src.ticra_grammar import Quantity, Ref, Function, Sequence, Struct, Physical, Command, BatchCommand, table
from src.ticra_grammar import Grammar


if __name__ == '__main__':
    argvs = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", dest="name", default="freq")
    opt = parser.parse_args()
    print(opt, argvs)

    # layer_info       : sequence
    #  struct(thickness: 0.0 m, substrate: ref(), el_par_index: 1),
    #  struct(thickness: 0.0 m, substrate: ref(), el_par_index: 2),
    # NG ->
    #  struct(thickness: 0.0 m, substrate: ref(Rogers6002), el_par_index: 1),
    #  struct(thickness: 0.0 m, substrate: ref(Rogers6002), el_par_index: 2),
    # OK

    txt, tor_file = """
periodic_unit_cell_planar_mesh  periodic_unit_cell_planar_mesh  
(
  frequency        : ref(frequency),
  unit_cell_size   : struct(x: 3.816 mm, y: 3.816 mm, skew_angle: 90.0, baseline: x),
  element_parameters : sequence
    (    struct(file_name: triple_dipoles_ratio.msh, unit: m),
         struct(file_name: triple_dipoles_ratio.msh, unit: m)
    ),
  layer_info       : sequence
    (    
         struct(thickness: 0.0 m, substrate: ref(), el_par_index: 1),
         struct(thickness: 0.127 mm, substrate: ref(Rogers6002), el_par_index: 0),
         struct(thickness: 0.0 m, substrate: ref(Rogers6002), el_par_index: 2),
         struct(thickness: 0.762 mm, substrate: ref(Rogers6002), el_par_index: 0)
    ),
  parameter_assignments : table
    (
    rot  "pi()/2"      1  
    L2    2.00000E-03      1  
    L2    2.00000E-03      2  
    ),
  analysis_settings : ref(periodic_mom_settings_layered_media)
)
""", "./ticra_ErrorTor/Analysis_and_Optimisation_of_PUC.tor"
    # parameter_assignments : table

    txt, tor_file = """
mode_launcher  circular_waveguide_grooved_step  
(
  frequency        : ref(frequency),
  port_1           : ref(port_mode_launcher_input),
  port_2           : ref(port_phasing_section_input),
  length_1         : "ref(ml_l1)" mm,
  length_2         : "ref(ml_l1)" mm,
  grooves          : sequence(    
         struct(centre: "360-ref(ml_slot_offset)", 
                width: "ref(ml_slot_width)", 
                length: "ref(ml_l2)" mm
                ),
         struct(centre: "ref(ml_slot_offset)", 
                width: "ref(ml_slot_width)", 
                length: "ref(ml_l2)+1" mm
                ),
         "ref(ml_l2)+ref(ml_l2)" mm
    ),
    analysis_settings : ref(mom_settings)
)
""", "./ticra_ErrorTor/Matched_Feed.tor"
    # length_2         : "ref(ml_l3)+ref(ml_l2)" mm
    # "ref(ml_l3)+ref(ml_l2)" mm -> NG
    # "1+ref(ml_l2)" mm -> NG
    # "ref(ml_l3)" mm -> OK
    #
    # "./ticra_ErrorTor/Orthomode_Transducer.tor" line:440
    # "ref(rwg_bend_inner_radius_1)+ref(rwg1_bdim)/2" mm -> NG
    # no solution
    # input_radius     : "(5.6-2*2.19)/2" mm,

    grm = Grammar()
    print(grm.object_repository.parse_string(txt))
    # grm.object_repository.parse_file(tor_file)

    def try_tor(torfile, i, name):
        try:
            grm.object_repository.parse_file(torfile)
            print(i, name)
        except Exception as e:
            print(i, name, e)

    tor_file = "./Project/working/Project.tor"
    try_tor(tor_file, 0, "Project")

    # tor_file = "C:/Program Files/TICRA/TICRA-Tools-23.0/TutorialCases/Parameter_Sweep/working/Parameter_Sweep.tor"
    # for physical in Grammar.object_repository.parseFile(tor_file):
    #    print (physical.display_name, physical)

    for i, name in enumerate(os.listdir("./ticra_ErrorTor/")):
        tor_file = "./ticra_ErrorTor/" + name
        try_tor(tor_file, i, name)


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
