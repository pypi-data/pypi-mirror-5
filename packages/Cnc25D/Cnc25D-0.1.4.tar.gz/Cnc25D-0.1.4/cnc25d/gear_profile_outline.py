# gear_profile_outline.py
# sub-module of gear_profile
# created by charlyoleg on 2013/09/07
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
gear_profile_outline.py is a sub-module of gear_profile.py
It has been created to split the too large gear_profile.py file into two smaller files, easier for editing.
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import cnc25d_api
#cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

# Python standard library
import math
#import sys, argparse
import sys
#from datetime import datetime
#import os, errno
#import re
#import Tkinter # to display the outline in a small GUI
# FreeCAD
#import Part
#from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import small_geometry # use some well-tested functions from the internal of the cnc25d_api

################################################################
# module variable
################################################################
gpo_radian_epsilon = math.pi/1000

################################################################
# gear_profile help functions (including involute_to_circle)
################################################################

#############################################################################
# make gear_profile_outline
#############################################################################

def involute_to_circle(ai_center, ai_base_radius, ai_initial_angle, ai_orientation, ai_parameter):
  """ Compute the Cartesian coordinates of P a point of an involute_to_circle curve with the parameter u
      ai_center: center of the base circle (O)
      ai_base_radius: radius of the base circle (B)
      ai_initial_angle : angle (xOS) with (S) start of of the involute_to_circle
      ai_orientation: orienation of the involute_to_circle: 1=CCW -1=CW
      it returns: the Cartesian coordinates of (P) and the tangent inclination (xPt)
  """
  # use notation of the documentation
  OX = ai_center[0]
  OY = ai_center[1]
  B = ai_base_radius
  s = ai_initial_angle
  rd = ai_orientation
  u = ai_parameter
  # check the parameter
  if(u<0):
    print("ERR099: Error, the parameter of the involute_to_circle must be positive {:0.8f}".format(u))
    print("dbg887: ai_center {:0.2f} {:0.2f}  ai_base_radius {:0.2f}  ai_initial_angle {:0.2f}  ai_orientation {:d}  ai_parameter {:0.2f}".format(ai_center[0], ai_center[1], ai_base_radius, ai_initial_angle, ai_orientation, ai_parameter))
    sys.exit(2)
  # involute_to_circle of center (0,0), radius 1 and initial_angle = 0 with the parameter u
  px0 = math.cos(u)+u*math.sin(u)
  py0 = rd*(math.sin(u)-u*math.cos(u))
  ti0 = math.fmod(rd*u+math.pi, 2*math.pi) - math.pi # =u translated in [-pi,pi[
  # involute_to_circle of center (OX,OY), radius B and initial_angle = s with the parameter u
  px = OX+math.cos(s)*B*px0-math.sin(s)*B*py0
  py = OY+math.sin(s)*B*px0+math.cos(s)*B*py0
  ti = math.fmod(ti0+s+3*math.pi, 2*math.pi) - math.pi #=u+s translated in [-pi,pi[
  # return
  r_itc=(px, py, ti)
  return(r_itc)

def search_point_of_involute_to_circle(ai_center, ai_base_radius, ai_initial_angle, ai_orientation, ai_altitude, ai_step, ai_precision):
  """ Compute the coordinates of the intersection (P) of an involute_to_circle curve and a circle of raidus ai_altitude
      ai_center: center of the base circle and of the other circle (O)
      ai_base_radius: radius of the base circle (B)
      ai_initial_angle : angle (xOS) with (S) start of of the involute_to_circle
      ai_orientation: orienation of the involute_to_circle: 1=CCW -1=CW
      ai_altitude: radius of the other circle
      ai_step: initial increment of the parameter to converge to (P)
      ai_precision: required precision to get closer to ai_altitude
      it returns: the paramter u, the angle (xOP), the Cartesian coordinates of (P), the tangent inclination (xPt)
  """
  #print("dbg974: ai_center:", ai_center)
  #print("dbg975: ai_base_radius:", ai_base_radius)
  #print("dbg976: ai_initial_angle:", ai_initial_angle)
  #print("dbg977: ai_orientation:", ai_orientation)
  #print("dbg978: ai_altitude:", ai_altitude)
  #print("dbg979: ai_step:", ai_step)
  #print("dbg980: ai_precision:", ai_precision)
  # use notation of the documentation
  OX = ai_center[0]
  OY = ai_center[1]
  B = ai_base_radius
  s = ai_initial_angle
  rd = ai_orientation
  R = ai_altitude
  # check the paramter
  if(R<B):
    print("ERR098: Error, the altitude {:0.2f} is smaller than the base_diameter {:0.2f}".format(R, B))
    sys.exit(2)
  ### method 1
  ## converge to P
  #u = 0
  #step = ai_step
  #error = -2*ai_precision
  #iteration_cnt = 0
  #while(abs(error)>ai_precision):
  #  iteration_cnt += 1
  #  #print("dbg351: iteration_cnt: {:d}  u: {:0.6f}  step: {:0.6f}  error: {:0.6f}".format(iteration_cnt, u, step, error))
  #  (px, py, ti) = involute_to_circle((OX,OY), B, s, rd, u)
  #  OP = math.sqrt((px-OX)**2+(py-OY)**2)
  #  sign_old_error = math.copysign(1, error)
  #  error = OP-R
  #  sign_new_error = math.copysign(1, error)
  #  if(sign_old_error*sign_new_error<0):
  #    step = step/2
  #  if(sign_new_error<0):
  #    u=u+step
  #  else:
  #    u=u-step
  ## we get u, px, py and ti
  ## calcultation of a = angle (xOP)
  #a = math.atan2((py-OY)/OP, (px-OX)/OP)
  #r_spoitc = (u, a, px, py, ti)
  ### method 2
  u2 = math.sqrt((R/B)**2-1)
  a2 = s+rd*(u2-math.atan(u2))
  ## compare the result of the two methods
  #if(abs(u2-u)>2*ai_precision)2:
  #  print("ERR877: Error in the calculation of u {:0.3f} or u2 {:0.3f}".format(u, u2))
  #  sys.exit(2)
  #if(abs(a2-a)>2*ai_precision):
  #  print("ERR878: Error in the calculation of a {:0.3f} or a2 {:0.3f}".format(a, a2))
  #  sys.exit(2)
  (px2, py2, ti2) = involute_to_circle((OX,OY), B, s, rd, u2)
  # return
  r_spoitc = (u2, a2, px2, py2, ti2)
  return(r_spoitc)

def sample_of_gear_tooth_profile(ai_center, ai_base_radius, ai_initial_angle, ai_orientation, ai_thickness_offset, ai_parameter):
  """ Compute the Cartesian coordinates of Q a point of a gear_tooth_profile with the parameter u
      ai_center: center of the base circle (O)
      ai_base_radius: radius of the base circle (B)
      ai_initial_angle : angle (xOS) with (S) start of of the involute_to_circle
      ai_orientation: orienation of the involute_to_circle: 1=CCW -1=CW
      ai_thickness_offset: translation apply to P. The translation is perpendicular to the tangent. Positive if move away from (O). Negative if move closer to (O)
      it returns: the Cartesian coordinates of (Q) and the tangent inclination (xPt)
  """
  (px, py, ti) = involute_to_circle(ai_center, ai_base_radius, ai_initial_angle, ai_orientation, ai_parameter)
  #rd = ai_orientation
  #qx = px + ai_thickness_offset*math.cos(ti-rd*math.pi/2) # cos(a-pi/2)=sin(a)   cos(a+pi/2)=-sin(a)
  #qy = py + ai_thickness_offset*math.sin(ti-rd*math.pi/2) # sin(a-pi/2)=-cos(a)  sin(a+pi/2)=cos(a)
  qx = px + ai_orientation*ai_thickness_offset*math.sin(ti)
  qy = py - ai_orientation*ai_thickness_offset*math.cos(ti)
  # return
  r_sogtp = (qx, qy, ti)
  return(r_sogtp)

