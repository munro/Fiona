# coding=utf-8
"""Encoding tests"""

from glob import glob
import os
import shutil

import pytest

import fiona


@pytest.fixture(scope='function')
def gre_shp_cp1252(tmpdir):
    """A tempdir containing copies of gre.* files, .cpg set to cp1252

    The shapefile attributes are in fact utf-8 encoded.
    """
    test_files = glob(os.path.join(os.path.dirname(__file__), 'data/gre.*'))
    tmpdir = tmpdir.mkdir('data')
    for filename in test_files:
        shutil.copy(filename, str(tmpdir))
    tmpdir.join('gre.cpg').write('cp1252')
    yield tmpdir.join('gre.shp')


def test_broken_encoding(gre_shp_cp1252):
    """Reading as cp1252 mis-encodes a Russian name"""
    with fiona.open(str(gre_shp_cp1252)) as src:
        assert src.session._get_internal_encoding() == 'utf-8'
        feat = next(iter(src))
        assert feat['properties']['name_ru'] != u'Гренада'


def test_cpg_encoding(gre_shp_cp1252):
    """Reads a Russian name"""
    gre_shp_cp1252.join('../gre.cpg').write('utf-8')
    with fiona.open(str(gre_shp_cp1252)) as src:
        assert src.session._get_internal_encoding() == 'utf-8'
        feat = next(iter(src))
        assert feat['properties']['name_ru'] == u'Гренада'


def test_override_encoding(gre_shp_cp1252):
    """utf-8 override succeeds"""
    with fiona.open(str(gre_shp_cp1252), encoding='utf-8') as src:
        assert src.session._get_internal_encoding() == 'utf-8'
        assert next(iter(src))['properties']['name_ru'] == u'Гренада'
