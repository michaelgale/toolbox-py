# Sample Test passing with nose and pytest

# system modules
import math, os.path
import sys
import pytest
import pprint
from math import pi

# my modules
from toolbox import *


def test_apply_params():
    class TestParams(object):
        PARAMS = {
            "abc": None,
            "defg": False,
            "hijk": 0.0,
            "lmno": "My Params",
        }

        def __init__(self, **kwargs):
            apply_params(self, kwargs, locals())

    tc = TestParams()
    assert "abc" in tc.__dict__
    assert "defg" in tc.__dict__
    assert "hijk" in tc.__dict__
    assert "lmno" in tc.__dict__
    assert tc.abc is None
    assert not tc.defg
    assert tc.hijk == 0.0
    assert tc.lmno == "My Params"

def test_yaml_params():
    tp = Params(yml="test_params.yml")
    assert "abc" in tp.__dict__
    assert "defg" in tp.__dict__
    assert "hijk" in tp.__dict__
    assert len(tp.abc) == 3
    assert tp.abc.a1 == 0
    assert tp.abc.a2 == 1.0
    assert tp.abc.a3 == 5.0
    assert tp.defg.b1 == 0.1
    assert tp.defg.b2 == 25.0
    assert tp.defg.b3 == 56.0
    assert tp.hijk.c1 == "This param"
    assert tp.hijk.c2 == "That param"
    assert tp.hijk.c3 == True
    assert len(tp.hijk.c4) == 7
    assert tp.hijk.c4[0] == 0
    assert tp.hijk.c4[-1] == 13