def calc_low_level_gear_parameters(ai_param):
  """ From the hight level parameters relative to a gearwheel (or gearbar) and returns the low level parameters required to compute the gearwheel outline
      It also adds some parameters to the high-level parameter dictionary ai_param. So this function must be called before calling pre_g2_position_calculation()
  """
  # get the hight level parameters
  g_type  = ai_param['gear_type']
  g_n     = ai_param['full_tooth_nb']
  g_m     = ai_param['module']
  g_pr    = ai_param['primitive_radius']
  g_adp   = ai_param['addendum_dedendum_parity']
  g_thh   = ai_param['tooth_half_height']
  g_ar    = ai_param['addendum_radius']
  g_dr    = ai_param['dedendum_radius']
  g_brp   = ai_param['positive_base_radius']
  g_brn   = ai_param['negative_base_radius']
  g_ox    = ai_param['center_ox']
  g_oy    = ai_param['center_oy']
  g_rbr   = ai_param['gear_router_bit_radius']
  g_hr    = ai_param['hollow_radius']
  g_irp   = ai_param['positive_involute_resolution']
  g_irn   = ai_param['negative_involute_resolution']
  g_stp   = ai_param['positive_skin_thickness']
  g_stn   = ai_param['negative_skin_thickness']
  g_ptn   = ai_param['portion_tooth_nb']
  g_pfe   = ai_param['portion_first_end']
  g_ple   = ai_param['portion_last_end']
  g_bi    = ai_param['gearbar_inclination']
  g_sp    = ai_param['positive_slope_angle']
  g_sn    = ai_param['negative_slope_angle']
  g_ah    = ai_param['addendum_height']
  g_dh    = ai_param['dedendum_height']
  g_hh    = ai_param['hollow_height']
  g_ks    = ai_param['gear_sign']
  # precision
  radian_epsilon = math.pi/1000
  radian_epsilon_2 = math.pi/10000
  ### check
  # tooth height check
  #
  if(g_ks*(g_pr-g_dr)<0):
    print("ERR985: Error, g_pr {:0.2f} and g_dr {:0.2f} are not in the correct order!".format(g_pr, g_dr))
    sys.exit(2)
  if(g_ks*(g_ar-g_pr)<0):
    print("ERR986: Error, g_pr {:0.2f} and g_ar {:0.2f} are not in the correct order!".format(g_pr, g_ar))
    sys.exit(2)
  # involute resolution check
  if(g_irp<1):
    print("ERR786: Error, g_irp {:d} must be equal or bigger than 1!".format(g_irp))
    sys.exit(2)
  if(g_irn<1):
    print("ERR787: Error, g_irn {:d} must be equal or bigger than 1!".format(g_irn))
    sys.exit(2)
  ### calculation of the low level parameters
  r_low_parameters = ()
  if((g_type=='e')or(g_type=='i')):
    ### search points
    initial_step = (g_ar-g_dr)/4
    pi_module_angle = 2*math.pi/g_n
    ai_param['pi_module_angle'] = pi_module_angle
    # intersection of positive involute and the primitive circle
    if(g_brp>g_pr-radian_epsilon):
      print("ERR987: Error, g_brp {:0.2f} is bigger than g_pr {:0.2f}!".format(g_brp, g_pr))
      sys.exit(2)
    (ippu, ippa, ippx, ippy, ippti) = search_point_of_involute_to_circle((g_ox, g_oy), g_brp, 0, 1, g_pr, initial_step, radian_epsilon_2)
    #ai_param['low_positive_primitive_angle'] = ippa
    # intersection of negative involute and the primitive circle
    if(g_brn>g_pr-radian_epsilon):
      print("ERR988: Error, g_brn {:0.2f} is bigger than g_pr {:0.2f}!".format(g_brp, g_pr))
      sys.exit(2)
    (inpu, inpa, inpx, inpy, inpti) = search_point_of_involute_to_circle((g_ox, g_oy), g_brn, 0, -1, g_pr, initial_step, radian_epsilon_2)
    #ai_param['low_negative_primitive_angle'] = inpa
    # intersection of positive involute and the addendum circle
    ipau=0; ipaa=0;
    if(g_brp<g_ar): # check for internal gear
      (ipau, ipaa, ipax, ipay, ipati) = search_point_of_involute_to_circle((g_ox, g_oy), g_brp, 0, 1, g_ar, initial_step, radian_epsilon_2)
    ai_param['low_positive_addendum_angle'] = ipaa
    # intersection of negative involute and the addendum circle
    inau=0; inaa=0;
    if(g_brn<g_ar): # check for internal gear
      (inau, inaa, inax, inay, inati) = search_point_of_involute_to_circle((g_ox, g_oy), g_brn, 0, -1, g_ar, initial_step, radian_epsilon_2)
    ai_param['low_negative_addendum_angle'] = inaa
    # intersection of positive involute and the dedendum circle
    ipdu=0; ipda=0;
    if(g_brp<g_dr): # check for external gear
      (ipdu, ipda, ipdx, ipdy, ipdti) = search_point_of_involute_to_circle((g_ox, g_oy), g_brp, 0, 1, g_dr, initial_step, radian_epsilon_2)
    #ai_param['low_positive_dedendum_angle'] = ipda
    # intersection of negative involute and the dedendum circle
    indu=0; inda=0;
    if(g_brn<g_dr): # check for external gear
      (indu, inda, indx, indy, indti) = search_point_of_involute_to_circle((g_ox, g_oy), g_brn, 0, -1, g_dr, initial_step, radian_epsilon_2)
    #ai_param['low_negative_dedendum_angle'] = inda
    #
    full_positive_involute = g_ks*(ipaa-ipda)
    full_negative_involute = -1*g_ks*(inaa-inda)
    addendum_positive_involute = g_ks*(ipaa-ippa)
    addendum_negative_involute = -1*g_ks*(inaa-inpa)
    dedendum_positive_involute = g_ks*(ippa-ipda)
    dedendum_negative_involute = -1*g_ks*(inpa-inda)
    #print("dbg646: full_positive_involute: {:0.3f}  full_negative_involute: {:0.3f}  addendum_positive_involute: {:0.3f}  addendum_negative_involute: {:0.3f}  dedendum_positive_involute: {:0.3f}  dedendum_negative_involute: {:0.3f}".format(full_positive_involute, full_negative_involute, addendum_positive_involute, addendum_negative_involute, dedendum_positive_involute, dedendum_negative_involute))
    top_land = pi_module_angle*g_adp-(addendum_positive_involute+addendum_negative_involute)
    if(top_land*g_ar<radian_epsilon): # a bit stricter than 0
      print("ERR989: Error, the top_land {:0.2f} is negative or too small!".format(top_land))
      print("dbg553: g_pr {:0.3f}  g_brp {:0.3f}  g_brn {:0.3f}".format(g_pr, g_brp, g_brn))
      sys.exit(2)
    bottom_land = pi_module_angle*(1-g_adp)-(dedendum_positive_involute+dedendum_negative_involute)
    if(bottom_land*g_dr<2*g_rbr+radian_epsilon): # a bit stricter than router_bit_radius
      print("ERR990: Error, the bottom_land {:0.2f} is negative or too small compare to the router_bit_radius {:0.2f} ({:0.2f} < {:0.2f})!".format(bottom_land, g_rbr, bottom_land*g_dr, 2*g_rbr))
      sys.exit(2)
    ai_param['top_land'] = top_land
    ai_param['bottom_land'] = bottom_land
    ai_param['addendum_positive_involute'] = addendum_positive_involute
    ai_param['addendum_negative_involute'] = addendum_negative_involute
    ai_param['dedendum_positive_involute'] = dedendum_positive_involute
    ai_param['dedendum_negative_involute'] = dedendum_negative_involute
    ai_param['full_positive_involute'] = full_positive_involute
    ai_param['full_negative_involute'] = full_negative_involute
    if(g_type=='e'): # negative > hollow > positive
      # low1: to create the gear-profile outline
      i1_base = g_brn
      i1_offset = top_land/2-inaa
      i1_sign = -1
      i1u_nb = g_irn
      i1u_ini = inau
      i1u_inc = (indu-inau)/i1u_nb # <0
      i1_thickness = g_stn
      i2_base = g_brp
      i2_offset = pi_module_angle-top_land/2-ipaa
      i2_sign = 1
      i2u_nb = g_irp
      i2u_ini = ipdu
      i2u_inc = (ipau-ipdu)/i2u_nb # >0
      i2_thickness = g_stp
      ha1 = top_land/2 + full_negative_involute
    elif(g_type=='i'): # positive > hollow > negative
      # low1
      i1_base = g_brp
      i1_offset = top_land/2-ipaa
      i1_sign = 1
      i1u_nb = g_irp
      i1u_ini = ipau
      i1u_inc = (ipdu-ipau)/i1u_nb # >0
      i1_thickness = g_stp
      i2_base = g_brn
      i2_offset = pi_module_angle-top_land/2-inaa
      i2_sign = -1
      i2u_nb = g_irn
      i2u_ini = indu
      i2u_inc = (inau-indu)/i2u_nb # >0
      i2_thickness = g_stn
      ha1 = top_land/2 + full_positive_involute
      #print("dbg663: ipaa {:0.3f}".format(ipaa))
    #
    #pi_module_angle = 2*math.pi/g_n
    hl1 = g_dr
    hl2 = g_hr
    #ha1 = top_land/2 + full_negative_involute or full_positive_involute
    ha2 = ha1 + bottom_land
    hlm = hl2*math.cos(bottom_land/2) # this is to ensure nice junction of split gearwheel
    ham = ha1 + bottom_land/2
    tlm = g_ar*math.cos(top_land/2) # this is to ensure nice junction of split gearwheel
    if(g_ptn==0):
      portion_tooth_nb = g_n
      closed = True
    else:
      portion_tooth_nb = g_ptn
      closed = False
    # return
    make_low_parameters = (g_type, pi_module_angle,
      i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_thickness,
      i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_thickness,
      hl1, hl2, ha1, ha2, g_rbr, hlm, ham, tlm,
      g_ox, g_oy, portion_tooth_nb, g_pfe, g_ple, closed)
    # info
    info_txt = "Gear profile details:\n"
    info_txt += "positive involute: \t{:0.3f} (radian)  \t{:0.3f} (mm)  \t{:0.2f} %\n".format(full_positive_involute, g_pr*full_positive_involute, 100*full_positive_involute/pi_module_angle)
    info_txt += "negative involute: \t{:0.3f} (radian)  \t{:0.3f} (mm)  \t{:0.2f} %\n".format(full_negative_involute, g_pr*full_negative_involute, 100*full_negative_involute/pi_module_angle)
    info_txt += "top land:          \t{:0.3f} (radian)  \t{:0.3f} (mm)  \t{:0.2f} %\n".format(top_land, g_ar*top_land, 100*top_land/pi_module_angle)
    info_txt += "bottom land:       \t{:0.3f} (radian)  \t{:0.3f} (mm)  \t{:0.2f} %\n".format(bottom_land, g_dr*bottom_land, 100*bottom_land/pi_module_angle)
  elif(g_type=='l'):
    # linear gear make low parameters
    pi_module = g_m * math.pi
    positive_addendum = g_ah*math.tan(g_sp)
    positive_dedendum = abs(g_dh)*math.tan(g_sp)
    negative_addendum = g_ah*math.tan(g_sn)
    negative_dedendum = abs(g_dh)*math.tan(g_sn)
    full_positive_slope = positive_addendum + positive_dedendum
    full_negative_slope = negative_addendum + negative_dedendum
    top_land = pi_module*g_adp-(positive_addendum+negative_addendum)
    bottom_land = pi_module*(1-g_adp)-(positive_dedendum+negative_dedendum)
    if(top_land<radian_epsilon):
      print("ERR858: Error, the linear gear top-land {:0.3f} is negative or too small!".format(top_land))
      sys.exit(2)
    if(bottom_land<2*g_rbr+radian_epsilon):
      print("ERR859: Error, the linear gear bottom-land {:0.3f} is too small compare to the gear_router_bit_radius {:0.3f}".format(bottom_land, g_rbr))
      sys.exit(2)
    ai_param['top_land'] = top_land
    ai_param['bottom_land'] = bottom_land
    ai_param['addendum_positive_slope'] = positive_addendum
    ai_param['addendum_negative_slope'] = negative_addendum
    ai_param['dedendum_positive_slope'] = positive_dedendum
    ai_param['dedendum_negative_slope'] = negative_dedendum
    ai_param['full_positive_slope'] = full_positive_slope
    ai_param['full_negative_slope'] = full_negative_slope
    bar_tooth_nb = g_n
    if(g_ptn>0):
      bar_tooth_nb = g_ptn
    middle_tooth = int(bar_tooth_nb/2)+1
    tlh = g_ah
    blh = g_dh + g_hh
    blx = top_land/2 + negative_addendum + negative_dedendum + bottom_land/2
    g_alp = g_ah/math.cos(g_sp)
    g_dlp = g_dh/math.cos(g_sp)
    g_hlp = g_hh/math.cos(g_sp)
    g_aln = g_ah/math.cos(g_sn)
    g_dln = g_dh/math.cos(g_sn)
    g_hln = g_hh/math.cos(g_sn)
    gb_p_offset = top_land/2+positive_addendum
    gb_n_offset = -1*(top_land/2+negative_addendum)
    # return
    make_low_parameters = (g_type, pi_module, g_ox, g_oy, g_bi, bar_tooth_nb, middle_tooth, g_pfe, g_ple, tlh, blh, blx,
                            g_sp, g_sn, g_alp, g_dlp, g_hlp, g_aln, g_dln, g_hln, g_rbr, g_stp, g_stn, gb_p_offset, gb_n_offset)
    # info
    info_txt = "Gearbar profile details:\n"
    info_txt += "positive slope: \t{:0.3f} (mm)  \t{:0.2f} %\n".format(full_positive_slope, 100*full_positive_slope/pi_module)
    info_txt += "negative slope: \t{:0.3f} (mm)  \t{:0.2f} %\n".format(full_negative_slope, 100*full_negative_slope/pi_module)
    info_txt += "top land:          \t{:0.3f} (mm)  \t{:0.2f} %\n".format(top_land, 100*top_land/pi_module)
    info_txt += "bottom land:       \t{:0.3f} (mm)  \t{:0.2f} %\n".format(bottom_land, 100*bottom_land/pi_module)
  else:
    print("ERR740: Error, the gear_type {:s} doesn't exist!".format(g_type))
    sys.exit(2)
  #return
  r_cllgp = (make_low_parameters, info_txt)
  return(r_cllgp)

