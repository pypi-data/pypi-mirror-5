##################################################################################
#    Copyright (c) 2004-2009 Utah State University, All rights reserved.
#    Portions copyright 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                      
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Brent Lambert, David Ray, Jon Thomas, Shane Graber'''
__version__   = '$ Revision 0.0 $'[11:-2]

from zope.testing import doctest
from Products.PloneTestCase.PloneTestCase import setupPloneSite, installProduct
from Products.PloneTestCase.PloneTestCase import PloneTestCase, FunctionalTestCase
from setuptools import find_packages

from Products.Five import fiveconfigure
from Products.Five import zcml
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_plonebookmarklets_project():
    """
    Load and install packages required for the collective.plonebookmarklets tests
    """

    fiveconfigure.debug_mode = True
    
    import collective.plonebookmarklets
    zcml.load_config('configure.zcml',collective.plonebookmarklets)
    zcml.load_config('browser/configure.zcml',collective.plonebookmarklets)
    
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.plonebookmarklets')


setup_plonebookmarklets_project()
setupPloneSite(with_default_memberarea=0,extension_profiles=['collective.plonebookmarklets:default'])

oflags = (doctest.ELLIPSIS |
          doctest.NORMALIZE_WHITESPACE)

prod = "collective.plonebookmarklets"

class PloneBookmarkletsTestCase(PloneTestCase):
    """ Test Class """

class PloneBookmarkletsFunctionalTestCase(FunctionalTestCase, PloneBookmarkletsTestCase):
    """ Functional test class """
