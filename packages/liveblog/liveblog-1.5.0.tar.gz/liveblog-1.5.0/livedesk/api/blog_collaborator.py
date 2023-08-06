'''
Created on May 4, 2012

@package: livedesk
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for livedesk blog collaborator.
'''

from .blog import Blog
from ally.api.config import service, call, DELETE, LIMIT_DEFAULT, UPDATE, alias
from ally.api.type import Iter
from livedesk.api.domain_livedesk import modelLiveDesk
from superdesk.collaborator.api.collaborator import Collaborator
from superdesk.source.api.source import QSource
from superdesk.user.api.user import QUser, User
from gui.action.api.action import Action

# --------------------------------------------------------------------

@modelLiveDesk(id='Name')
class BlogCollaboratorType:
    '''
    Provides the blog collaborator type.
    '''
    Name = str

@alias
class Type(BlogCollaboratorType):
    '''
    Short blog type alias
    '''
    
@modelLiveDesk(name=Collaborator)
class BlogCollaborator(Collaborator):
    '''
    Provides the blog collaborator model.
    '''
    Blog = Blog
    Type = BlogCollaboratorType

# --------------------------------------------------------------------

# No query

# --------------------------------------------------------------------

@service
class IBlogCollaboratorService:
    '''
    Provides the service methods for the blog collaborators.
    '''
        
    @call
    def getAllTypes(self) -> Iter(BlogCollaboratorType):
        '''
        Provides all the blog collaborator types.
        '''
        
    @call
    def getActions(self, userId:User.Id, blogId:Blog, path:str=None, origPath:str=None) -> Iter(Action):
        '''
        Get all actions registered for the provided user for the blog.
        '''

    @call
    def getById(self, blogId:Blog, collaboratorId:BlogCollaborator) -> BlogCollaborator:
        '''
        Provides the blog collaborator based on the id.
        '''

    @call
    def getAll(self, blogId:Blog, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True) -> Iter(BlogCollaborator):
        '''
        Provides all the blog collaborators.
        '''

    @call(webName="Potential")
    def getPotential(self, blogId:Blog, excludeSources:bool=True, offset:int=None, limit:int=LIMIT_DEFAULT,
                     detailed:bool=True, qu:QUser=None, qs:QSource=None) -> Iter(Collaborator):
        '''
        Provides all the collaborators that are not registered to this blog.
        '''

    @call(method=UPDATE)
    def addCollaborator(self, blogId:Blog.Id, collaboratorId:Collaborator.Id, typeName:Type.Name):
        '''
        Assigns the collaborator as a collaborator to the blog.
        '''
    # TODO: merge this methods when will do the combinations for UPDATE.
    @call(method=UPDATE, webName='Add')
    def addCollaboratorAsDefault(self, blogId:Blog.Id, collaboratorId:Collaborator.Id):
        '''
        Assigns the collaborator as a collaborator to the blog.
        '''

    @call(method=DELETE, webName='Remove')
    def removeCollaborator(self, blogId:Blog, collaboratorId:Collaborator) -> bool:
        '''
        Removes the collaborator from the blog.
        '''
