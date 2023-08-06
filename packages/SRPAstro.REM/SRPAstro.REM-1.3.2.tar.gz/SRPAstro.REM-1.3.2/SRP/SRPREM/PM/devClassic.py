""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.1.0
Author  : Stefano Covino
Date    : 13/08/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (23/08/2012) First version.
        : (13/08/2013) cos(ALT) factor in computation.


"""

import numpy
from Classic import Classic


def devClassic ((c_AN,c_AE,c_NPAE,c_BNP,c_TF,c_AOFS,c_EOFS),taz,talt,oaz,oalt):
    caz, calt = Classic((oaz,oalt),(c_AN,c_AE,c_NPAE,c_BNP,c_TF,c_AOFS,c_EOFS))
    return numpy.sqrt(((taz-caz)*numpy.cos(numpy.radians(talt)))**2).sum()/len(taz), numpy.sqrt((talt-calt)**2).sum()/len(talt)
