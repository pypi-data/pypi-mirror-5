# design_output.py
# generates output design files from a figure
# created by charlyoleg on 2013/08/27
#
# (C) Copyright 2013 charlyoleg
#
# This file is part of the Cnc25D Python package.
# 
# Cnc25D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cnc25D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Cnc25D.  If not, see <http://www.gnu.org/licenses/>.


"""
design_output.py is part of the Cnc25D API.
it provide macro that are commonly used to generate the output files of a design
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import importing_freecad
importing_freecad.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

# Python standard library
import math
import sys, argparse
#from datetime import datetime
#import os, errno
import os
import re
#import Tkinter # to display the outline in a small GUI
# FreeCAD
import Part
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import outline_backends
import export_2d
import design_help


################################################################
# help functions
################################################################

################################################################
# functions to be reused
################################################################

def generate_output_file_add_argument(ai_parser):
  """ Add the argparse switch --output_file_basename
  """
  r_parser = ai_parser
  r_parser.add_argument('--output_file_basename','--ofb', action='store', default='', dest='sw_output_file_basename',
    help="If not  the empty_string (the default value), it outputs the (first) gear in file(s) depending on your argument file_extension: .dxf uses mozman dxfwrite, .svg uses mozman svgwrite, no-extension uses FreeCAD and you get .brep and .dxf")
  # return
  return(r_parser)
  
def generate_output_file(ai_figure, ai_output_filename, ai_height):
  """ implement the swith --output_file_basename
  """
  if(ai_output_filename!=''):
    # create the output directory if needed
    l_output_dir = os.path.dirname(ai_output_filename)
    design_help.mkdir_p(l_output_dir)
    #l_output_basename = os.path.basename(ai_output_filename)
    #print("dbg449: l_output_basename:", l_output_basename)
    # mozman dxfwrite
    if(re.search('\.dxf$', ai_output_filename)):
      #print("Generate {:s} with mozman dxfwrite".format(ai_output_filename))
      outline_backends.write_figure_in_dxf(ai_figure, ai_output_filename)
    # mozman svgwrite
    elif(re.search('\.svg$', ai_output_filename)):
      #print("Generate {:s} with mozman svgwrite".format(ai_output_filename))
      outline_backends.write_figure_in_svg(ai_figure, ai_output_filename)
    # FreeCAD
    else:
      print("Generate with FreeCAD the BRep file {:s}.brep".format(ai_output_filename))
      freecad_part = outline_backends.figure_to_freecad_25d_part(ai_figure, ai_height)
      freecad_part.exportBrep("{:s}.brep".format(ai_output_filename))
      print("Generate with FreeCAD the DXF file {:s}.dxf".format(ai_output_filename))
      # slice freecad_part  in the XY plan at a height of ai_height/2
      export_2d.export_to_dxf(freecad_part, Base.Vector(0,0,1), ai_height/2, "{:s}.dxf".format(ai_output_filename))
    # return
    return(0)

################################################################
# test-functions
################################################################


