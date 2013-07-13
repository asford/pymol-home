import pymol
from pymol import cmd

import sys, os
import re
import itertools

def viewAlaScan(resultfile, spectrumMinimum = None, spectrumMaximum = None, _self = None):
    assert resultfile is not None

    scanresults = list(
        itertools.takewhile(
            lambda l: l.count("End report for alascan") == 0,
            itertools.dropwhile(
                lambda l: l.count("protocols.simple_filters.AlaScan") == 0,
                open(resultfile).readlines())))
    
    resultformat = re.compile(
        "(?P<residue>\w\w\w) \s+ (?P<residue_id>\d+) \s+ (?P<chain>\w) \s+ : \s+ (?P<value>[-\d\.]+)",
        re.VERBOSE) # ARG 354 B :    0.0096

    matches = [m.groupdict() for m in resultformat.finditer("\n".join(scanresults))]

    print "Loading Alascan results:"
    for m in matches:
        print "    " + " ".join([m["residue"], m["residue_id"], m["chain"], m["value"]])

    LoadResidueResults([
                        {"residue_id"   : int(m["residue_id"]),
                         "chain"        : m["chain"],
                         "value"        : float(m["value"])}
                        for m in matches],
                        spectrumMinimum = spectrumMinimum,
                        spectrumMaximum = spectrumMaximum)

def LoadResidueResults(results, resultfield="value", objectName="", selectionName = None, spectrum = "blue_white_red", spectrumMinimum = None, spectrumMaximum = None):

    if selectionName is None:
        selectionName = "%s_results" % objectName

    #Clear B factor on the entire object and results selection
    cmd.alter("/%s/" % objectName, "b=0.0")
    cmd.select(selectionName, "none")

    #Reset b factor to value and create named selection
    for result in results:
        selectexpr = "/%s//%s/%i/" % (objectName, result['chain'], result['residue_id'])

        cmd.alter(selectexpr, "b=%f" % result[resultfield])
        cmd.select(selectionName, "%s | %s " % (selectionName, selectexpr))

    cmd.spectrum("b", spectrum, selectionName, minimum = spectrumMinimum, maximum = spectrumMaximum) 
 
cmd.extend("viewAlaScan", viewAlaScan)
