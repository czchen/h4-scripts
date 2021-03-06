# -*- coding: utf-8 -*-

from Config import Config
from Wikidot import Wikidot

config = Config()
user_app = config['wikidot']['wikidot_api_user']
key = config['wikidot']['wikidot_api_key']

site = 'hackingthursday'
page_url = 'test'
title = 'Test'
content = '''
[[toc]]

+ heading level 1

[[code]]
...
[[/code]]
'''

wikidot = Wikidot()


def test_auth():
    assert wikidot.auth(user_app, key)


def test_set_site():
    assert wikidot.set_site(site)


def test_save_page():
    assert wikidot.save_page(page_url, title, content)


def test_get_page():
    assert wikidot.get_page(page_url)


def test_get_pages_meta():
    assert wikidot.get_pages_meta(page_url)


def test_list_pages():
    assert wikidot.list_pages()
