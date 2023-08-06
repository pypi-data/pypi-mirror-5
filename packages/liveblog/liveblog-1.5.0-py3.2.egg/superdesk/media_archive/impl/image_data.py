'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

SQL Alchemy based implementation for the image data API. 
'''

from ally.cdm.spec import ICDM
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from superdesk.media_archive.api.image_data import IImageDataService, QImageData
from superdesk.media_archive.core.impl.meta_service_base import \
    MetaDataServiceBaseAlchemy
from superdesk.media_archive.core.spec import IMetaDataReferencer, \
    IThumbnailManager
from superdesk.media_archive.meta.image_data import ImageDataMapped

# --------------------------------------------------------------------

@injected
@setup(IImageDataService, name='imageDataService')
class ImageDataServiceAlchemy(MetaDataServiceBaseAlchemy, IMetaDataReferencer, IImageDataService):
    '''
    @see: IImageDataService
    '''

    cdmArchiveImage = ICDM; wire.entity('cdmArchiveImage')
    thumbnailManager = IThumbnailManager; wire.entity('thumbnailManager')

    def __init__(self):
        assert isinstance(self.cdmArchiveImage, ICDM), 'Invalid archive CDM %s' % self.cdmArchiveImage
        assert isinstance(self.thumbnailManager, IThumbnailManager), 'Invalid thumbnail manager %s' % self.thumbnailManager
       
        MetaDataServiceBaseAlchemy.__init__(self, ImageDataMapped, QImageData, self, self.cdmArchiveImage, self.thumbnailManager)
    
