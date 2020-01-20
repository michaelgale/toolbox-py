# Sample Test passing with nose and pytest

# system modules
import math, os.path
import sys
import pytest
import pprint
from math import pi

# my modules
from toolbox import *


def test_str_constraint():
    x = str_constraint("5.0", 5)
    assert x
    x = str_constraint("5.0", 4.75)
    assert not x
    x = str_constraint(">3.0", 3.5)
    assert x
    x = str_constraint(">3.0", 3.0)
    assert not x
    x = str_constraint(">3.0", 1)
    assert not x
    x = str_constraint(">=3.0", 3)
    assert x
    x = str_constraint(">=3.0", 6)
    assert x
    x = str_constraint("<9.0", 7)
    assert x
    x = str_constraint("<9.0", 13.0)
    assert not x
    x = str_constraint("<9.0", 9)
    assert not x
    x = str_constraint("<=9.0", 9)
    assert x
    x = str_constraint("<=9.0", 8)
    assert x


def test_valid_value():
    x = is_valid_value(3, 3)
    assert x
    x = is_valid_value(4.5, "4.5")
    assert x
    x = is_valid_value(6, ">5.0")
    assert x
    x = is_valid_value(5.0, [">2", "<6"])
    assert x
    x = is_valid_value(7, [">=7", "<10"])
    assert x
    x = is_valid_value(8, [">2", "<=7.5"])
    assert not x
    x = is_valid_value(7.5, [">2", "<=7.5"])
    assert x


all_words = ["abc", "def", "ghi", "jklmnop", "Important", "important", "ImPoRtAnT"]


def test_word_list():
    x = are_words_in_word_list("abc", all_words, case_sensitive=False)
    assert x
    x = are_words_in_word_list("Abc", all_words, case_sensitive=True)
    assert not x
    x = are_words_in_word_list("Important", all_words, case_sensitive=True)
    assert x
    x = are_words_in_word_list("Important", all_words, case_sensitive=False)
    assert x
    x = are_words_in_word_list("important", all_words, case_sensitive=False)
    assert x
    x = are_words_in_word_list(["abc", "def"], all_words, case_sensitive=False)
    assert x
    x = are_words_in_word_list(["abc", "Def"], all_words, case_sensitive=True)
    assert not x
    x = are_words_in_word_list(["important", "Def"], all_words, case_sensitive=True)
    assert not x
    x = are_words_in_word_list(["important", "Def"], all_words, case_sensitive=False)
    assert x
    x = are_words_in_word_list("jk*", all_words, case_sensitive=True)
    assert x
    x = are_words_in_word_list("Jk*", all_words, case_sensitive=True)
    assert not x
    x = are_words_in_word_list(["abc", "imp*"], all_words, case_sensitive=False)
    assert x
    x = are_words_in_word_list(["abc", "IMP*"], all_words, case_sensitive=True)
    assert not x

