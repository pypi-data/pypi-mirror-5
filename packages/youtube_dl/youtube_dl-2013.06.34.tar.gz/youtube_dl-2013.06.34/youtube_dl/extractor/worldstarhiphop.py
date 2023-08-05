import re

from .common import InfoExtractor


class WorldStarHipHopIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www|m)\.worldstar(?:candy|hiphop)\.com/videos/video\.php\?v=(?P<id>.*)'
    IE_NAME = u'WorldStarHipHop'

    def _real_extract(self, url):
        m = re.match(self._VALID_URL, url)
        video_id = m.group('id')

        webpage_src = self._download_webpage(url, video_id)

        video_url = self._search_regex(r'so\.addVariable\("file","(.*?)"\)',
            webpage_src, u'video URL')

        if 'youtube' in video_url:
            self.to_screen(u'Youtube video detected:')
            return self.url_result(video_url, ie='Youtube')

        if 'mp4' in video_url:
            ext = 'mp4'
        else:
            ext = 'flv'

        video_title = self._html_search_regex(r"<title>(.*)</title>",
            webpage_src, u'title')

        # Getting thumbnail and if not thumbnail sets correct title for WSHH candy video.
        thumbnail = self._html_search_regex(r'rel="image_src" href="(.*)" />',
            webpage_src, u'thumbnail', fatal=False)

        if not thumbnail:
            _title = r"""candytitles.*>(.*)</span>"""
            mobj = re.search(_title, webpage_src)
            if mobj is not None:
                video_title = mobj.group(1)

        results = [{
                    'id': video_id,
                    'url' : video_url,
                    'title' : video_title,
                    'thumbnail' : thumbnail,
                    'ext' : ext,
                    }]
        return results