def involute_outline(ai_ox, ai_oy, ai_base_radius, ai_offset, ai_sign, ai_u_nb, ai_u_ini, ai_u_inc, ai_thickness, ai_tooth_angle):
  """ from subset of low-level parameter, generates an involute_to_circle format B outline
  """
  # precision
  #radian_epsilon=math.pi/1000 # unefficient because this function is used often
  radian_epsilon = gpo_radian_epsilon
  #
  u = ai_u_ini
  involute_C = []
  for sampling in range(ai_u_nb+1):
    #print("dbg443: u:", u)
    if(abs(u)<radian_epsilon): # for rounding error
      u=0
    (qx, qy, ti) = sample_of_gear_tooth_profile((ai_ox,ai_oy), ai_base_radius, ai_tooth_angle+ai_offset, ai_sign, ai_thickness, u)
    involute_C.append((qx, qy, ti-(ai_sign-1)/2*math.pi))
    u += ai_u_inc
  #print("dbg444: involute_C:", involute_C)
  r_involute_B = cnc25d_api.smooth_outline_c_curve(involute_C, radian_epsilon, 0, "involute_outline")
  return(r_involute_B)

def gearwheel_profile_outline(ai_low_parameters, ai_angle_position):
  """ create the outline of a gear definied by ai_low_parameters
      The reference of a gearwheel is the middle of its first tooth.
      ai_angle_position sets the reference of the gearwheel.
  """
  # get ai_low_parameters
  (gear_type, pi_module_angle,
    i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_thickness,
    i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_thickness,
    hl1, hl2, ha1, ha2, hrbr, hlm, ham, tlm,
    ox, oy, portion_tooth_nb, first_end, last_end, closed) = ai_low_parameters
  # precision
  #radian_epsilon = math.pi/1000
  radian_epsilon = gpo_radian_epsilon
  # construct the final_outline
  r_final_outline = []
  tooth_angle = ai_angle_position
  ### start of the gearwheel_portion
  if(first_end>0):
    half_hollow = []
    start_of_profile_B = []
    if(first_end==1):
      start_of_profile_B = [(ox+tlm*math.cos(tooth_angle), oy+tlm*math.sin(tooth_angle))]
    else:
      start_of_profile_B = involute_outline(ox, oy, i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_thickness, tooth_angle-pi_module_angle)
      # gearwheel hollow
      if(first_end==3):
        hollow_A = []
        hollow_A.append((ox+hlm*math.cos(tooth_angle-pi_module_angle+ham), oy+hlm*math.sin(tooth_angle-pi_module_angle+ham), 0))
        hollow_A.append((ox+hl2*math.cos(tooth_angle-pi_module_angle+ha2), oy+hl2*math.sin(tooth_angle-pi_module_angle+ha2), hrbr))
        hollow_A.append((ox+hl1*math.cos(tooth_angle-pi_module_angle+ha2), oy+hl1*math.sin(tooth_angle-pi_module_angle+ha2), 0))
        hollow_B = cnc25d_api.cnc_cut_outline(hollow_A, "hollow")
        half_hollow = hollow_B[0:-1]
    # assembly
    r_final_outline.extend(half_hollow)
    r_final_outline.extend(start_of_profile_B)
  ### bulk of the gearwheel_portion
  for tooth in range(portion_tooth_nb):
    # first involute
    first_involute_B = involute_outline(ox, oy, i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_thickness, tooth_angle)
    # gearwheel hollow
    hollow_A = []
    hollow_A.append((ox+hl1*math.cos(tooth_angle+ha1), oy+hl1*math.sin(tooth_angle+ha1), 0))
    hollow_A.append((ox+hl2*math.cos(tooth_angle+ha1), oy+hl2*math.sin(tooth_angle+ha1), hrbr))
    hollow_A.append((ox+hl2*math.cos(tooth_angle+ha2), oy+hl2*math.sin(tooth_angle+ha2), hrbr))
    hollow_A.append((ox+hl1*math.cos(tooth_angle+ha2), oy+hl1*math.sin(tooth_angle+ha2), 0))
    hollow_B = cnc25d_api.cnc_cut_outline(hollow_A, "hollow")
    # second involute
    second_involute_B = involute_outline(ox, oy, i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_thickness, tooth_angle)
    # assembly
    r_final_outline.extend(first_involute_B)
    r_final_outline.extend(hollow_B[1:-1])
    r_final_outline.extend(second_involute_B)
    # prepare the next tooth
    tooth_angle += pi_module_angle
  ### end of bulk
  if(last_end>0):
    half_hollow = []
    end_of_profile_B = []
    if(first_end==1):
      end_of_profile_B = [(ox+tlm*math.cos(tooth_angle), oy+tlm*math.sin(tooth_angle))]
    else:
      end_of_profile_B = involute_outline(ox, oy, i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_thickness, tooth_angle)
      # gearwheel hollow
      if(first_end==3):
        hollow_A = []
        hollow_A.append((ox+hl1*math.cos(tooth_angle+ha1), oy+hl1*math.sin(tooth_angle+ha1), 0))
        hollow_A.append((ox+hl2*math.cos(tooth_angle+ha1), oy+hl2*math.sin(tooth_angle+ha1), hrbr))
        hollow_A.append((ox+hlm*math.cos(tooth_angle+ham), oy+hlm*math.sin(tooth_angle+ham), 0))
        hollow_B = cnc25d_api.cnc_cut_outline(hollow_A, "hollow")
        half_hollow = hollow_B[1:]
    # assembly
    r_final_outline.extend(end_of_profile_B)
    r_final_outline.extend(half_hollow)
  if(closed):
    r_final_outline.append(r_final_outline[0]) # closed the outline in case of full gearwheel
  #return
  return(r_final_outline)

