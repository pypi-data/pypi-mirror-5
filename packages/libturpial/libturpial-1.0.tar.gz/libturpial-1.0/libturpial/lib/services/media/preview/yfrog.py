# -*- coding: utf-8 -*-

"""Yfrog show media content service"""

from libturpial.api.models.media import *
from libturpial.lib.services.media.preview.base import *


class YfrogMediaContent(PreviewMediaService):
    def __init__(self):
        PreviewMediaService.__init__(self)
        self.url_pattern = "(http(s)?://)?yfrog.com"

    def do_service(self, url):
        media_content_url = "%s:medium" % url
        rawimg = self._get_content_from_url(media_content_url)
        return Media.new_image(name, rawimg)
