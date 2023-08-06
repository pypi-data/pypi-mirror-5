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

__author__  = '''Brent Lambert, David Ray, Jon Thomas'''
__version__   = '$ Revision 0.0 $'[11:-2]

from Products.CMFCore.utils import ContentInit, ToolInit
from config import PROJECTNAME, GLOBALS
from Products.CMFCore.permissions import AddPortalContent
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore.DirectoryView import registerDirectory
from AccessControl import allow_module, allow_class
from collective.captcha.browser.captcha import Captcha
from zope.i18nmessageid import MessageFactory
from enpraxis.educommons.loadtesttool import LoadTestTool

allow_module('collective.captcha.browser.captcha')
allow_class(Captcha)

tools = ( LoadTestTool, )

def initialize(context):

    import content

    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME), PROJECTNAME)

    ContentInit(PROJECTNAME + ' Content',
                content_types=content_types,
                permission=AddPortalContent,
                extra_constructors=constructors,
                fti=ftis,
                ).initialize(context)

    ToolInit('eduCommons Tool',
             tools = tools,
             icon='tool.gif',
             ).initialize(context)

eduCommonsMessageFactory = MessageFactory('eduCommons')

registerDirectory('skins', GLOBALS)