def ideal_involute_tooth_outline(ai_low_parameters, ai_angle_position, ai_thickness_coeff):
  """ create the ideal tooth_profile over the first tooth of an intern or extern gearwheel
  """
  # precision
  #radian_epsilon=math.pi/1000 # unefficient because this function is used often
  radian_epsilon = gpo_radian_epsilon
  # get ai_low_parameters
  (gear_type, pi_module_angle,
    i1_base, i1_offset, i1_sign, i1u_nb, i1u_ini, i1u_inc, i1_thickness,
    i2_base, i2_offset, i2_sign, i2u_nb, i2u_ini, i2u_inc, i2_thickness,
    hl1, hl2, ha1, ha2, hrbr, hlm, ham, tlm,
    ox, oy, portion_tooth_nb, first_end, last_end, closed) = ai_low_parameters
  # precision
  ideal = 8 # additional_sampling_for_ideal_curve. it's a multiplicator
  # initialization
  tooth_angle = ai_angle_position
  # construct the ideal_tooth_outline over the first tooth
  # first_involute
  first_involute = []
  u = i2u_ini
  ideal_i2u_inc = float(i2u_inc)/ideal
  for sampling in range(ideal*i2u_nb+1):
    if(abs(u)<radian_epsilon): # for rounding error
      u=0
    (qx, qy, ti) = sample_of_gear_tooth_profile((ox,oy), i2_base, tooth_angle-pi_module_angle+i2_offset, i2_sign, ai_thickness_coeff*i2_thickness, u)
    first_involute.append((qx, qy))
    u += ideal_i2u_inc
  # second_involute
  second_involute = []
  u = i1u_ini
  ideal_i1u_inc = float(i1u_inc)/ideal
  for sampling in range(ideal*i1u_nb+1):
    if(abs(u)<radian_epsilon): # for rounding error
      u=0
    (qx, qy, ti) = sample_of_gear_tooth_profile((ox,oy), i1_base, tooth_angle+i1_offset, i1_sign, ai_thickness_coeff*i1_thickness, u)
    second_involute.append((qx, qy))
    u += ideal_i1u_inc
  # assembly
  r_ideal_tooth_outline = []
  r_ideal_tooth_outline.extend(first_involute)
  r_ideal_tooth_outline.extend(second_involute)
  #return
  return(r_ideal_tooth_outline)

def slope_outline(ai_ox, ai_oy, ai_bi, ai_offset, ai_slope_angle, ai_sign, ai_top_length, ai_bottom_length, ai_hollow_length, ai_thickness, ai_bottom_router_bit, ai_tooth_position):
  """ from subset of low-level parameter, generates a gearbear_tooth_slope format B outline
  """
  # precision
  #radian_epsilon=math.pi/1000 # unefficient because this function is used often
  radian_epsilon = gpo_radian_epsilon
  #
  slope_angle = ai_bi + ai_sign*ai_slope_angle
  thickness_angle = slope_angle - ai_sign*math.pi/2
  #top_height = ai_top_height/math.cos(ai_slope_angle)
  #bottom_height = ai_bottom_height/math.cos(ai_slope_angle)
  top_length = ai_top_length
  bottom_length = ai_bottom_length + ai_hollow_length + ai_thickness*math.tan(ai_slope_angle)
  #
  top_x = ai_ox + (ai_tooth_position+ai_offset)*math.cos(ai_bi-math.pi/2) + top_length*math.cos(slope_angle) + ai_thickness*math.cos(thickness_angle)
  top_y = ai_oy + (ai_tooth_position+ai_offset)*math.sin(ai_bi-math.pi/2) + top_length*math.sin(slope_angle) + ai_thickness*math.sin(thickness_angle)
  bottom_x = ai_ox + (ai_tooth_position+ai_offset)*math.cos(ai_bi-math.pi/2) - bottom_length*math.cos(slope_angle) + ai_thickness*math.cos(thickness_angle)
  bottom_y = ai_oy + (ai_tooth_position+ai_offset)*math.sin(ai_bi-math.pi/2) - bottom_length*math.sin(slope_angle) + ai_thickness*math.sin(thickness_angle)
  #
  if(ai_sign==1):
    r_slope_B = ((top_x, top_y, 0),(bottom_x, bottom_y, ai_bottom_router_bit))
  elif(ai_sign==-1):
    r_slope_B = ((bottom_x, bottom_y, ai_bottom_router_bit),(top_x, top_y, 0))
  # return
  return(r_slope_B)

def gearbar_profile_outline(ai_low_parameters, ai_tangential_position):
  """ create the outline of a gearbar definied by ai_low_parameters
      The reference of a gearbar is the middle of the middle tooth.
      ai_tangential_position sets the reference of the gearbar.
  """
  # get ai_low_parameters
  #(g_type, pi_module, g_ox, g_oy, g_bi, bar_tooth_nb, g_pfe, g_ple, g_sp, g_sn, g_ah, g_dh, g_hh, g_rbr, g_stp, g_stn, gb_p_offset, gb_n_offset) = ai_low_parameters
  (g_type, pi_module, g_ox, g_oy, g_bi, bar_tooth_nb, middle_tooth, g_pfe, g_ple, tlh, blh, blx,
    g_sp, g_sn, g_alp, g_dlp, g_hlp, g_aln, g_dln, g_hln, g_rbr, g_stp, g_stn, gb_p_offset, gb_n_offset) = ai_low_parameters
  # construct the final_outline
  r_final_outline = []
  cyclic_tangential_position = math.fmod(ai_tangential_position, middle_tooth*pi_module) # to avoid the gearbar move away from its gearwheel
  tangential_position = cyclic_tangential_position - middle_tooth*pi_module # the position reference is the middle of the middle tooth
  # start of the gearbar
  gearbar_A = []
  if(g_pfe==3): # start on hollow_middle
    hollow_middle_x = g_ox + (tangential_position-pi_module+blx)*math.cos(g_bi+math.pi/2) + blh*math.cos(g_bi+math.pi)
    hollow_middle_y = g_oy + (tangential_position-pi_module+blx)*math.sin(g_bi+math.pi/2) + blh*math.sin(g_bi+math.pi)
    gearbar_A.append((hollow_middle_x, hollow_middle_y, 0)) # hollow middle
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_n_offset, g_sn, -1, g_aln, g_dln, g_hln, g_stn, g_rbr, tangential_position)) # positive slope
  elif(g_pfe==2): # start on the positive slope
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_n_offset, g_sn, -1, g_aln, g_dln, g_hln, g_stn, 0, tangential_position)) # positive slope
  elif(g_pfe==1): # start on the top middle
    top_middle_x = g_ox + tangential_position*math.cos(g_bi+math.pi/2) + tlh*math.cos(g_bi)
    top_middle_y = g_oy + tangential_position*math.sin(g_bi+math.pi/2) + tlh*math.sin(g_bi)
    gearbar_A.append((top_middle_x, top_middle_y, 0)) # top middle
  if(gearbar_A!=[]):
    gearbar_B = cnc25d_api.cnc_cut_outline(gearbar_A, "start of gearbar")
    r_final_outline.extend(gearbar_B)
  # bulk of the gearbar
  for tooth in range(bar_tooth_nb):
    gearbar_A = []
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_p_offset, g_sp,  1, g_alp, g_dlp, g_hlp, g_stp, g_rbr, tangential_position)) # negative slope
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_n_offset, g_sn, -1, g_aln, g_dln, g_hln, g_stn, g_rbr, tangential_position+pi_module)) # positive slope
    #print("dbg745: gearbar_A:", gearbar_A)
    gearbar_B = cnc25d_api.cnc_cut_outline(gearbar_A, "bulk of gearbar")
    r_final_outline.extend(gearbar_B)
    # prepare the next tooth
    tangential_position += pi_module
  # end of the gearbar
  gearbar_A = []
  if(g_ple==3): # stop on hollow_middle
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_p_offset, g_sp,  1, g_alp, g_dlp, g_hlp, g_stp, g_rbr, tangential_position)) # negative slope
    hollow_middle_x = g_ox + (tangential_position+blx)*math.cos(g_bi+math.pi/2) + blh*math.cos(g_bi+math.pi)
    hollow_middle_y = g_oy + (tangential_position+blx)*math.sin(g_bi+math.pi/2) + blh*math.sin(g_bi+math.pi)
    gearbar_A.append((hollow_middle_x, hollow_middle_y, 0)) # hollow middle
  elif(g_ple==2): # stop on the negative slope
    gearbar_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_p_offset, g_sp,  1, g_alp, g_dlp, g_hlp, g_stp, 0, tangential_position)) # negative slope
  elif(g_ple==1): # stop on the top middle
    top_middle_x = g_ox + tangential_position*math.cos(g_bi+math.pi/2) + tlh*math.cos(g_bi)
    top_middle_y = g_oy + tangential_position*math.sin(g_bi+math.pi/2) + tlh*math.sin(g_bi)
    gearbar_A.append((top_middle_x, top_middle_y, 0)) # top middle
  if(gearbar_A!=[]):
    gearbar_B = cnc25d_api.cnc_cut_outline(gearbar_A, "end of gearbar")
    r_final_outline.extend(gearbar_B)
  #return
  return(r_final_outline)

def ideal_linear_tooth_outline(ai_low_parameters, ai_tangential_position, ai_thickness_coeff):
  """ create the ideal tooth_profile over the first tooth of a gearbar
  """
  # get ai_low_parameters
  (g_type, pi_module, g_ox, g_oy, g_bi, bar_tooth_nb, middle_tooth, g_pfe, g_ple, tlh, blh, blx,
    g_sp, g_sn, g_alp, g_dlp, g_hlp, g_aln, g_dln, g_hln, g_rbr, g_stp, g_stn, gb_p_offset, gb_n_offset) = ai_low_parameters
  cyclic_tangential_position = math.fmod(ai_tangential_position, middle_tooth*pi_module) # to avoid the gearbar move away from its gearwheel
  #tangential_position = cyclic_tangential_position - middle_tooth*pi_module # the position reference is the middle of the middle tooth
  tangential_position = cyclic_tangential_position
  # tooth
  tooth_A = []
  tooth_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_n_offset, g_sn, -1, g_aln, g_dln, 0, ai_thickness_coeff*g_stn, 0, tangential_position))
  tooth_A.extend(slope_outline(g_ox, g_oy, g_bi, gb_p_offset, g_sp,  1, g_alp, g_dlp, 0, ai_thickness_coeff*g_stp, 0, tangential_position))
  r_ideal_tooth_outline_B = cnc25d_api.cnc_cut_outline(tooth_A, "bulk of gearbar")
  #return
  return(r_ideal_tooth_outline_B)

