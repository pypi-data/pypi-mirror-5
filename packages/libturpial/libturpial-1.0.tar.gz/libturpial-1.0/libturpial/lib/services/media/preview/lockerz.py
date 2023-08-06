# -*- coding: utf-8 -*-

"""Lockers show media content service"""

from libturpial.api.models.media import *
from libturpial.lib.services.media.preview.base import *

class LockerzMediaContent(PreviewMediaService):
    def __init__(self):
        PreviewMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?lockerz.com"

    def do_service(self, url):
        url2 = 'http://api.plixi.com/api/tpapi.svc/imagefromurl?url=%s&size=big' % url
        rawimg = self._get_content_from_url(url2)
        return Media.new_image(url, rawimg)
