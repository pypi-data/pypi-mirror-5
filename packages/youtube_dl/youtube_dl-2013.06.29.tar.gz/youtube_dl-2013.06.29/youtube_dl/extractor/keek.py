import re

from .common import InfoExtractor


class KeekIE(InfoExtractor):
    _VALID_URL = r'http://(?:www\.)?keek\.com/(?:!|\w+/keeks/)(?P<videoID>\w+)'
    IE_NAME = u'keek'

    def _real_extract(self, url):
        m = re.match(self._VALID_URL, url)
        video_id = m.group('videoID')

        video_url = u'http://cdn.keek.com/keek/video/%s' % video_id
        thumbnail = u'http://cdn.keek.com/keek/thumbnail/%s/w100/h75' % video_id
        webpage = self._download_webpage(url, video_id)

        video_title = self._html_search_regex(r'<meta property="og:title" content="(?P<title>.*?)"',
            webpage, u'title')

        uploader = self._html_search_regex(r'<div class="user-name-and-bio">[\S\s]+?<h2>(?P<uploader>.+?)</h2>',
            webpage, u'uploader', fatal=False)

        info = {
                'id': video_id,
                'url': video_url,
                'ext': 'mp4',
                'title': video_title,
                'thumbnail': thumbnail,
                'uploader': uploader
        }
        return [info]
