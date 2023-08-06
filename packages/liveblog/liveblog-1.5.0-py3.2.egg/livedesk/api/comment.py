'''
Created on May 27, 2013

@package: livedesk
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Martin Saturka

API specifications for blog comment.
'''

from ..api.blog_post import BlogPost, QBlogPost
from ally.api.config import service, call, INSERT
from ally.api.type import Iter
from ally.support.api.keyed import Entity
from livedesk.api.domain_livedesk import modelLiveDesk
from livedesk.api.blog import Blog
from superdesk.post.api.post import Post

# --------------------------------------------------------------------

@modelLiveDesk(name='Comment')
class BlogComment:
    '''
    Separate model for the comment itself.
    '''
    UserName = str
    CommentText = str
    CommentSource = str

# --------------------------------------------------------------------
# No query
# --------------------------------------------------------------------

@service
class IBlogCommentService:
    '''
    Provides the service methods for the blog comment.
    '''

    @call(webName='Comment')
    def getComments(self, blogId:Blog.Id, offset:int=None, limit:int=None, detailed:bool=True,
                    q:QBlogPost=None) -> Iter(BlogPost):
        '''
        Lists comment Posts of the specified blog.
        '''

    @call(webName='Post')
    def getOriginalComments(self, blogId:Blog.Id, offset:int=None, limit:int=None, detailed:bool=True,
                    q:QBlogPost=None) -> Iter(BlogComment):
        '''
        Lists original comments of Comment-based Posts of the specified blog.
        '''

    @call(method=INSERT)
    def addComment(self, blogId:Blog.Id, comment:BlogComment) -> BlogPost.Id:
        '''
        Inserts a new blog comment.
        '''
