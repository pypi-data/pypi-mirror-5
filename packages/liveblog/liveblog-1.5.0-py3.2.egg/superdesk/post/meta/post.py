'''
Created on May 2, 2012

@package: superdesk posts
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the SQL alchemy meta for post API.
'''

from ..api.post import Post
from ally.support.sqlalchemy.mapper import validate
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import case
from sqlalchemy.types import TEXT, DateTime
from superdesk.collaborator.meta.collaborator import CollaboratorMapped
from superdesk.meta.metadata_superdesk import Base
from superdesk.post.meta.type import PostTypeMapped
from superdesk.user.meta.user import UserMapped
from ally.container.binder_op import validateManaged, validateRequired, \
    EVENT_PROP_UPDATE

# --------------------------------------------------------------------

@validate(exclude=('Type', 'CreatedOn', 'UpdatedOn', 'DeletedOn', 'PublishedOn'))
class PostMapped(Base, Post):
    '''
    Provides the mapping for Post.
    '''
    __tablename__ = 'post'
    __table_args__ = dict(mysql_engine='InnoDB', mysql_charset='utf8')

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Type = association_proxy('type', 'Key')
    Creator = Column('fk_creator_id', ForeignKey(UserMapped.Id, ondelete='RESTRICT'), nullable=False)
    Author = Column('fk_author_id', ForeignKey(CollaboratorMapped.Id, ondelete='RESTRICT'))
    Meta = Column('meta', TEXT)
    ContentPlain = Column('content_plain', TEXT)
    Content = Column('content', TEXT)
    CreatedOn = Column('created_on', DateTime, nullable=False)
    PublishedOn = Column('published_on', DateTime)
    UpdatedOn = Column('updated_on', DateTime)
    DeletedOn = Column('deleted_on', DateTime)
    @hybrid_property
    def IsModified(self):
        return self.UpdatedOn is not None
    @hybrid_property
    def IsPublished(self):
        return self.PublishedOn is not None
    @hybrid_property
    def AuthorName(self):
        if self.Author is None:
            if self.creator is None: return None
            else: return self.creator.Name
        return self.author.Name

    # Non REST model attributes --------------------------------------
    typeId = Column('fk_type_id', ForeignKey(PostTypeMapped.id, ondelete='RESTRICT'), nullable=False)
    type = relationship(PostTypeMapped, uselist=False, lazy='joined')
    author = relationship(CollaboratorMapped, uselist=False, lazy='joined')
    creator = relationship(UserMapped, uselist=False, lazy='joined')

    # Expression for hybrid ------------------------------------
    @classmethod
    @IsModified.expression
    def _IsModified(cls):
        return case([(cls.UpdatedOn != None, True)], else_=False)
    @classmethod
    @IsPublished.expression
    def _IsPublished(cls):
        return case([(cls.PublishedOn != None, True)], else_=False)
    @classmethod
    @AuthorName.expression
    def _AuthorName(cls):
        return case([(cls.Author == None, UserMapped.Name)], else_=CollaboratorMapped.Name)

validateRequired(PostMapped.Type)
validateManaged(PostMapped.Type, key=EVENT_PROP_UPDATE)
validateManaged(PostMapped.Author, key=EVENT_PROP_UPDATE)

validateManaged(PostMapped.CreatedOn)
validateManaged(PostMapped.PublishedOn)
validateManaged(PostMapped.UpdatedOn)
validateManaged(PostMapped.DeletedOn)
