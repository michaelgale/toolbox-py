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


text = """
The best way to find a phrase in this text is by
splitting the lines into consecutive word tuplets
and scanning the desired phrase across the tuplets
"""


def test_find_phrase():
    x = is_phrase_in_text("best way", text)
    assert x
    x = is_phrase_in_text("Best way", text)
    assert x
    x = is_phrase_in_text("Best way", text, case_sensitive=True)
    assert not x
    x = is_phrase_in_text("the fast car", text)
    assert not x
    x = is_phrase_in_text("the desired phrase", text)
    assert x
    x = is_phrase_in_text(["the desired phrase", "best way", "scanning"], text)
    assert x
    x = is_phrase_in_text(["the desired phrase", "best buy", "scanning"], text)
    assert not x


text_list = ["cat", "dog", "red car", "blue boat", "Dr. White", "Alice", "cat"]


def test_words_and_phrases():
    words, phrases = words_and_phrases(text_list)
    assert len(words) == 4
    assert len(phrases) == 3
    assert "dog" in words
    assert "cat" in words
    assert "blue boat" in phrases


value_text = """
this is placeholder text that could contain embedded values
Sub totalled: 34.52
Taxes: 10%
Total: 74.82
Pays: 16.32 dollars
footnote text under the document """


def test_parse_value():
    v = parse_value(value_text, "Total: %v")
    assert abs(v - 74.82) < 1e-6
    v = parse_value(value_text, "Final value: %v")
    assert v is None
    v = parse_value(value_text, "Sub totalled: %v")
    assert abs(v - 34.52) < 1e-6
    v = parse_value(value_text, "Pays: %v dollars")
    assert abs(v - 16.32) < 1e-6


email_text = """
this is placeholder text which may or may not contain
email addresses such as michael.gale@me.com or info@abc.com
but should not match things like blah@google or 
123@*$@.123
but could match single line addresses like
admin@eleceng.queensu.ca
"""
email_list = [
    "not an email",
    "shrek",
    "info@abc.com",
    "invalid@google",
    "possibly an email michael@me.com",
]


def test_find_email():
    x = get_email_addresses(email_text)
    assert len(x) == 3
    assert "info@abc.com" in x
    assert "123@$@.123" not in x
    assert "blah@google" not in x
    y = get_email_addresses(value_text)
    assert len(y) == 0
    z = get_email_addresses(email_list)
    assert len(z) == 2
    assert "michael@me.com" in z
    assert "invalid@google" not in z


tele_text = """
this is placeholder text which may or may not contain
telephone numbers such as 613-295-1899 or (613) 207-1452
but should not match things like +44 01983 336782 or 
204-293-293 or 1-270-1999
but could match single line numbers like
613 863-2541 but not 800-GET-MILK or 876-200-S0AP
Max Headroom PYTHON Python ALL-CAPS MyCAPS
"""


def test_find_telephone():
    x = get_telephone_numbers(tele_text)
    assert len(x) == 3
    assert "613 863-2541" in x
    assert "204-293-293" not in x
    y = get_telephone_numbers(email_text)
    assert len(y) == 0


def test_uppercase_words():
    x = get_uppercase_words(tele_text)
    assert len(x) == 4
    assert "PYTHON" in x
    assert "ALL-CAPS" in x
    assert "MyCAPS" not in x


def test_captial_words():
    x = get_capitalized_words(tele_text)
    assert len(x) == 3
    assert "Max" in x
    assert "Headroom" in x
    assert "MyCAPS" not in x


def test_get_numbers():
    x = get_numbers(tele_text)
    assert len(x) == 8
    assert "613" in x
    assert "204-293-293" in x
    assert "876-200-S0AP" not in x