def gear_profile_outline(ai_low_parameters, ai_angle_position):
  """ create the format B outline of a gear definied by ai_low_parameters
      ai_angle_position sets the gear position.
  """
  r_gear_profile_outline_B = []
  g_type = ai_low_parameters[0]
  if((g_type=='e')or(g_type=='i')):
    r_gear_profile_outline_B = gearwheel_profile_outline(ai_low_parameters, ai_angle_position)
  elif(g_type=='l'):
    r_gear_profile_outline_B = gearbar_profile_outline(ai_low_parameters, ai_angle_position)
  #return
  return(r_gear_profile_outline_B)

def ideal_tooth_outline(ai_low_parameters, ai_angle_position, ai_thickness_coeff):
  """ create the ideal tooth_profile over the first tooth of a gear (i, e or l)
  """
  r_ideal_tooth_outline = []
  g_type = ai_low_parameters[0]
  if((g_type=='e')or(g_type=='i')):
    r_ideal_tooth_outline = ideal_involute_tooth_outline(ai_low_parameters, ai_angle_position, ai_thickness_coeff)
  elif(g_type=='l'):
    r_ideal_tooth_outline = ideal_linear_tooth_outline(ai_low_parameters, ai_angle_position, ai_thickness_coeff)
  #return
  return(r_ideal_tooth_outline)

#############################################################################
# positioning help-function
#############################################################################

def calc_real_force_angle(ai_g1_type, ai_g1_pr, ai_g1_br, ai_g2_type, ai_g2_pr, ai_g2_br, ai_aal, ai_g1_sa, ai_g2_sa):
  """ calculate the real_force_angle depending also on the additional inter-axis length
  """
  if((ai_g1_type=='e')and(ai_g2_type=='e')):# depending on gear_type
    r_real_force_angle = math.acos(float(ai_g1_br+ai_g2_br)/(ai_g1_pr+ai_g2_pr+ai_aal))
  elif((ai_g1_type=='i')and(ai_g2_type=='e')): # i-e
    if(ai_g2_pr>ai_g1_pr):
      print("ERR546: Error, the gearring radius {:0.3f} must be bigger gearwheel radius {:0.3f}".format(ai_g1_pr, ai_g2_pr))
      sys.exit(2)
    r_real_force_angle = math.acos(float(ai_g1_br-ai_g2_br)/(ai_g1_pr-(ai_g2_pr+ai_aal)))
  elif((ai_g1_type=='e')and(ai_g2_type=='i')): # e-i
    if(ai_g1_pr>ai_g2_pr):
      print("ERR547: Error, the gearring radius {:0.3f} must be bigger gearwheel radius {:0.3f}".format(ai_g2_pr, ai_g1_pr))
      sys.exit(2)
    r_real_force_angle = math.acos(float(ai_g2_br-ai_g1_br)/(ai_g2_pr-(ai_g1_pr+ai_aal)))
  elif((ai_g1_type=='l')and(ai_g2_type=='e')): # l-e
    r_real_force_angle = ai_g1_sa
  elif((ai_g1_type=='e')and(ai_g2_type=='l')): # e-l
    r_real_force_angle = ai_g2_sa
  else:
    print("ERR221: Error, the gear type combination {:s}-{:s} does not exist!".format(ai_g1_type, ai_g2_type))
    sys.exit(2)
  return(r_real_force_angle)

#############################################################################
# positioning
#############################################################################

def tmp_f(ai_param, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale):
  # get the hight level parameters
  g_type  = ai_param['gear_type']
  g_n     = ai_param['full_tooth_nb']
  g_m     = ai_param['module']
  g_pr    = ai_param['primitive_radius']
  g_adp   = ai_param['addendum_dedendum_parity']
  g_thh   = ai_param['tooth_half_height']
  g_ar    = ai_param['addendum_radius']
  g_dr    = ai_param['dedendum_radius']
  g_brp   = ai_param['positive_base_radius']
  g_brn   = ai_param['negative_base_radius']
  g_ox    = ai_param['center_ox']
  g_oy    = ai_param['center_oy']
  g_rbr   = ai_param['gear_router_bit_radius']
  g_hr    = ai_param['hollow_radius']
  g_irp   = ai_param['positive_involute_resolution']
  g_irn   = ai_param['negative_involute_resolution']
  g_stp   = ai_param['positive_skin_thickness']
  g_stn   = ai_param['negative_skin_thickness']
  g_ptn   = ai_param['portion_tooth_nb']
  g_pfe   = ai_param['portion_first_end']
  g_ple   = ai_param['portion_last_end']
  g_bi    = ai_param['gearbar_inclination']
  g_sp    = ai_param['positive_slope_angle']
  g_sn    = ai_param['negative_slope_angle']
  g_ah    = ai_param['addendum_height']
  g_dh    = ai_param['dedendum_height']
  g_hh    = ai_param['hollow_height']
  g_ks    = ai_param['gear_sign']
  g_pc    = ai_param['position_coefficient']
  # precision
  #radian_epsilon = math.pi/1000
  r_low_parameters = ()
  if((g_type=='e')or(g_type=='i')):
    pi_module_angle             = ai_param['pi_module_angle']
    top_land                    = ai_param['top_land']
    bottom_land                 = ai_param['bottom_land']
    addendum_positive_involute  = ai_param['addendum_positive_involute']
    addendum_negative_involute  = ai_param['addendum_negative_involute']
    dedendum_positive_involute  = ai_param['dedendum_positive_involute']
    dedendum_negative_involute  = ai_param['dedendum_negative_involute']
    ipaa                        = ai_param['low_positive_addendum_angle']
    inaa                        = ai_param['low_negative_addendum_angle']
    if(g_type=='e'): # negative > hollow > positive
      # low1: to create the gear-profile outline
      i1_base = g_brn
      i2_base = g_brp
      # low2: to calculate g2_position
      #i1_primitive_offset = top_land/2-inpa #>0
      #i2_primitive_offset = -1*(top_land/2+ippa) #<0
      i1_primitive_offset = top_land/2+addendum_negative_involute #>0
      i2_primitive_offset = -1*(top_land/2+addendum_positive_involute) #<0
      i1_offset2 = top_land/2-inaa # >0
      i2_offset2 = -1*(top_land/2+ipaa) # <0
      driven_ip_base = g_brp
      driven_ip_offset = i2_offset2
      driven_in_base = g_brn
      driven_in_offset = i1_offset2
    elif(g_type=='i'): # positive > hollow > negative
      # low1
      i1_base = g_brp
      i2_base = g_brn
      # low2
      # gearring with positive rotation, push with positive involute
      i1_primitive_offset = top_land/2+addendum_positive_involute #>0
      i2_primitive_offset = -1*(top_land/2+addendum_negative_involute) #<0
      i1_offset2 = top_land/2-ipaa
      i2_offset2 = -1*top_land/2-inaa
      driven_ip_base = g_brp
      driven_ip_offset = i1_offset2
      driven_in_base = g_brn
      driven_in_offset = i2_offset2
      #print("dbg663: ipaa {:0.3f}".format(ipaa))
    #
    # return
    place_low_parameters = (g_type, pi_module_angle, g_n, g_pr, g_ox, g_oy, g_ks, g_pc, g_bi,
      i1_base, i1_primitive_offset, i1_offset2,
      i2_base, i2_primitive_offset, i2_offset2,
      driven_ip_base, driven_ip_offset, driven_in_base, driven_in_offset)
  elif(g_type=='l'):
    # linear gear make low parameters
    pi_module         = ai_param['pi_module']
    top_land          = ai_param['top_land']
    bottom_land       = ai_param['bottom_land']
    positive_addendum = ai_param['addendum_positive_slope']
    negative_addendum = ai_param['addendum_negative_slope']
    positive_dedendum = ai_param['dedendum_positive_slope']
    negative_dedendum = ai_param['dedendum_negative_slope']
    # linear gear place low parameters
    i1_base = g_sn
    i1_primitive_offset = -1*(top_land/2+negative_addendum)
    i1_offset2 = -1*(top_land/2+negative_addendum+negative_dedendum)
    i2_base = g_sp
    i2_primitive_offset = top_land/2+positive_addendum
    i2_offset2 = top_land/2+positive_addendum+positive_dedendum
    driven_ip_base = g_sp
    driven_ip_offset = i2_primitive_offset
    driven_in_base = g_sn
    driven_in_offset = i1_primitive_offset
    # return
    place_low_parameters = (g_type, pi_module, g_n, g_pr, g_ox, g_oy, g_ks, g_pc, g_bi,
      i1_base, i1_primitive_offset, i1_offset2,
      i2_base, i2_primitive_offset, i2_offset2,
      driven_ip_base, driven_ip_offset, driven_in_base, driven_in_offset)
  #return
  r_low_parameters = place_low_parameters
  return(r_low_parameters)


