from pymol import cmd, stored
from InterfaceUtils import colorInterface

def setup_fragment_match(selection_name = "(all)", stub_object_name = "stubs"):
    colorInterface(selection_name)
    cmd.extract(stub_object_name, "%s and chain C:E" % selection_name)
    cmd.zoom(selection_name)

def setup_fragment_view(selection_name = "(all)", context_object_name = "context"):
    colorInterface(selection_name)
    cmd.extract(context_object_name, "%s and chain A" % selection_name)
    cmd.zoom(selection_name)
    cmd.show("surface", context_object_name)
    cmd.set("transparency", .5)
    

cmd.extend("setup_fragment_match", setup_fragment_match)
cmd.extend("setup_fragment_view", setup_fragment_view)
