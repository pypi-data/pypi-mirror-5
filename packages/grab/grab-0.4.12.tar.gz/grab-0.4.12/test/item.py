# coding: utf-8
from unittest import TestCase

import os
import sys

# Hack environment to force import "item" module from grab/item.py location
root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, root)
from lxml.html import fromstring

from grab import Grab, DataNotFound
from grab.item import (Item, IntegerField, StringField, DateTimeField, func_field,
                       FuncField)
from test.util import GRAB_TRANSPORT
from grab.tools.lxml_tools import get_node_text, parse_html
from grab.selector import XpathSelector
from grab.error import GrabMisuseError

XML = """<?xml version='1.0' encoding='utf-8'?>
<bbapi version='1'>
    <player id='26982032' retrieved='2012-09-11T07:38:44Z'>
        <firstName>Ardeshir</firstName>
        <lastName>Lohrasbi</lastName>
        <nationality id='89'>Pakistan</nationality>
        <age>19</age>
        <height>75</height>
        <dmi>14300</dmi>
        <comment>abc</comment>
        <comment_cdata><![CDATA[abc]]></comment_cdata>
        <games>
            <game name="quake1"></game>
            <game name="quake2"></game>
        </games>
    </player>
</bbapi>
"""

def calculated_func2(item, sel):
    if not hasattr(item, 'count2'):
        item.count2 = 1
    else:
        item.count2 += 1
    return sel.select('//height').text() + '-zoo2-' + str(item.count2)


class Player(Item):
    id = IntegerField('//player/@id')
    first_name = StringField('//player/firstname')
    retrieved = DateTimeField('//player/@retrieved', '%Y-%m-%dT%H:%M:%SZ')
    comment = StringField('//player/comment')
    comment_cdata = StringField('//player/comment_cdata')

    data_not_found = StringField('//data/no/found')

    @func_field()
    def calculated(item, sel):
        if not hasattr(item, 'count'):
            item.count = 1
        else:
            item.count += 1
        return sel.select('//height').text() + '-zoo-' + str(item.count)

    calculated2 = FuncField(calculated_func2, pass_item=True)

    @func_field()
    def height1(item, sel):
        return sel.select('//height').number()

    height2 = FuncField(lambda sel: sel.select('//height').number())


class GameItem(Item):
    class Meta:
        find_query = '//games/game'

    name = StringField('@name')


class ItemTestCase(TestCase):
    def get_item(self, content_type=None):
        grab = Grab(transport=GRAB_TRANSPORT)
        if content_type is not None:
            grab.setup(content_type=content_type)
        grab.fake_response(XML)
        player = Player(grab.tree)
        return player

    def test_integer_field(self):
        player = self.get_item()
        self.assertEquals(26982032, player.id)

    def test_string_field(self):
        player = self.get_item()
        self.assertEquals('Ardeshir', player.first_name)

    def test_datetime_field(self):
        player = self.get_item()
        self.assertEquals('2012-09-11 07:38:44', str(player.retrieved))

    def test_item_cache_feature(self):
        player = self.get_item()

        self.assertEquals('75-zoo-1', player.calculated)
        # should got from cache
        self.assertEquals('75-zoo-1', player.calculated)

        # test assigning value
        player.calculated = 'baz'
        self.assertEquals('baz', player.calculated)

        # test FuncField
        self.assertEquals('75-zoo2-1', player.calculated2)
        # should got from cache
        self.assertEquals('75-zoo2-1', player.calculated2)


    def test_dom_builder(self):
        player = self.get_item()

        # By default comment_cdata attribute contains empty string
        # because HTML DOM builder is used by default
        self.assertEquals('abc', player.comment)
        self.assertEquals('', player.comment_cdata)

        # We can control default DOM builder with
        # content_type option
        player = self.get_item(content_type='xml')

        self.assertEquals('abc', player.comment)
        self.assertEquals('abc', player.comment_cdata)

        self.assertRaises(DataNotFound, lambda: player.data_not_found)

    def test_func_field_decorator(self):
        player = self.get_item()
        self.assertEquals(75, player.height1)

    def test_func_field(self):
        player = self.get_item()
        self.assertEquals(75, player.height2)

    def test_get_function(self):
        func = Player.get_function('height1')
        html = '<html><body><height>3'
        self.assertEquals(3, func(XpathSelector(parse_html(html))))

        func = Player.get_function('height2')
        html = '<html><body><height>3'
        self.assertEquals(3, func(XpathSelector(parse_html(html))))

    def test_func_field_warning(self):
        """
        Test that usage of func_field decorators without "()"
        raises exception.
        """

        def foo():
            class TestItem(Item):
                @func_field
                def foo(self, sel):
                    return 'test'

        self.assertRaises(GrabMisuseError, foo)

        def foo():
            class TestItem(Item):
                @func_field()
                def foo(self, sel):
                    return 'test'
            
            return TestItem(fromstring('<div></div>')).foo

        self.assertEqual('test', foo())

    def test_unknown_selector_type(self):
        class TestItem(Item):
            pass

        TestItem(None)

        self.assertRaises(GrabMisuseError,
            lambda: TestItem(None, selector_type='Batman Selector'))

    def test_find(self):
        grab = Grab(transport=GRAB_TRANSPORT)
        grab.fake_response(XML)
        games = list(GameItem.find(grab.doc))
        self.assertEqual(['quake1', 'quake2'],
                         [x.name for x in games])


class JsonSelectorTestCase(TestCase):
    class PlanetItem(Item):
        class Meta:
            find_query = '$..planets[*]'
            selector_type = 'json'

        name = StringField('name')

    def setUp(self):
        self.data = {
            'existence': {
                'worldA': {
                    'id': 1,
                    'planets': [
                        {'name': 'Earth', 'cities': ['Moscow', 'Paris', 'Tokio'],
                         'population': 7000000000},
                        {'name': 'Mars', 'cities': [], 'population': 0},
                    ],
                },
                'worldB': {
                    'id': 2,
                    'planets': [
                        {'name': 'Onyx', 'cities': ['Oyyx', 'Yiiix'], 'population': 8000000},
                    ],
                },
            },
        }

    def it_just_works(self):
        item = self.PlanetItem(self.data, selector_type='json')

    def test_find(self):
        planets = list(self.PlanetItem.find(self.data))
        self.assertEqual(len(planets), 3)

    def test_string_field(self):
        planets = list(self.PlanetItem.find(self.data))
        self.assertEqual(set(['Earth', 'Mars', 'Onyx']),
                         set(x.name for x in planets))