def pre_g2_position_calculation(ai_g1_param, ai_g2_param, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale):
  """ Initial calcultation for getting the g2_position from the high-level parameters of g1 anf g2.
      The goal of this function is to speed-up the function g2_position_calcultion by factoring some of the processing
  """
  # place_low_parameters
  g1_place_low_parameters = tmp_f(ai_g1_param, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale)
  g2_place_low_parameters = tmp_f(ai_g2_param, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale)
  # info_txt
  info_txt = ""
  # return
  place_low_parameters = (g1_place_low_parameters, g2_place_low_parameters, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale)
  r_ppc = (place_low_parameters, info_txt)
  return(r_ppc)

#def g2_position_calculation(ai_g1_param, ai_g2_param, ai_rotation_direction, ai_g1_position, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale):
def g2_position_calculation(ai_place_low_param, ai_rotation_direction, ai_g1_position):
  """ calculation of the angle position of the second gear and other related parameters (speed, friction)
  """
  #((g1_place_low_parameters, g2_place_low_parameters), tmp_info) = pre_g2_position_calculation(ai_g1_param, ai_g2_param, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale)
  (g1_place_low_parameters, g2_place_low_parameters, ai_aal, ai_g1g2_a, ai_g1_rotation_speed, ai_speed_scale) = ai_place_low_param
  # get ai_g1_low_parameters
  (g1_gear_type, g1_pi_module_angle, g1_n, g1_pr, g1_ox, g1_oy, g1_ks, g1_pc, g1_bi,
    g1_i1_base, g1_i1_primitive_offset, g1_i1_offset2,
    g1_i2_base, g1_i2_primitive_offset, g1_i2_offset2,
    g1_driven_ip_base, g1_driven_ip_offset, g1_driven_in_base, g1_driven_in_offset) = g1_place_low_parameters
  # get ai_g2_low_parameters
  (g2_gear_type, g2_pi_module_angle, g2_n, g2_pr, g2_ox, g2_oy, g2_ks, g2_pc, g2_bi,
    g2_i1_base, g2_i1_primitive_offset, g2_i1_offset2,
    g2_i2_base, g2_i2_primitive_offset, g2_i2_offset2,
    g2_driven_ip_base, g2_driven_ip_offset, g2_driven_in_base, g2_driven_in_offset) = g2_place_low_parameters
  # precision
  #radian_epsilon = math.pi/1000
  radian_epsilon = gpo_radian_epsilon
  # select parameter depending on ai_rotation_direction
  if(ai_rotation_direction==1): # rotation_direction positive (g1 driving, g2 driven) : g1_negative_involute with g2_negative_involute
    g1_primitive_offset = g1_i1_primitive_offset
    g1_br = g1_i1_base
    g1_involute_offset = g1_i1_offset2
    g1_sa = g1_i1_base
  else:
    g1_primitive_offset = g1_i2_primitive_offset
    g1_br = g1_i2_base
    g1_involute_offset = g1_i2_offset2
    g1_sa = g1_i2_base
  # g2 parameter depend on g1_ks and rotation_direction
  if(ai_rotation_direction*g1_ks==1):
    g2_br = g2_driven_in_base
    g2_involute_offset = g2_driven_in_offset
    g2_sa = g2_driven_in_base
  else:
    g2_br = g2_driven_ip_base
    g2_involute_offset = g2_driven_ip_offset
    g2_sa = g2_driven_ip_base
  ## gear system related
  # real_force_angle
  real_force_angle = calc_real_force_angle(g1_gear_type, g1_pr, g1_br, g2_gear_type, g2_pr, g2_br, ai_aal, g1_sa, g2_sa)
  #print("dbg743: real_force_angle:", real_force_angle)
  #AB = g1_pr+g2_pr+ai_aal
  AB = abs(g1_ks*g1_pc*g1_pr+g2_ks*g2_pc*g2_pr+ai_aal)
  # alternative for AB
  AB2 = math.sqrt((g2_ox-g1_ox)**2+(g2_oy-g1_oy)**2)
  if(abs(AB2-AB)>radian_epsilon):
    print("ERR314: Error with the calculation of AB {:0.3f} or {:0.3f}".format(AB, AB2))
    sys.exit(2)
  ## g1 related
  if((g1_gear_type=='e')or(g1_gear_type=='i')):
    # get the angle of the closest middle of addendum to the contact point
    aa = ai_g1_position + g1_primitive_offset - ai_g1g2_a
    while(abs(aa)>g1_pi_module_angle/2+radian_epsilon):
      if(aa>0):
        aa = aa - g1_pi_module_angle
      else:
        aa = aa + g1_pi_module_angle
    contact_g1_tooth_angle = aa - g1_primitive_offset + ai_g1g2_a
    contact_g1_tooth_relative_angle = aa - g1_primitive_offset # relative to the inter-axis
    # g1_involute_offset_angle (see the documentation for the exact definition)
    #g1_involute_offset_angle = contact_g1_tooth_relative_angle + g1_involute_offset
    # g1_contact_u : involute parameter for g1 of the contact point
    #g1_contact_u = real_force_angle + ai_rotation_direction*g1_involute_offset_angle
    g1_contact_u = real_force_angle + ai_rotation_direction * g1_ks * (contact_g1_tooth_relative_angle + g1_involute_offset)
    #print("dbg558: g1_involute_offset {:0.3f}  contact_g1_tooth_relative_angle {:0.3f}  real_force_angle {:0.3f}".format(g1_involute_offset, contact_g1_tooth_relative_angle, g1_involute_offset))
    # contact point coordinates (method 1)
    (cx, cy, ti) = sample_of_gear_tooth_profile((g1_ox, g1_oy), g1_br, contact_g1_tooth_angle+g1_involute_offset, -1*g1_ks*ai_rotation_direction, 0, g1_contact_u)
    #print("dbg858: contact point (method1): cx: {:0.2f}  cy: {:0.2f}  ti: {:0.2f}".format(cx, cy, ti))
  elif(g1_gear_type=='l'): # linear-gear (aka gearbar)
    # some geometry
    KD = g2_br*math.tan(g1_sa)
    AD = g2_br/math.cos(g1_sa)
    BD = AB-AD
    DE = BD/math.sin(g1_sa)
    KE = KD+DE
    BE = BD/math.tan(g1_sa)
    if(BD<0):
      print("ERR853: Error, BD {:0.3f} is negative".format(BD))
      sys.exit(2)
    # contact_g1_tooth_position
    aa = ai_g1_position + g1_primitive_offset
    while(abs(aa)>g1_pi_module_angle/2+radian_epsilon):
      if(aa>0):
        aa = aa - g1_pi_module_angle
      else:
        aa = aa + g1_pi_module_angle
    contact_g1_tooth_position = aa - g1_primitive_offset
    g1_contact_u = (contact_g1_tooth_position-ai_rotation_direction*BE)*math.cos(g1_sa)
    g1_position2 = ai_rotation_direction*BE + g1_contact_u/math.cos(g2_sa) - g1_involute_offset
    dc = (g1_position2+g1_involute_offset-ai_rotation_direction*BE)*math.cos(g1_sa)
    cx = g1_ox + ai_rotation_direction*BE*math.cos(g1_bi-math.pi/2) + dc*math.cos(g1_bi-math.pi/2-ai_rotation_direction*g1_sa)
    cy = g1_oy + ai_rotation_direction*BE*math.sin(g1_bi-math.pi/2) + dc*math.sin(g1_bi-math.pi/2-ai_rotation_direction*g1_sa)
    #print("dbg989: g2_position {:0.3f}   dc {:0.3f}".format(g2_position, dc))
    # ti
    ti = g1_sa
  ## triangle ABC
  # length of AC
  AC = math.sqrt((cx-g1_ox)**2+(cy-g1_oy)**2)
  # length of BC
  BC = math.sqrt((cx-g2_ox)**2+(cy-g2_oy)**2)
  # angle CBA
  if(AC+BC==AB):
  #if(abs(AC+BC-AB)<radian_epsilon):
    print("WARN468: Warning, the triangle ABC is flat")
    BAC = 0
    ABC = 0
  elif(AC+BC<AB):
    print("ERR478: Error of length in the triangle ABC")
    sys.exit(20)
  else:
    # law of cosinus (Al-Kashi) in ABC
    BAC = math.acos(float(AB**2+AC**2-BC**2)/(2*AB*AC))
    ABC = math.acos(float(AB**2+BC**2-AC**2)/(2*AB*BC))
    #print("dbg569: BAC {:0.3f}   ABC {:0.3f}".format(BAC, ABC))
    BAC = math.fmod(BAC+5*math.pi/2, math.pi)-math.pi/2
    ABC = math.fmod(ABC+5*math.pi/2, math.pi)-math.pi/2
    # alternative
    xAB = math.atan2(g2_oy-g1_oy, g2_ox-g1_ox)
    xAC = math.atan2(cy-g1_oy, cx-g1_ox)
    #BAC2 = math.fmod(xAC-xAB+5*math.pi, 2*math.pi)-math.pi
    BAC2 = math.fmod(xAC-xAB+9*math.pi/2, math.pi)-math.pi/2
    xBA = math.atan2(g1_oy-g2_oy, g1_ox-g2_ox)
    xBC = math.atan2(cy-g2_oy, cx-g2_ox)
    #ABC2 = math.fmod(xBC-xBA+5*math.pi, 2*math.pi)-math.pi
    ABC2 = math.fmod(xBC-xBA+9*math.pi/2, math.pi)-math.pi/2
    #print("dbg557: xBA {:0.3f}  xBC {:0.3f}".format(xBA, xBC))
    # sign BAC, ABC
    BAC = math.copysign(BAC, BAC2)
