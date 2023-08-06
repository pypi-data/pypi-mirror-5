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

from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.annotation.interfaces import IAnnotations
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from enpraxis.educommons import portlet
from enpraxis.educommons.utilities.interfaces import IECUtility
from enpraxis.educommons.annotations.interfaces import IClearCopyrightable, IAccessibilityCompliantable
from enpraxis.educommons.interfaces import ICourseUpdateEvent, IDeleteCourseObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements
import transaction


def add_course_portlets(obj, evt):
    """ add Course Summary portlet and OER Recommender portlet upon Course Creation  """
    rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=obj)
    right = getMultiAdapter((obj, rightColumn), IPortletAssignmentMapping, context=obj)

    #This code breaks the course object when the server has no outbound access to the web
    if u'OER Recommender' not in right:
        right[u'OER Recommender'] = portlet.oerrecommenderportlet.Assignment()

    if u'Course Summary' not in right:
        right[u'Course Summary'] = portlet.courseinfoportlet.Assignment()

    if u'Reuse Course' not in right:
        right[u'Reuse Course'] = portlet.reusecourseportlet.Assignment()


def set_default_creators(obj, evt):
    """ sets default value for Creator for newly created objects within a Course  """
    #Try block for instantiating Plone site
    try:
        ecutils = getUtility(IECUtility)
    except ComponentLookupError: 
        return

    creators = obj.Schema()['creators']

    if hasattr(obj, 'getECParent'):
        parent = obj.getECParent()

        #Check to see if this is a temp obj and within a course
        if obj.isTemporary() and parent.meta_type == 'Course' and obj.Type() != 'Course':
            creators.set(obj, ('(course_default)', ))

def set_default_excludefromnav(obj, evt):
    """ sets the default value for excludeFromNav or image, file, and document to True  """
    exclude = obj.Schema()['excludeFromNav']
    if obj.isTemporary() and obj.Type() not in ['Division', 'Course']:
        exclude.set(obj, True)

def update_clear_copyright(obj, evt):
    """ update clear copyright annotation  """
    if IClearCopyrightable.providedBy(evt.object):
	if hasattr(evt.object.REQUEST, 'clearedCopyright'):
	    if hasattr(evt.object.REQUEST, 'id'):
	        if evt.object.id == evt.object.REQUEST['id']:
                    IAnnotations(evt.object)['eduCommons.clearcopyright'] = evt.object.REQUEST['clearedCopyright']
                    evt.object.reindexObject()
        else:
	    IAnnotations(evt.object)['eduCommons.clearcopyright'] = False
            evt.object.reindexObject()

def update_accessibility_compliant(obj, evt):
    """ update accessibility compliant annotation  """
    if IAccessibilityCompliantable.providedBy(evt.object):
	if hasattr(evt.object.REQUEST, 'accessibilitycompliant'):
	    if hasattr(evt.object.REQUEST, 'id'):
	        if evt.object.id == evt.object.REQUEST['id']:
                    IAnnotations(evt.object)['eduCommons.accessible'] = evt.object.REQUEST['accessibilitycompliant']
                    evt.object.reindexObject()
        else:
	    IAnnotations(evt.object)['eduCommons.accessible'] = False
            evt.object.reindexObject()

def reindexOnReorder(obj, event):
    obj.reindexObject()


class CourseUpdate(ObjectEvent):
    """ Set namespace information in manifest. """
    implements(ICourseUpdateEvent)

    def __init__(self, object, workflow_action, bulkChange, initial_state=None):
        super(CourseUpdate, self).__init__(object)
        self.object = object
        self.target = workflow_action
        self.bulkChange = bulkChange
        self.initial_state = initial_state

class DeleteObjectEvent(ObjectEvent):
    """ Set namespace information in manifest. """
    implements(IDeleteCourseObjectEvent)

    def __init__(self, object, bulkChange, contains_published):
        super(DeleteObjectEvent, self).__init__(object)
        self.object = object
        self.bulkChange = bulkChange
        self.contains_published = contains_published


# Setting recursive ownership metadata

supported_objects_set_recursive_ownership = [
    'School', 
    'Division', 
    'Course', 
    'ATFolder', 
    'ATDocument', 
    'ATFile', 
    'ATImage', 
    'ATLink',
    'ATBlob'
]
   

def setRecursiveOwnership(obj, evt):
    """ Set ownership metadata recursively for all sub-objects. """
    if obj.isPrincipiaFolderish:
        if getattr(obj.REQUEST, 'recurse_ownership_folders', None):
            setOwnership(obj, obj.Creators(), obj.Contributors(), obj.Rights())


def setOwnership(obj, creators, contributors, rights):
    """ Set ownership metadat on object and sub-objects. """
    for ob in obj.objectValues():
        if ob.meta_type in supported_objects_set_recursive_ownership and ob != obj:
            if getattr(ob, 'setCreators', None):
                ob.setCreators(creators)
            if getattr(ob, 'setContributors', None):
                ob.setContributors(contributors)
            if getattr(ob, 'setRights', None):
                ob.setRights(rights)
            ob.reindexObject()
            if ob.isPrincipiaFolderish:
                setOwnership(ob, creators, contributors, rights)
        
def setIDToFilename(obj, evt):
    """ Undo the rename from title by default functionality """
    if obj.getId() == obj.generateNewId():
        filename = obj.getFilename()
        if filename:
            filename = obj._cleanupFilename(filename, obj.REQUEST)
            filename = obj._findUniqueId(filename)
            if filename:
                transaction.savepoint(optimistic=True)
                obj.setId(filename)

