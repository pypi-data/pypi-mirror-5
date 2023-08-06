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

from zope.app.component.interfaces import ISite
from Products.Five.site.localsite import enableLocalSiteHook
from zope.app.component.hooks import setSite
from utilities.interfaces import IPloneBookmarkletsUtility
from utilities.utils import PloneBookmarkletsUtility
from zope.component import getSiteManager


def importFinalSteps(context):
    site = context.getSite()
    if context.readDataFile('collective_plonebookmarklets_setup.txt') is None:
        return
    setupUtilities(site)

def setupUtilities(site):
    """ Register a local utility """

    if not ISite.providedBy(site):
        enableLocalSiteHook(site)

    setSite(site)

    sm = getSiteManager()
    if not sm.queryUtility(IPloneBookmarkletsUtility):
        sm.registerUtility(PloneBookmarkletsUtility('plonebookmarklets'),
                        IPloneBookmarkletsUtility)