#    ABC = -1*g1_ks*g2_ks* math.copysign(ABC, BAC2)
    ABC = ABC2
    # check BAC and BAC2
    if(abs(BAC2-BAC)>radian_epsilon):
      print("ERR689: Error in the calculation of BAC {:0.3f} or BAC2 {:0.3f} !".format(BAC, BAC2))
      sys.exit(2)
    # check ABC and ABC2
    if(abs(ABC2-ABC)>radian_epsilon):
      print("ERR688: Error in the calculation of ABC {:0.3f} or ABC2 {:0.3f} !".format(ABC, ABC2))
      sys.exit(2)
  #print("dbg334: BAC: {:0.3f}".format(BAC))
  #print("dbg335: ABC: {:0.3f}".format(ABC))
  ## speed / radial angle
  g1_sra = ai_rotation_direction*g1_ks*real_force_angle+BAC
  # alternative
  if((g1_gear_type=='e')or(g1_gear_type=='i')):
    g1_sra2 = ai_rotation_direction*g1_ks*math.atan(g1_contact_u)
    if(abs(g1_sra2-g1_sra)>radian_epsilon):
      print("ERR414: Error in calculation of g1_sra {:0.3f} or g1_sra2 {:0.3f}".format(g1_sra, g1_sra2))
      sys.exit(2)
  ## speed of c1 (contact point of g1)
  # c1 speed
  if((g1_gear_type=='e')or(g1_gear_type=='i')):
    c1_speed = AC*ai_g1_rotation_speed
    c1_speed_radial = c1_speed*math.cos(g1_sra)
    c1_speed_tangential = c1_speed*math.sin(g1_sra)
  elif(g1_gear_type=='l'): # linear-gear (aka gearbar)
    c1_speed = ai_g1_rotation_speed * g1_pi_module_angle * 5
    c1_speed_radial = c1_speed*math.cos(g1_sa)
    c1_speed_tangential = c1_speed*math.sin(g1_sa)
  ### g2_position, g2_contact_u, c2x, c2y, c2_speed_radial, c2_speed, c2_speed_tangential, g2_rotation_speed
  if((g2_gear_type=='e')or(g2_gear_type=='i')):
    ## g2_contact_u : involute parameter for g2 of the contact point
    # several mathods:
    g2_sra = ai_rotation_direction*g1_ks*real_force_angle+ABC
    # length KL (see documentation  graphic gear_position.svg)
    #KL = math.sqrt(AB**2 - (g1_br*(1+float(g2_n)/g1_n))**2) # kind of pythagor
    #KL = math.sqrt(AB**2 - (g1_br+g2_br)**2) # kind of pythagor
    KL = math.sin(real_force_angle)*AB
    #print("dbg631: KL {:0.5f}".format(KL))
    #g2_contact_u1 = float(KL - g1_contact_u*g1_br)/g2_br
    g2_contact_u1 = g1_ks*float(KL - g2_ks*g1_contact_u*g1_br)/g2_br
    if((g1_gear_type=='e')or(g1_gear_type=='i')):
      g2_contact_u2 = math.tan(abs(g2_sra))
      g2_contact_u3 = math.sqrt((float(BC)/g2_br)**2-1)
      if(abs(g2_contact_u2-g2_contact_u1)>radian_epsilon):
        print("ERR331: Error in the calculation of g2_contact_u1 {:0.3f} or g2_contact_u2 {:0.3f}".format(g2_contact_u1, g2_contact_u2))
        sys.exit(2)
      if(abs(g2_contact_u3-g2_contact_u1)>radian_epsilon):
        print("ERR332: Error in the calculation of g2_contact_u1 {:0.3f} or g2_contact_u3 {:0.3f}".format(g2_contact_u1, g2_contact_u3))
        sys.exit(2)
    g2_contact_u = g2_contact_u1 # select the method for g2_contact_u
    ## c2_position
    #g2_position = ai_g1g2_a + math.pi - ai_rotation_direction*(real_force_angle - g2_contact_u) - g2_involute_offset
    g2_position = ai_g1g2_a + (1+g1_ks*g2_ks)/2*math.pi - ai_rotation_direction*g1_ks*(real_force_angle - g2_contact_u) - g2_involute_offset
    # c2 coordinates
    (c2x, c2y, t2i) = sample_of_gear_tooth_profile((g2_ox, g2_oy), g2_br, g2_position+g2_involute_offset, -1*ai_rotation_direction*g1_ks, 0, g2_contact_u)
    if(abs(math.fmod(ti-t2i, math.pi/2))>radian_epsilon):
      print("ERR874: Error, the tangents ti {:0.3f} and ti2 {:0.3f} are not equal (modulo pi)".format(ti, t2i))
      #sys.exit(2)
    #print("dbg632: g2_ox {:0.3f}  g2_oy {:0.3f}  g2_br {:0.3f}".format(g2_ox, g2_oy, g2_br))
    ## speed of c2 (contact point of g2)
    c2_speed_radial = c1_speed_radial
    c2_speed = float(c2_speed_radial)/math.cos(g2_sra)
    c2_speed_tangential = c2_speed*math.sin(g2_sra)
    # alternative
    c2_speed_tangential2 = ai_rotation_direction*g1_ks*c2_speed_radial*g2_contact_u
    if(abs(c2_speed_tangential2-c2_speed_tangential)>radian_epsilon):
      print("ERR336: Error in the calculation of c2_speed_tangential {:0.3f} or c2_speed_tangential2 {:0.3f}".format(c2_speed_tangential, c2_speed_tangential2))
      #sys.exit(2)
    g2_rotation_speed = float(c2_speed)/BC
  elif(g2_gear_type=='l'): # linear-gear (aka gearbar)
    KD = g1_br*math.tan(g2_sa)
    AD = g1_br/math.cos(g2_sa)
    BD = AB-AD
    DE = BD/math.sin(g2_sa)
    KE = KD+DE
    BE = BD/math.tan(g2_sa)
    #if(BD<0):
    #  print("ERR852: Error, BD {:0.3f} is negative".format(BD))
    #  sys.exit(2)
    g2_contact_u = ai_rotation_direction*(g1_contact_u*g1_br-KE)
    g2_position = ai_rotation_direction*BE + g2_contact_u/math.cos(g2_sa) - g2_involute_offset
    dc = (g2_position+g2_involute_offset-ai_rotation_direction*BE)*math.cos(g2_sa)
    c2x = g2_ox + ai_rotation_direction*BE*math.cos(g2_bi-math.pi/2) + dc*math.cos(g2_bi-math.pi/2-ai_rotation_direction*g2_sa)
    c2y = g2_oy + ai_rotation_direction*BE*math.sin(g2_bi-math.pi/2) + dc*math.sin(g2_bi-math.pi/2-ai_rotation_direction*g2_sa)
    #print("dbg989: g2_position {:0.3f}   dc {:0.3f}".format(g2_position, dc))
    if(abs(math.fmod(ti - (-1*ai_rotation_direction*g2_sa), math.pi/2))>radian_epsilon):
      print("ERR875: Error, the tangents ti {:0.3f} and slope g2_sa {:0.3f} are not equal (modulo pi)".format(ti, g2_sa))
      sys.exit(2)
    c2_speed_radial = c1_speed_radial
    c2_speed = float(c2_speed_radial)/math.cos(g2_sa)
    c2_speed_tangential = ai_rotation_direction*c2_speed*math.sin(g2_sa)
    g2_rotation_speed = c2_speed
  # friction between g1 and g2
  tangential_friction = c2_speed_tangential - c1_speed_tangential
  ## speed outline
  # scale the outline
  scaled_c1_speed_radial = c1_speed_radial*ai_speed_scale # *g1_module *g1_pr ???
  scaled_c1_speed_tangential = c1_speed_tangential*ai_speed_scale
  scaled_c2_speed_radial = c2_speed_radial*ai_speed_scale # *g2_module *g2_pr ???
  scaled_c2_speed_tangential = c2_speed_tangential*ai_speed_scale
  # normal-tangential reference frame
  nxa = ti+ai_rotation_direction*math.pi/2
  txa = nxa+math.pi/2
  #
  c1rx = cx+scaled_c1_speed_radial*math.cos(nxa)
  c1ry = cy+scaled_c1_speed_radial*math.sin(nxa)
  c1_speed_outline = ((cx, cy), # contact point
    (c1rx, c1ry), # c1 radial speed
    (c1rx+scaled_c1_speed_tangential*math.cos(txa), c1ry+scaled_c1_speed_tangential*math.sin(txa)), # c1 tangential speed
    (cx, cy)) # close
  c2rx = c2x+scaled_c2_speed_radial*math.cos(nxa)
  c2ry = c2y+scaled_c2_speed_radial*math.sin(nxa)
  c2_speed_outline = ((c2x, c2y),
    (c2rx, c2ry), # c2 radial speed
    (c2rx+scaled_c2_speed_tangential*math.cos(txa), c2ry+scaled_c2_speed_tangential*math.sin(txa)), # c2 tangential speed
    (c2x, c2y)) # close
  # return
  r_position = (g2_position, g2_rotation_speed, tangential_friction, c1_speed_outline, c2_speed_outline)
  return(r_position)

#############################################################################
# analytic calculation of the real_force_angle
#############################################################################

