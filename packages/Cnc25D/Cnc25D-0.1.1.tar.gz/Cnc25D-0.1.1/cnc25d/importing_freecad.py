# importing_freecad.py
# a function that replace in a more sophisticated way the import FreeCAD.
# created by charlyoleg on 2013/05/17
# license: CC BY SA 3.0

################################################################
# settings
################################################################

FREECADPATH=['/usr/lib/freecad/lib'] # add the path to the file FreeCAD.so to this list
#FREECADPATH=['/uuu/lib/freecad/lib', '/usr/lib/freecad/lib'] 
#FREECADPATH=['/uuu/lib/freecad/lib'] 

################################################################
# import
################################################################

import sys, os

################################################################
# function
################################################################

def importing_freecad():
  """ This function looks for the FreeCAD library and import it if needed
      just call this function where you want to import FreeCAD
  """
  # choose your favorite test to check if you are running with FreeCAD GUI or traditional Python
  freecad_gui = True
  #if not(FREECADPATH in sys.path): # test based on PYTHONPATH
  if not("FreeCAD" in dir()):       # test based on loaded module
    freecad_gui = False
  #print("dbg102: freecad_gui:", freecad_gui)
  
  if not(freecad_gui):
    freecad_path=''
    for p in FREECADPATH:
      if(os.path.isfile("%s/FreeCAD.so"%(p))):
        freecad_path=p
    if(freecad_path==''):
      print("ERR070: Error, the FreeCAD library path has not been found!")
      sys.exit(2)
    #print("dbg101: add FREECADPATH to sys.path")
    sys.path.append(freecad_path)
    import FreeCAD

################################################################
# main : only useful for debug
################################################################

if __name__ == "__main__":
  importing_freecad()
  print("FreeCAD.Version:", FreeCAD.Version())
  FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n")

