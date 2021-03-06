#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
# This file is part of the legocad python module.
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Misc data manipulation and validation functions
#
import re


def str_constraint(constraint, check_value, tolerance=0.1):
    """Validates a numeric constraint described by a string.  The string
    can specify fixed value constraints such as "0.0" or range constraints
    such as "<3.0" or ">=10.0"
    """
    check_greater_eq = True if ">=" in constraint else False
    check_less_eq = True if "<=" in constraint else False
    check_greater = True if ">" in constraint and not check_greater_eq else False
    check_less = True if "<" in constraint and not check_less_eq else False
    value = float(constraint.strip(">").strip("<").strip("="))
    if check_greater:
        if check_value > value:
            return True
    elif check_less:
        if check_value < value:
            return True
    elif check_greater_eq:
        if check_value >= value:
            return True
    elif check_less_eq:
        if check_value <= value:
            return True
    else:
        if abs(check_value - value) < tolerance:
            return True
    return False


def is_valid_value(value, value_constraints, tolerance=0.1):
    """Validates a length value against one or more constraints.  The
    constraints are specified either as fixed values or with strings which
    specify more complex criteria such as ">2.0".  Multiple constraints are
    specified as a list such as [">0.0", "<15.0"]
    """
    is_valid = True
    if not isinstance(value_constraints, list):
        constraints = [value_constraints]
    else:
        constraints = value_constraints
    for constraint in constraints:
        if isinstance(constraint, str):
            if not str_constraint(constraint, value):
                is_valid = False
        elif not abs(value - constraint) < tolerance:
            is_valid = False
    return is_valid


def are_words_in_word_list(
    words, word_list, case_sensitive=False, get_score=False, all_must_match=True
):
    """Checks if word(s) are contained in another word list.
    The search can be performed with or without case sensitivity.
    The check words can contain wildcards, e.g. "abc*" to allow
    a wider range of matches against the word list."""
    if not isinstance(words, list):
        check_words = [words]
    else:
        check_words = words
    found = {}
    for w in check_words:
        word = w.lower() if not case_sensitive else w
        if "*" in word:
            idx = word.find("*") - 1
            word = word[:idx]

        for wl in word_list:
            wl = wl.lower() if not case_sensitive else wl
            if wl.startswith(word):
                found[word] = True
    if all_must_match and len(found) == len(check_words):
        if get_score:
            return True, len(found)
        return True
    if not all_must_match and len(found) > 0:
        if get_score:
            return True, len(found)
        return True
    if get_score:
        return False, len(found)
    return False


def n_grams(text, n, as_list=True):
    """ Splits text into consecutive n-grams, e.g. pairwise, triples, etc. """
    w = text.split()
    if len(w) >= n:
        n_grams = [w[i : i + n] for i in range(len(w) - n + 1)]
        if as_list:
            return n_grams
        joined = []
        for n_gram in n_grams:
            joined.append(" ".join(n_gram))
        return joined
    return w


def parse_value(text, spec):
    """Finds a value embedded in a formatted string (spec) in the form of
    'placeholder placeholder2 %v placeholder3' where placeholder text
    helps locate the desired value denoted by %v"""
    slen = len(spec.split())
    value = None
    if spec == "$":
        for t in text.split():
            if len(t) > 0:
                if t[0] == "$":
                    x = t.replace("$", "")
                    try:
                        value = float(x)
                        return value
                    except:
                        pass
    for phrase in n_grams(text, slen, as_list=True):
        matches = 0
        if len(phrase) == slen:
            for p in zip(phrase, spec.split()):
                if p[0] == p[1]:
                    matches += 1
                if p[1] == "%v":
                    try:
                        x = p[0].replace("$", "")
                        x = x.replace("%", "")
                        value = float(x)
                    except:
                        pass
        if matches == slen - 1:
            return value
    return None


def is_phrase_in_text(phrase_items, text, case_sensitive=False):
    """ Checks to see if multi word phrase(s) is contained in supplied text """
    if isinstance(phrase_items, list):
        phrases = phrase_items
    else:
        phrases = [phrase_items]
    phrase_count = len(phrases)
    phrase_dict = {}
    for phrase in phrases:
        phrase_len = len(phrase.split())
        p = phrase.lower() if not case_sensitive else phrase
        lines = text.splitlines()
        for line in lines:
            w = line.lower() if not case_sensitive else line
            tuplets = n_grams(w, phrase_len)
            for tuplet in tuplets:
                if p == " ".join(tuplet):
                    phrase_dict[p] = True
                    break
            if p in phrase_dict:
                break
    if len(phrase_dict) == phrase_count:
        return True
    return False


def words_and_phrases(text):
    """ splits a list containing single words and/or multi-word phrases """
    words = []
    phrases = []
    for t in text:
        if len(t.split()) > 1:
            phrases.append(t)
        else:
            words.append(t)
    return words, phrases


def get_email_addresses(text):
    """ finds email addresses in text and return as a list """
    s = []
    if isinstance(text, list):
        text = " ".join(text)
    for t in text.split():
        if len(t) > 1:
            address = re.search(
                "^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", t
            )
            if address is not None:
                s.append(address.group(0))
    return s


def get_telephone_numbers(text):
    """ finds North American style telephone numbers in text and return as a list """
    s = []
    # look for telephone numbers spanning pairwise with area code and number
    # separated by whitespace
    if isinstance(text, list):
        all_words = " ".join(text)
    else:
        all_words = text
    pairs = n_grams(all_words, 2, as_list=False)
    if len(pairs) > 0:
        for pair in pairs:
            pair = pair.replace(":", " ")
            telno = re.search("\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{4}$", pair)
            if telno is not None:
                s.append(telno.group(0))
    # then look for completely contained telephone numbers which have not
    # already been added
    for t in all_words.split():
        if len(t) > 1:
            word = t.replace(":", " ")
            telno1 = re.match("^\d{1}[-]\d{3}[-]\d{3}[-]\d{4}$", word)
            telno2 = re.match("^\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{4}$", word)
            telno3 = re.match("^\d{3}[-]\d{4}$", word)
            if telno1 is not None or telno2 is not None or telno3 is not None:
                if word not in s:
                    is_already_in_s = False
                    for tn in s:
                        if len(word) <= len(tn):
                            if word == tn[-len(word) :]:
                                is_already_in_s = True
                    if not is_already_in_s:
                        s.append(word)
    return s


def get_capitalized_words(text):
    """ Finds individual capitalized words and return in a list """
    s = []
    if isinstance(text, list):
        text = " ".join(text)
    for t in text.split():
        if len(t) > 1:
            if t[0].isupper() and t[1:].islower():
                s.append(t)
    return s


def get_uppercase_words(text):
    """ Finds individual uppercase words and return in a list """
    s = []
    if isinstance(text, list):
        text = " ".join(text)
    for t in text.split():
        if len(t) > 1:
            if t.isupper() and not t.isnumeric():
                s.append(t)
    return s


def get_numbers(text):
    """ Finds valid numeric values in text and return in a list """
    s = []
    if isinstance(text, list):
        text = " ".join(text)
    for t in text.split():
        ok = True
        for c in t:
            if c not in list("0123456789.-"):
                ok = False
                break
        if ok:
            # check for invalid trivial single - or .
            if t != "-" and t != ".":
                s.append(t)
    return s