def info_on_real_force_angle(ai_g1_param, ai_g2_param, ai_sys_param, ai_rotation_direction):
  """ Analytic calculation to check the real_force_angle (including the additional_inter_axis_length) and the force_path_length
  """
  ### positive_rotation
  # external / external : negative_involute / negative_involute
  # external / internal : negative_involute / negative_involute
  # internal / external : positive_involute / positive_involute # exception !
  # external / linear   : negative_involute / negative_involute
  # linear   / external : negative_involute / negative_involute
  if(ai_rotation_direction==1):
    rotation_name = 'Positive'
  elif(ai_rotation_direction==-1):
    rotation_name = 'Negative'
  else:
    print("ERR663: Error, ai_rotation_direction {:d} can only be 1 or -1!".format(ai_rotation_direction))
    sys.exit(2)
  # get the interesting high-level parameters
  rd = ai_rotation_direction
  g1_type = ai_g1_param['gear_type']
  g1_sign = ai_g1_param['gear_sign']
  g1_n    = ai_g1_param['full_tooth_nb']
  g1_pr   = ai_g1_param['primitive_radius']
  g1_ar   = ai_g1_param['addendum_radius']
  g1_ah   = ai_g1_param['addendum_height']
  g1_bl   = ai_g1_param['gearbar_length']
  g1_ox   = ai_g1_param['center_ox']
  g1_oy   = ai_g1_param['center_oy']
  g2_type = ai_g2_param['gear_type']
  g2_sign = ai_g2_param['gear_sign']
  g2_n    = ai_g2_param['full_tooth_nb']
  g2_pr   = ai_g2_param['primitive_radius']
  g2_ar   = ai_g2_param['addendum_radius']
  g2_ah   = ai_g2_param['addendum_height']
  g2_bl   = ai_g2_param['gearbar_length']
  g2_ox   = ai_g2_param['center_ox']
  g2_oy   = ai_g2_param['center_oy']
  g1g2_a  = ai_sys_param['g1g2_angle']
  aal     = ai_sys_param['additional_inter_axis_length']
  if(rd*g1_sign==1):
    involute_name = 'Negative'
    g1_br = ai_g1_param['negative_base_radius']
    g2_br = ai_g2_param['negative_base_radius']
    g1_sa = ai_g1_param['negative_slope_angle']
    g2_sa = ai_g2_param['negative_slope_angle']
  else:
    involute_name = 'Positive'
    g1_br = ai_g1_param['positive_base_radius']
    g2_br = ai_g2_param['positive_base_radius']
    g1_sa = ai_g1_param['positive_slope_angle']
    g2_sa = ai_g2_param['positive_slope_angle']
  # start creating the info text
  r_info = ""
  #r_info += "Info on Real Force Angle {:s}:\n".format(rotation_name)
  #print("dbg311: ai_g1_br:", ai_g1_br)
  # depending on gear_type
  #real_force_angle = math.acos(float(ai_g1_br*(ai_g1_n+ai_g2_n))/((ai_g1_pr+ai_g2_pr+ai_aal)*ai_g1_n))
  real_force_angle = calc_real_force_angle(g1_type, g1_pr, g1_br, g2_type, g2_pr, g2_br, aal, g1_sa, g2_sa)
  #r_info += "{:s} Real Force Angle = {:0.2f} radian ({:0.2f} degree)\n".format(rotation_name, real_force_angle, real_force_angle*180/math.pi)
  # coordinate of C (intersection of axis-line and force-line)
  #AC = float((ai_g1_pr+ai_g2_pr+ai_aal)*ai_g1_n)/(ai_g1_n+ai_g2_n)
  AC = g1_br/math.cos(real_force_angle)
  CX = g1_ox + math.cos(g1g2_a)*AC
  CY = g1_oy + math.sin(g1g2_a)*AC
  # force line equation
  real_force_inclination = g1g2_a + rd*(math.pi/2 - real_force_angle) # angle (Ox, force)
  Flx = math.sin(real_force_inclination)
  Fly = -1*math.cos(real_force_inclination)
  Fk = -1*(Flx*CX+Fly*CY)
  # F2: intersection of the force line and the addendum_circle_1
  if((g1_type=='e')or(g1_type=='i')):
    S2X = CX + g1_pr/g1_n*math.cos(g1g2_a+rd*math.pi/2) # S2: define the side of the intersection line-circle
    S2Y = CY + g1_pr/g1_n*math.sin(g1g2_a+rd*math.pi/2)
    (F2X,F2Y, line_circle_intersection_status) = small_geometry.line_circle_intersection((Flx, Fly, Fk), (g1_ox, g1_oy), g1_ar, (S2X,S2Y), real_force_inclination, "F2 calcultation")
    if(line_circle_intersection_status==2):
      print("ERR125: Error with the intersection of the force line and the addendum_circle_1")
      sys.exit(2)
  elif(g1_type=='l'):
    LX = g1_ox+g1_ah*math.cos(g1g2_a)
    LY = g1_oy+g1_ah*math.sin(g1g2_a)
    Blx = math.sin(g1g2_a+math.pi/2)
    Bly = -1*math.cos(g1g2_a+math.pi/2)
    Bk = -1*(Blx*LX+Bly*LY)
    (F2X, F2Y, line_line_intersection_status) = small_geometry.line_line_intersection((Flx, Fly, Fk), (Blx, Bly, Bk), "F2 calcultation with gearbar")
    if(line_line_intersection_status==2):
      print("ERR127: Error with the intersection of the force line and the gearbar addendum line")
      sys.exit(2)
  # F1: intersection of the force line and the addendum_circle_2
  if((g2_type=='e')or(g2_type=='i')):
    S1X = CX + g2_pr/g2_n*math.cos(g1g2_a-rd*math.pi/2) # S1: define the side of the intersection line-circle
    S1Y = CY + g2_pr/g2_n*math.sin(g1g2_a-rd*math.pi/2)
    (F1X,F1Y, line_circle_intersection_status) = small_geometry.line_circle_intersection((Flx, Fly, Fk), (g2_ox, g2_oy), g2_ar, (S1X,S1Y), real_force_inclination+math.pi, "F1 calcultation")
    if(line_circle_intersection_status==2):
      print("ERR126: Error with the intersection of the force line and the addendum_circle_2")
      sys.exit(2)
  elif(g2_type=='l'):
    LX = g2_ox+g1_ah*math.cos(g1g2_a+math.pi)
    LY = g2_oy+g1_ah*math.sin(g1g2_a+math.pi)
    Blx = math.sin(g1g2_a+math.pi/2)
    Bly = -1*math.cos(g1g2_a+math.pi/2)
    Bk = -1*(Blx*LX+Bly*LY)
    (F1X, F1Y, line_line_intersection_status) = small_geometry.line_line_intersection((Flx, Fly, Fk), (Blx, Bly, Bk), "F1 calcultation with gearbar")
    if(line_line_intersection_status==2):
      print("ERR129: Error with the intersection of the force line and the gearbar addendum line")
      sys.exit(2)
  ### action_line_outline
  r_action_line_outline = ((F1X, F1Y), (F2X, F2Y))
  # length of F1F2
  F1F2 = math.sqrt((F2X-F1X)**2+(F2Y-F1Y)**2)
  #r_info += "length of the tooth {:s} contact path: {:0.2f}\n".format(involute_name, F1F2)
  r_info += "{:s} rotation, {:s}-{:s} involute {:s}. Real Force Angle = {:0.2f} radian ({:0.2f} degree). Contact path length: {:0.2f}\n".format(rotation_name, g1_type, g2_type, involute_name, real_force_angle, real_force_angle*180/math.pi, F1F2)
  # angle (F1AF2)
  if((g1_type=='e')or(g1_type=='i')):
    AF1 = float(math.sqrt((F1X-g1_ox)**2+(F1Y-g1_oy)**2))
    xAF1 = math.atan2((F1Y-g1_oy)/AF1, (F1X-g1_ox)/AF1)
    AF2 = float(g1_ar)
    xAF2 = math.atan2((F2Y-g1_oy)/AF2, (F2X-g1_ox)/AF2)
    F1AF2 = abs(math.fmod(xAF2-xAF1+5*math.pi, 2*math.pi)-math.pi)
    F1AF2p = F1AF2*g1_n/(2*math.pi)
    r_info += "tooth {:s} contact path angle from gearwheel1: {:0.2f} radian ({:0.2f} degree) {:0.2f}% of tooth length\n".format(involute_name, F1AF2, F1AF2*180/math.pi, F1AF2p*100)
  elif(g1_type=='l'):
    F1F2t = F1F2*math.cos(g1_sa)
    F1F2p = float(F1F2t)*g1_n/g1_bl
    r_info += "tooth {:s} contact path from gearbar1 tangential length {:0.2f} (mm) {:0.2f}% of tooth length\n".format(involute_name, F1F2t, F1F2p*100)
  # angle (F1EF2)
  if((g2_type=='e')or(g2_type=='i')):
    EF2 = float(math.sqrt((F2X-g2_ox)**2+(F2Y-g2_oy)**2))
    xEF2 = math.atan2((F2Y-g2_oy)/EF2, (F2X-g2_ox)/EF2)
    EF1 = float(g2_ar)
    xEF1 = math.atan2((F1Y-g2_oy)/EF1, (F1X-g2_ox)/EF1)
    F1EF2 = abs(math.fmod(xEF2-xEF1+5*math.pi, 2*math.pi)-math.pi)
    F1EF2p = F1EF2*g2_n/(2*math.pi)
    r_info += "tooth {:s} contact path angle from gearwheel2: {:0.2f} radian ({:0.2f} degree) {:0.2f}% of tooth length\n".format(involute_name, F1EF2, F1EF2*180/math.pi, F1EF2p*100)
  elif(g2_type=='l'):
    F1F2t = F1F2*math.cos(g2_sa)
    F1F2p = float(F1F2t)*g2_n/g2_bl
    r_info += "tooth {:s} contact path from gearbar2 tangential length {:0.2f} (mm) {:0.2f}% of tooth length\n".format(involute_name, F1F2t, F1F2p*100)
  # return
  r_iorfa = (r_info, r_action_line_outline)
  return(r_iorfa)

