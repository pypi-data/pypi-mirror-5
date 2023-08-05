"""
Test for remotebag.py.
"""

REMOTE_BAG = 'http://remotebag-test.tiddlyspace.com/bags/remotebag-test_public/tiddlers'

REMOTE_HTML = 'http://peermore.com/astool.html'

from tiddlyweb.config import config
from tiddlywebplugins.remotebag import init, get_remote_tiddlers, get_remote_tiddler
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb import control
from tiddlywebplugins.utils import get_store

import httplib2

def setup_module(module):
    import shutil
    try:
        shutil.rmtree('store')
    except OSError:
        pass
    init(config)
    module.store = get_store(config)
    module.environ = {'tiddlyweb.config': config,
            'tiddlyweb.store': store}

def test_get_tiddlers():
    tiddlers = list(get_remote_tiddlers(environ, REMOTE_BAG))

    titles = [tiddler.title for tiddler in tiddlers]
    for title in ['alpha', 'beta', 'gamma']:
        assert title in titles

    assert tiddlers[0].bag == REMOTE_BAG
    assert tiddlers[0]._text == None

def test_get_tiddler():
    remote_tiddler = Tiddler('alpha', REMOTE_BAG)
    tiddler = get_remote_tiddler(environ, remote_tiddler)

    assert tiddler.tags == ['alpha']
    assert tiddler.text == 'alpha'

def test_get_recipe():
    recipe = Recipe('thing')
    recipe.set_recipe([(REMOTE_BAG, '')])
    store.put(recipe)

    tiddlers = control.get_tiddlers_from_recipe(recipe, environ)
    titles = [tiddler.title for tiddler in tiddlers]
    for title in ['alpha', 'beta', 'gamma']:
        assert title in titles

    assert tiddlers[0].bag == REMOTE_BAG
    assert tiddlers[0]._text == None

def test_get_recipe_filters():
    recipe = Recipe('thing')
    recipe.set_recipe([(REMOTE_BAG, 'select=tag:alpha')])
    store.put(recipe)

    tiddlers = control.get_tiddlers_from_recipe(recipe, environ)
    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'alpha'

    assert tiddlers[0].bag == REMOTE_BAG
    assert tiddlers[0].text == 'alpha'

def test_get_remote_weird():
    recipe = Recipe('stuff')
    recipe.set_recipe([(REMOTE_HTML, '')])
    store.put(recipe)

    tiddlers = control.get_tiddlers_from_recipe(recipe, environ)
    assert len(tiddlers) == 1
    assert tiddlers[0].title == 'The Computer as Tool: From Interaction To Augmentation'
    tiddler = store.get(tiddlers[0])
    assert 'Humans are likely to grant intention to someone or something that performs actions in a way that is difficult to understand.' in tiddler.text
