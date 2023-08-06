'''
Created on May 2, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for source. A source provides content, the source type of a source dictates the format in which
the content is received from the source.
'''

from .type import SourceType
from ally.api.config import service, call, query, LIMIT_DEFAULT
from ally.api.criteria import AsBoolean, AsLikeOrdered, AsLike, AsEqual
from ally.api.type import Iter, Reference
from ally.support.api.entity import Entity, IEntityGetCRUDService, QEntity
from superdesk.api.domain_superdesk import modelData

# --------------------------------------------------------------------

@modelData
class Source(Entity):
    '''
    Provides the source model.
    '''
    Type = SourceType
    Name = str
    URI = Reference
    Key = str
    IsModifiable = bool
    OriginName = str
    OriginURI = str

# --------------------------------------------------------------------

@query(Source)
class QSource(QEntity):
    '''
    Provides the query for source model.
    '''
    name = AsLikeOrdered
    uri = AsLikeOrdered
    isModifiable = AsBoolean
    all = AsLike
    type = AsEqual

# --------------------------------------------------------------------

@service((Entity, Source), (QEntity, QSource))
class ISourceService(IEntityGetCRUDService):
    '''
    Provides the service methods for the source.
    '''

    @call
    def getAll(self, typeKey:SourceType.Key=None, offset:int=None, limit:int=LIMIT_DEFAULT, detailed:bool=True,
               q:QSource=None) -> Iter(Source):
        '''
        Provides all the available sources.
        '''

    @call
    def insert(self, source:Source) -> Source.Id:
        '''
        Insert the source, also the source will have automatically assigned the Id to it.

        @param source: Source
            The source to be inserted.

        @return: The id assigned to the source
        @raise InputError: If the source is not valid.
        '''
