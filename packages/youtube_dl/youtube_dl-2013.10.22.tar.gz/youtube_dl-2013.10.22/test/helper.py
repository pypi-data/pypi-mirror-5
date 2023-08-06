import errno
import io
import hashlib
import json
import os.path
import re
import types

import youtube_dl.extractor
from youtube_dl import YoutubeDL


def global_setup():
    youtube_dl._setup_opener(timeout=10)


def get_params(override=None):
    PARAMETERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "parameters.json")
    with io.open(PARAMETERS_FILE, encoding='utf-8') as pf:
        parameters = json.load(pf)
    if override:
        parameters.update(override)
    return parameters


def try_rm(filename):
    """ Remove a file if it exists """
    try:
        os.remove(filename)
    except OSError as ose:
        if ose.errno != errno.ENOENT:
            raise


class FakeYDL(YoutubeDL):
    def __init__(self, override=None):
        # Different instances of the downloader can't share the same dictionary
        # some test set the "sublang" parameter, which would break the md5 checks.
        params = get_params(override=override)
        super(FakeYDL, self).__init__(params)
        self.result = []
        
    def to_screen(self, s, skip_eol=None):
        print(s)

    def trouble(self, s, tb=None):
        raise Exception(s)

    def download(self, x):
        self.result.append(x)

    def expect_warning(self, regex):
        # Silence an expected warning matching a regex
        old_report_warning = self.report_warning
        def report_warning(self, message):
            if re.match(regex, message): return
            old_report_warning(message)
        self.report_warning = types.MethodType(report_warning, self)

def get_testcases():
    for ie in youtube_dl.extractor.gen_extractors():
        t = getattr(ie, '_TEST', None)
        if t:
            t['name'] = type(ie).__name__[:-len('IE')]
            yield t
        for t in getattr(ie, '_TESTS', []):
            t['name'] = type(ie).__name__[:-len('IE')]
            yield t


md5 = lambda s: hashlib.md5(s.encode('utf-8')).hexdigest()
