import re

from .common import InfoExtractor
from ..utils import (
    compat_urllib_parse,
)

class CSpanIE(InfoExtractor):
    _VALID_URL = r'http://www.c-spanvideo.org/program/(.*)'

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        prog_name = mobj.group(1)
        webpage = self._download_webpage(url, prog_name)
        video_id = self._search_regex(r'programid=(.*?)&', webpage, 'video id')
        data = compat_urllib_parse.urlencode({'programid': video_id,
                                              'dynamic':'1'})
        info_url = 'http://www.c-spanvideo.org/common/services/flashXml.php?' + data
        video_info = self._download_webpage(info_url, video_id, u'Downloading video info')

        self.report_extraction(video_id)

        title = self._html_search_regex(r'<string name="title">(.*?)</string>',
                                        video_info, 'title')
        description = self._html_search_regex(r'<meta (?:property="og:|name=")description" content="(.*?)"',
                                              webpage, 'description',
                                              flags=re.MULTILINE|re.DOTALL)
        thumbnail = self._html_search_regex(r'<meta property="og:image" content="(.*?)"',
                                            webpage, 'thumbnail')

        url = self._search_regex(r'<string name="URL">(.*?)</string>',
                                 video_info, 'video url')
        url = url.replace('$(protocol)', 'rtmp').replace('$(port)', '443')
        path = self._search_regex(r'<string name="path">(.*?)</string>',
                            video_info, 'rtmp play path')

        return {'id': video_id,
                'title': title,
                'ext': 'flv',
                'url': url,
                'play_path': path,
                'description': description,
                'thumbnail': thumbnail,
                }
