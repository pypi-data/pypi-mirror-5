'''
Created on May 3, 2012

@package: superdesk collaborator
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy implementation for collaborator API.
'''

from ..api.collaborator import ICollaboratorService
from ..meta.collaborator import CollaboratorMapped
from ally.container.ioc import injected
from ally.container.support import setup
from ally.support.sqlalchemy.util_service import buildQuery, buildLimits
from sql_alchemy.impl.entity import EntityGetCRUDServiceAlchemy
from superdesk.source.meta.source import SourceMapped
from ally.api.extension import IterPart
from superdesk.user.meta.user import UserMapped
from sqlalchemy.sql.expression import or_

# --------------------------------------------------------------------

@injected
@setup(ICollaboratorService, name='collaboratorService')
class CollaboratorServiceAlchemy(EntityGetCRUDServiceAlchemy, ICollaboratorService):
    '''
    Implementation for @see: ICollaboratorService
    '''

    def __init__(self):
        '''
        Construct the collaborator service.
        '''
        EntityGetCRUDServiceAlchemy.__init__(self, CollaboratorMapped)

    def getAll(self, userId=None, sourceId=None, offset=None, limit=None, detailed=False, qu=None, qs=None):
        '''
        @see: ICollaboratorService.getAll
        '''
        sql = self.session().query(CollaboratorMapped)
        sql = sql.outerjoin(UserMapped).filter(or_(UserMapped.Active == True, UserMapped.Active == None))
        if userId is not None: sql = sql.filter(CollaboratorMapped.User == userId)
        if sourceId is not None: sql = sql.filter(CollaboratorMapped.Source == sourceId)
        if qu is not None: sql = buildQuery(sql.join(UserMapped), qu, UserMapped)
        if qs is not None: sql = buildQuery(sql.join(SourceMapped), qs, SourceMapped)
        sqlLimit = buildLimits(sql, offset, limit)
        if detailed: return IterPart(sqlLimit.all(), sql.count(), offset, limit)
        return sqlLimit.all()
