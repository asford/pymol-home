from pymol import cmd, stored, util
from pymol.util import protein_assign_charges_and_radii
from glob import glob
import string

def selection_res_ids(selection):
    stored.select_res_ids = {}
    cmd.iterate(selection, "stored.select_res_ids[(chain, resv)] = 1")
    return list(stored.select_res_ids.iterkeys())

def print_selection_id(selection):
    print ",".join("%s.%s" % (chain, resv) for (chain, resv) in selection_res_ids(selection))

def print_selection_list(selection):
    print "%r" % selection_res_ids(selection)


cmd.extend( 'print_selection_id', print_selection_id)
cmd.auto_arg[0]["print_selection_id"] = [ cmd.selection_sc, 'selection', '']

cmd.extend( 'print_selection_list', print_selection_list)
cmd.auto_arg[0]["print_selection_list"] = [ cmd.selection_sc, 'selection', '']

def load_selection_id(selection_name, selection_id_string):
    selection_id_string = selection_id_string.replace('"', '')
    selection_id_string = selection_id_string.replace('\'', '')
    selection_id_list = [res.split(".") for res in selection_id_string.split(",")]
    selection_string = " or ".join("(chain %s and resi %s)" % (chain, resi) for chain, resi in selection_id_list)
    print "Selection ids: %s" % selection_id_string
    print "Selection string: %s" % selection_string
    cmd.select(selection_name, selection_string)

cmd.extend( 'load_selection_id', load_selection_id)
cmd.auto_arg[0]["load_selection_id"] = [ cmd.selection_sc, 'selection', '']

def cba(selection="(all)",quiet=1,_self=cmd):
    """Color selection by element."""
    pymol=_self._pymol
    cmd=_self
    s = str(selection)
    cmd.color("atomic","(("+s+") and not elem C)",quiet=quiet)

cmd.extend('cba', cba)
cmd.auto_arg[0]["cba"] = [ cmd.selection_sc, 'selection', '']

# Load all PDBs in the current directory
def load_glob(g, **load_kwargs):
    """Load all paths matching the given glob."""

    for f in glob(g):
        cmd.load(f,  **load_kwargs)

cmd.extend("load_glob",load_glob)

def protein_vacuum_esp(selection, mode=2, border=10.0, quiet = 1, _self=cmd):
    pymol=_self._pymol
    cmd=_self

    if ((string.split(selection)!=[selection]) or
         selection not in cmd.get_names('objects')):
        print " Error: must provide an object name"
        raise cmd.QuietException
    obj_name = selection + "_e_chg"
    map_name = selection + "_e_map"
    pot_name = selection + "_e_pot"
    cmd.disable(selection)
    cmd.delete(obj_name)
    cmd.delete(map_name)
    cmd.delete(pot_name)
    cmd.create(obj_name,"((polymer and ("+selection+
               ") and (not resn A+C+T+G+U)) or ((bymol (polymer and ("+
               selection+"))) and resn NME+NHE+ACE)) and (not hydro)")
         # try to just get protein...

    protein_assign_charges_and_radii(obj_name,_self=_self)
        
    ext = cmd.get_extent(obj_name)
    max_length = max(abs(ext[0][0] - ext[1][0]),abs(ext[0][1] - ext[1][1]),abs(ext[0][2]-ext[1][2])) + 2*border

    # compute an grid with a maximum dimension of 50, with 10 A borders around molecule, and a 1.0 A minimum grid

    sep = max_length/50.0
    if sep<1.0: sep = 1.0
    print " Util: Calculating electrostatic potential..."
    if mode==0: # absolute, no cutoff
        cmd.map_new(map_name,"coulomb",sep,obj_name,border)
    elif mode==1: # neutral, no cutoff
        cmd.map_new(map_name,"coulomb_neutral",sep,obj_name,border)
    else: # local, with cutoff
        cmd.map_new(map_name,"coulomb_local",sep,obj_name,border)      
        
    cmd.ramp_new(pot_name, map_name, selection=obj_name,zero=1)
    cmd.hide("everything",obj_name)
    cmd.show("surface",selection)
    cmd.set("surface_color",pot_name,selection)
    cmd.set("surface_ramp_above_mode",1,selection)

cmd.extend("protein_vacuum_esp", protein_vacuum_esp)
cmd.auto_arg[0]["protein_vacuum_esp"] = [ cmd.object_sc, 'object', '']

# vim: ft=python tabstop=4 expandtab shiftwidth=4 softtabstop=4
