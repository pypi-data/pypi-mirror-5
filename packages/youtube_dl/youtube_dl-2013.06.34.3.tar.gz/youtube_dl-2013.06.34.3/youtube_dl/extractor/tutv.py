import base64
import re

from .common import InfoExtractor
from ..utils import (
    compat_parse_qs,
)

class TutvIE(InfoExtractor):
    _VALID_URL=r'https?://(?:www\.)?tu\.tv/videos/(?P<id>[^/?]+)'
    _TEST = {
        u'url': u'http://tu.tv/videos/noah-en-pabellon-cuahutemoc',
        u'file': u'2742556.flv',
        u'md5': u'5eb766671f69b82e528dc1e7769c5cb2',
        u'info_dict': {
            u"title": u"Noah en pabellon cuahutemoc"
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)
        title = self._html_search_regex(
            r'<meta property="og:title" content="(.*?)">', webpage, u'title')
        internal_id = self._search_regex(r'codVideo=([0-9]+)', webpage, u'internal video ID')

        data_url = u'http://tu.tv/flvurl.php?codVideo=' + str(internal_id)
        data_content = self._download_webpage(data_url, video_id, note=u'Downloading video info')
        data = compat_parse_qs(data_content)
        video_url = base64.b64decode(data['kpt'][0])
        ext = video_url.partition('?')[0].rpartition('.')[2]

        info = {
            'id': internal_id,
            'url': video_url,
            'ext': ext,
            'title': title,
        }
        return [info]
