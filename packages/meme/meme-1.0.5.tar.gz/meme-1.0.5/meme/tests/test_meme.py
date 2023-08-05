import os
import shlex
import unittest
import httpretty
from meme import meme


ARGS_POPULAR = shlex.split('-l')
ARGS_SEARCH = shlex.split('-s blah')
ARGS_CREATE_EXPLICIT = shlex.split('title "line 1" "line 2"')
ARGS_CREATE_SEARCH = shlex.split('-s blah "line 1" "line 2"')

fp = lambda f: os.path.join(os.path.dirname(__file__), f)

FILE_POPULAR = fp('popular.json')
FILE_SEARCH = fp('search.json')
FILE_ACTION_RESULT = fp('action_result.json')
FILE_INFO = fp('info.json')


def search_body(request, url, headers):
    jsonfile = FILE_SEARCH if request.querystring.get('q', None) \
                           else FILE_POPULAR
    with open(jsonfile) as h:
        return 200, headers, h.read()


class TestMeme(unittest.TestCase):
    def setUp(self):
        content_type = 'application/json; charset=utf-8'
        httpretty.enable()
        with open(FILE_POPULAR) as h:
            httpretty.register_uri(httpretty.GET, meme.POPULAR,
                                   body=search_body, content_type=content_type)
        with open(FILE_SEARCH) as h:
            httpretty.register_uri(httpretty.GET, meme.SEARCH.format('blah'),
                                   body=search_body, content_type=content_type)
        with open(FILE_ACTION_RESULT) as h:
            httpretty.register_uri(httpretty.POST, meme.ACTION,
                                   body=h.read(), content_type=content_type)
        with open(FILE_INFO) as h:
            httpretty.register_uri(httpretty.GET, meme.INFO.format('1234'),
                                   body=h.read(), content_type=content_type)

    def tearDown(self):
        httpretty.disable()

    def test_list_popular(self):
        response = meme.cli(ARGS_POPULAR)
        self.assertTrue('Philosoraptor' in response)

    def test_search(self):
        response = meme.cli(ARGS_SEARCH)
        self.assertTrue('Cat' in response)

    def test_create_explicit(self):
        response = meme.cli(ARGS_CREATE_EXPLICIT)
        self.assertTrue(response.endswith('.jpg'))

    def test_create_search(self):
        response = meme.cli(ARGS_CREATE_SEARCH)
        self.assertTrue(response.endswith('.jpg'))


