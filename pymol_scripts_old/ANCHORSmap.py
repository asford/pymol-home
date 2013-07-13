import pymol
from pymol import cmd

import sys, os
from os import path
from glob import glob

import numpy


# ANCHORSmap rank files start with blank line, and have a column header "pot E" which breaks table parsing.
def ProcessANCHORSmapRanksFile(filename):
    f = open(filename, "r")

    try:
        for line in f:
            yield line.replace("pot E", "potE")
    except:
        close(f)
        raise

def viewANCHORSmapResultDirectory(resultdir, score_cutoff, spectrum = "blue_white_red", spectrumMinimum = None, spectrumMaximum = None):
    assert path.exists(resultdir)

    #Create result directory selection
    result_selection = "anchors-%s" % path.basename(resultdir)
    result_objects = []

    cmd.select(result_selection, "none")

    stubdirs = glob(path.join(resultdir,"*"))

    for stubdir in stubdirs:
        if not path.exists(path.join(stubdir, "Out", "ranks.out")):
            continue

        ranks = numpy.recfromtxt(ProcessANCHORSmapRanksFile(path.join(stubdir, "Out", "ranks.out")), names=True, skiprows=1)

        #Create result stub selection
        stub_selection = "%s-%s" % (result_selection, path.basename(stubdir))
        stub_objects = []
        cmd.select(stub_selection, "none")

        for x in xrange(len(ranks)):
            if ranks["DG"][x] < score_cutoff:
                #Load the stub result into an object
                filename = "%s.pdb" % path.join(stubdir, "Pdb", ranks["FName"][x])
                objectname = "%s-%s-%s" % (path.basename(resultdir), path.basename(stubdir), ranks["FName"][x])
                cmd.load(filename, objectname)

                #Add object to result and stub selections
                result_objects.append(objectname)
                stub_objects.append(objectname)


                #Load DDG value into B value
                cmd.alter("/%s/" % objectname, "b=%s" % ranks["DG"][x])

        cmd.select(stub_selection, " | ".join(stub_objects))

    cmd.select(result_selection, " | ".join(result_objects))

    #Color result selection by B value 
    cmd.spectrum("b", spectrum, result_selection, minimum = spectrumMinimum, maximum = spectrumMaximum) 

def viewANCHORSmapList(listfile, spectrum = "blue_white_red", spectrumMinimum = None, spectrumMaximum = None):
    assert path.exists(listfile)    

    #Create result selection
    result_selection = "anchors-%s" % path.basename(listfile)
    result_objects = []
    cmd.select(result_selection, "none")

    ranks = numpy.recfromtxt(ProcessANCHORSmapRanksFile(listfile), names=True)

    #Create stub selection objects
    stub_selections = {}
    for x in xrange(len(ranks)):
        if not stub_selections.has_key(ranks["stub"][x]):
            stub_selections[ranks["stub"][x]] = []

    for stub in stub_selections:
        cmd.select("%s-%s" % (result_selection, stub), "none")

    for x in xrange(len(ranks)):
        #Load the stub result into an object
        filename = "%s.pdb" % path.join(path.dirname(listfile), ranks["stub"][x], "Pdb", ranks["FName"][x])
        objectname = "%s-%s-%s" % (path.basename(listfile), ranks["stub"][x], ranks["FName"][x])
        cmd.load(filename, objectname)

        #Add object to result and stub selections
        result_objects.append(objectname)
        stub_selections[ranks["stub"][x]].append(objectname)

        #Load DDG value into B value
        cmd.alter("/%s/" % objectname, "b=%s" % ranks["DG"][x])

    for stub in stub_selections:
        cmd.select("%s-%s" % (result_selection, stub), " | ".join(stub_selections[stub]))
    cmd.select(result_selection, " | ".join(result_objects))

    #Color result selection by B value 
    cmd.spectrum("b", spectrum, result_selection, minimum = spectrumMinimum, maximum = spectrumMaximum) 

cmd.extend("viewANCHORSmapResultDirectory", viewANCHORSmapResultDirectory)
cmd.extend("viewANCHORSmapList", viewANCHORSmapList)
