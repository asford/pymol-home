'''
(c) 2010 Thomas Holder, Max Planck Institute for Developmental Biology

PyMOL wrapper for DSSP and STRIDE

From http://www.mail-archive.com/pymol-users@lists.sourceforge.net/msg09558.html

dssp may be installed on osx via the macports 'whatcheck' package.

'''

from pymol import cmd, stored
from subprocess import Popen, PIPE
import tempfile, os

def _common_ss_alter(selection, ss_dict, ss_map, raw=''):
	'''
DESCRIPTION

    Shared code of 'dssp' and 'stride' functions.
	'''
	if raw != 'ss':
		cmd.alter(selection, 'ss = ss_map.get(ss_dict.get((model,chain,resi)), "")',
				space={'ss_dict': ss_dict, 'ss_map': ss_map})
	if raw != '':
		cmd.alter(selection, raw + ' = ss_dict.get((model,chain,resi), "")',
				space={'ss_dict': ss_dict})
	cmd.rebuild(selection, 'cartoon')

def dssp(selection='(all)', exe='dsspcmbi', raw=''):
	'''
DESCRIPTION

    Secondary structure assignment with DSSP.
    http://swift.cmbi.ru.nl/gv/dssp/

ARGUMENTS

    selection = string: atom selection {default: all}

    exe = string: name of dssp executable {default: dsspcmbi}

    raw = string: atom property to load raw dssp class into {default: ''}

EXAMPLE

    dssp all, /sw/bin/dsspcmbi, raw=text_type
    color gray
    color red, text_type H
    color orange, text_type G
    color yellow, text_type E
    color wheat, text_type B
    color forest, text_type T
    color green, text_type S
    set cartoon_discrete_colors, 1

SEE ALSO

    dss, stride
	'''
	ss_map = {
		'B': 'S', # residue in isolated beta-bridge
		'E': 'S', # extended strand, participates in beta ladder
		'T': 'L', # hydrogen bonded turn
		'G': 'H', # 3-helix (3/10 helix)
		'H': 'H', # alpha helix
		'I': 'H', # 5 helix (pi helix)
		'S': 'L', # bend
		' ': 'L', # loop or irregular
	}
	tmpfilepdb = tempfile.mktemp('.pdb')
	ss_dict = dict()
	for model in cmd.get_object_list(selection):
		cmd.save(tmpfilepdb, '%s and (%s)' % (model, selection))
		process = Popen([exe, '-na', tmpfilepdb], stdout=PIPE)
		for line in process.stdout:
			if line.startswith('  #  RESIDUE'):
				break
		for line in process.stdout:
			resi = line[5:11].strip()
			chain = line[11].strip()
			ss = line[16]
			ss_dict[model,chain,resi] = ss
	os.remove(tmpfilepdb)
	_common_ss_alter(selection, ss_dict, ss_map, raw)
cmd.extend('dssp', dssp)

def stride(selection='(all)', exe='stride', raw=''):
	'''
DESCRIPTION

    Secondary structure assignment with STRIDE.
    http://webclu.bio.wzw.tum.de/stride/

SEE ALSO

    dss, dssp
	'''
	ss_map = {
		'C': 'L',
		'B': 'S',
		'b': 'S',
		'E': 'S',
		'T': 'L',
		'G': 'H',
		'H': 'H',
	}
	tmpfilepdb = tempfile.mktemp('.pdb')
	ss_dict = dict()
	for model in cmd.get_object_list(selection):
		cmd.save(tmpfilepdb, '%s and (%s)' % (model, selection))
		process = Popen([exe, tmpfilepdb], stdout=PIPE)
		for line in process.stdout:
			if not line.startswith('ASG'):
				continue
			chain = line[9].strip('-')
			resi = line[11:16].strip()
			ss = line[24]
			ss_dict[model,chain,resi] = ss_map.get(ss)
	os.remove(tmpfilepdb)
	_common_ss_alter(selection, ss_dict, ss_map, raw)
cmd.extend('stride', stride)

# tab-completion
cmd.auto_arg[0].update({
	'dssp'           : [ cmd.selection_sc           , 'selection'       , ', ' ],
	'stride'         : [ cmd.selection_sc           , 'selection'       , ', ' ],
})
