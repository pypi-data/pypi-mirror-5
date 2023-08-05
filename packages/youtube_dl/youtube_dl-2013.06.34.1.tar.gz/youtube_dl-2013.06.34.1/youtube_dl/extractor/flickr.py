import re

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    unescapeHTML,
)


class FlickrIE(InfoExtractor):
    """Information Extractor for Flickr videos"""
    _VALID_URL = r'(?:https?://)?(?:www\.)?flickr\.com/photos/(?P<uploader_id>[\w\-_@]+)/(?P<id>\d+).*'

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)

        video_id = mobj.group('id')
        video_uploader_id = mobj.group('uploader_id')
        webpage_url = 'http://www.flickr.com/photos/' + video_uploader_id + '/' + video_id
        webpage = self._download_webpage(webpage_url, video_id)

        secret = self._search_regex(r"photo_secret: '(\w+)'", webpage, u'secret')

        first_url = 'https://secure.flickr.com/apps/video/video_mtl_xml.gne?v=x&photo_id=' + video_id + '&secret=' + secret + '&bitrate=700&target=_self'
        first_xml = self._download_webpage(first_url, video_id, 'Downloading first data webpage')

        node_id = self._html_search_regex(r'<Item id="id">(\d+-\d+)</Item>',
            first_xml, u'node_id')

        second_url = 'https://secure.flickr.com/video_playlist.gne?node_id=' + node_id + '&tech=flash&mode=playlist&bitrate=700&secret=' + secret + '&rd=video.yahoo.com&noad=1'
        second_xml = self._download_webpage(second_url, video_id, 'Downloading second data webpage')

        self.report_extraction(video_id)

        mobj = re.search(r'<STREAM APP="(.+?)" FULLPATH="(.+?)"', second_xml)
        if mobj is None:
            raise ExtractorError(u'Unable to extract video url')
        video_url = mobj.group(1) + unescapeHTML(mobj.group(2))

        video_title = self._html_search_regex(r'<meta property="og:title" content=(?:"([^"]+)"|\'([^\']+)\')',
            webpage, u'video title')

        video_description = self._html_search_regex(r'<meta property="og:description" content=(?:"([^"]+)"|\'([^\']+)\')',
            webpage, u'description', fatal=False)

        thumbnail = self._html_search_regex(r'<meta property="og:image" content=(?:"([^"]+)"|\'([^\']+)\')',
            webpage, u'thumbnail', fatal=False)

        return [{
            'id':          video_id,
            'url':         video_url,
            'ext':         'mp4',
            'title':       video_title,
            'description': video_description,
            'thumbnail':   thumbnail,
            'uploader_id': video_uploader_id,
        }]
