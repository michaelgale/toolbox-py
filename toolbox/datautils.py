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

import datetime
import dateparser
import math
import numpy as np
import cv2
import re
import string
import pycountry
import itertools
import nltk
from email.header import decode_header, make_header

from toolbox.constants import *


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
    if isinstance(word_list, str):
        word_list = word_list.split()
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
    """Splits text into consecutive n-grams, e.g. pairwise, triples, etc."""
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


def parse_value(text, spec, max_value=None):
    """Finds a value embedded in a formatted string (spec) in the form of
    'placeholder placeholder2 %v placeholder3' where placeholder text
    helps locate the desired value denoted by %v"""
    text = text.replace("|", "")
    text = text.replace("]", "")
    text = text.replace("[", "")
    slen = len(spec.split())
    value = None
    if spec == "$":
        for t in text.split():
            if len(t) > 0:
                if t[0] == "$":
                    x = t.replace("$", "")
                    try:
                        value = float(x)
                        if max_value is not None:
                            if value <= max_value:
                                return value
                            else:
                                return None
                        else:
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
    """Checks to see if multi word phrase(s) is contained in supplied text"""
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
    """splits a list containing single words and/or multi-word phrases"""
    words = []
    phrases = []
    for t in text:
        if len(t.split()) > 1:
            phrases.append(t)
        else:
            words.append(t)
    return words, phrases


def get_email_addresses(text):
    """finds email addresses in text and return as a list"""
    s = []
    if isinstance(text, list):
        text = " ".join(text)
    text = str(text)
    for t in text.split():
        if len(t) > 1:
            address = re.search(
                "^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", t
            )
            if address is not None:
                s.append(address.group(0))
    return s


def get_telephone_numbers(text):
    """finds North American style telephone numbers in text and return as a list"""
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
    """Finds individual capitalized words and return in a list"""
    s = []
    if isinstance(text, list):
        text = " ".join(text)
    text = str(text)
    for t in text.split():
        if len(t) > 1:
            if t[0].isupper() and t[1:].islower():
                s.append(t)
    return s


def get_uppercase_words(text):
    """Finds individual uppercase words and return in a list"""
    s = []
    if isinstance(text, list):
        text = " ".join(text)
    text = str(text)
    for t in text.split():
        if len(t) > 1:
            if t.isupper() and not t.isnumeric():
                s.append(t)
    return s


def get_numbers(text):
    """Finds valid numeric values in text and return in a list"""
    s = []
    if isinstance(text, list):
        text = " ".join(text)
    text = str(text)
    for t in text.split():
        ok = True
        for c in t:
            if c not in list("0123456789.-"):
                ok = False
                break
        if ok:
            # check for invalid trivial single - or .
            if not all([x == "." for x in t]) and not all([x == "-" for x in t]):
                s.append(t)
    return s


def has_numbers(word):
    """Returns true if numbers are in word"""
    for c in word:
        if c in list("0123456789-"):
            return True
    return False


def strip_punc(
    text, filter_chars=None, from_right=False, from_left=False, replacement=""
):
    """Strips any common punctuation characters from text"""
    if filter_chars is None:
        filter_chars = ", . ; : - _ / ? ! @ & % ( ) [ ] { }"
    if from_right:
        for c in filter_chars.split():
            text = text.rstrip(c)
    if from_left:
        for c in filter_chars.split():
            text = text.lstrip(c)
    if not from_right and not from_left:
        for c in filter_chars.split():
            text = text.replace(c, replacement)
    return text


def word_split(text, word_list, case_sensitive=False):
    """Adds space between desired words which may or may not be delimited with whitespace.
    The desired words are specified by word_list and case sensitivity is optional"""
    if isinstance(word_list, str):
        word_list = word_list.split()
    for word in word_list:
        w = word.lower() if not case_sensitive else word
        if not case_sensitive:
            tl = text.lower()
        else:
            tl = text
        ts = tl.split(w)
        ns = len(ts)
        if ns > 1:
            new_text = []
            idx = 0
            for i, t in enumerate(ts):
                end = idx + len(t)
                if len(t) > 0:
                    new_text.append(text[idx:end])
                    if not t[-1] == " ":
                        new_text.append(" ")
                idx += len(t)
                if i < ns - 1:
                    new_text.append(text[idx : idx + len(word)])
                    idx += len(word)
                    if len(ts[i + 1]) > 0:
                        if not ts[i + 1][0] == " ":
                            new_text.append(" ")
            text = "".join(new_text)
    text = text.lstrip()
    text = text.rstrip()
    return text


def str_from_mime_words(text):
    """Returns a string from a possible MIME encoded-words string object."""
    try:
        ss = str(make_header(decode_header(text.decode())))
    except:
        try:
            ss = str(make_header(decode_header(text)))
        except:
            ss = str(text)
    return ss.lstrip().rstrip()


def clean_filename(text, replacement="_", no_spaces=True):
    """Returns a safe string object suitable for a filename.
    Objectionable characters such as path separators / \,
    punctuation, etc. are removed and substituted with either an
    underscore or other optionally specified character."""
    text = str_from_mime_words(text)
    text = strip_punc(
        text, filter_chars="/ \\ & , ; : + @ % *", replacement=replacement
    )
    if no_spaces:
        # get rid of spurious replacements around - and . (looks better)
        text = text.replace("  ", replacement).replace(" ", replacement)
        rep = "%s-%s" % (replacement, replacement)
        text = text.replace(rep, "-")
        rep = "%s-" % (replacement)
        text = text.replace(rep, "-")
        rep = "-%s" % (replacement)
        text = text.replace(rep, "-")
        rep = "%s." % (replacement)
        text = text.replace(rep, ".")
        # get rid of consecutive runs of replacement chars
        for n in [4, 3, 2]:
            rep = replacement * n
            text = text.replace(rep, replacement)
    return text


MONTHS_LIST = "jan feb mar apr may jun jul aug sep oct nov dec"


def month_num(month):
    """Converts any representation of a month to a corresponding integer.
    Jan = 1, Feb = 2, etc."""
    for i, m in enumerate(MONTHS_LIST.split()):
        if month.lower()[:3] == m:
            return i + 1
    return 0


WEEKDAY_LIST = "sun mon tue wed thu fri sat"


def day_week_num(day, sunday_first=True):
    """Converts any representation of a weekday to a corresponding integer.
    Sun = 1, Mon = 2, etc. if sunday_first, else Mon = 1, etc."""
    for i, m in enumerate(WEEKDAY_LIST.split()):
        if day.lower()[:3] == m:
            if sunday_first:
                return i + 1
            else:
                return i if i > 0 else 7
    return 0


def ymd_from_date_spec(date):
    """Returns a tuple of datetime.date ranges based on text specification.
    YYYY returns date(YYYY, 1, 1), date(YYYY, 2, 1)
    YYYY-MM returns date(YYYY, MM, 1), date(YYYY, MM+1, 1)
    YYYY-MM-DD returns date(YYYY, MM, DD), date(YYYY, MM, DD+1)"""
    ds = str(date).replace("-", "").replace("/", "")
    y1 = int(ds[:4])
    y2 = y1
    m1, m2 = 1, 12
    d1, d2 = 1, 31
    if len(ds) > 4:
        m1 = int(ds[4:6])
        m2 = min(m1 + 1, 12)
        if m1 < 12:
            d2 = 1
    if len(ds) > 6:
        m2 = m1
        d1 = int(ds[6:8])
        d2 = d1 + 1
        if d2 > 31:
            d2 = 1
            m2 = m1 + 1
            if m2 > 12:
                m2 = 1
                y2 += 1
    return datetime.date(y1, m1, d1), datetime.date(y2, m2, d2)


def cleanup_date(date, use_space=False):
    """Cleanup string in preparation for processing as a date."""
    clean_chars = "( ) ° . , = + * $ @"
    cd = date
    for c in clean_chars.split():
        if use_space:
            cd = cd.replace(c, " ")
        else:
            cd = cd.replace(c, "")
    # clean up possible spelling errors
    spelling_pairs = ["vay may", "fab feb", "dac dec", "var mar", "way may"]
    cd = cd.lower()
    for e in spelling_pairs:
        es = e.split()
        cd = cd.replace(es[0], es[1])
    return cd.rstrip()


def pick_best_ymd(date):
    """Choose the best date candidate from a triple numerical representation of
    date in either YMD, MDY, or DMY."""
    ymd_date = dateparser.parse(
        date,
        languages=["en"],
        settings={
            "STRICT_PARSING": True,
            "DATE_ORDER": "YMD",
        },
    )
    mdy_date = dateparser.parse(
        date,
        languages=["en"],
        settings={
            "STRICT_PARSING": True,
            "DATE_ORDER": "MDY",
        },
    )
    dmy_date = dateparser.parse(
        date,
        languages=["en"],
        settings={
            "STRICT_PARSING": True,
            "DATE_ORDER": "DMY",
        },
    )
    # ensure 4 digit year formats are preferred over 2 digit years
    if "-" in date:
        ds = date.split("-")
    elif "/" in date:
        ds = date.split("/")
    else:
        ds = None
    if ds is not None:
        ls = "".join([str(len(x)) for x in ds])
        if ls == "422":
            return ymd_date
        elif ls == "224":
            return mdy_date

    today = datetime.datetime.today()
    if all([d is not None for d in [ymd_date, mdy_date, dmy_date]]):
        dates = [
            (abs(today - ymd_date), ymd_date),
            (abs(today - mdy_date), mdy_date),
            (abs(today - dmy_date), dmy_date),
        ]
        dates = sorted(dates, key=lambda x: x[0])
        if len(dates) > 0:
            return dates[0][1]
    return None


def get_dates_from_text(phrases, preferred_format=None, debug=False):
    """Finds candidate dates from provided text."""

    def _valid_date(d):
        if d.year < 1995 or d.year > 2040:
            return None
        return datetime.datetime(d.year, d.month, d.day)

    dates = []
    date_formats = preferred_format
    if preferred_format is not None:
        if isinstance(preferred_format, list):
            date_formats = []
            for pf in preferred_format:
                date_formats.append(cleanup_date(pf))
        else:
            date_formats = [cleanup_date(preferred_format)]
    for phrase in phrases:
        phrase = cleanup_date(phrase, use_space=True)
        if len(phrase) < 8:
            continue
        new_date = None

        if date_formats is None:
            ymd = re.search("^\d{2,4}[\/-]\d{1,2}[\/-]\d{1,2}$", phrase)
            mdy = re.search("^\d{1,2}[\/-]\d{1,2}[\/-]\d{4}$", phrase)
            if ymd is not None:
                new_date = pick_best_ymd(ymd.group(0))
            elif mdy is not None:
                new_date = pick_best_ymd(mdy.group(0))
            else:
                ps = phrase.split()
                if len(ps) > 1:
                    for p in ps:
                        ymd = re.search("^\d{2,4}[\/-]\d{1,2}[\/-]\d{1,2}$", p)
                        mdy = re.search("^\d{1,2}[\/-]\d{1,2}[\/-]\d{4}$", p)
                        if ymd is not None:
                            new_date = pick_best_ymd(ymd.group(0))
                        elif mdy is not None:
                            new_date = pick_best_ymd(mdy.group(0))
                        if new_date is not None:
                            break

        split_phrase = phrase.split()
        if new_date is None:
            numbers = get_numbers(split_phrase)
            # avoid processing two number pairs or ambiguous number pairs
            # such as 19 Sep 17
            skip = False
            if len(numbers) == 2 and "-" in phrase:
                skip = True
            if len(numbers) >= 2 and len(split_phrase) == 3:
                # reject improper form 2022 04 march
                if len(numbers) == 2 and not has_numbers(split_phrase[2]):
                    skip = True
                if len(numbers[0]) == 2 and len(numbers[1]) == 2:
                    if numbers[0] == split_phrase[0] and numbers[1] == split_phrase[2]:
                        skip = True
                    elif (
                        numbers[0] == split_phrase[2] and numbers[1] == split_phrase[0]
                    ):
                        skip = True
                    elif len(numbers) == 3:
                        skip = True
            # guard against too many elements with only single characters
            if sum([len(e) == 1 for e in split_phrase]) >= 2:
                skip = True
            if date_formats is not None:
                d = dateparser.date.parse_with_formats(
                    phrase, date_formats=date_formats, settings=None
                )
                if isinstance(d, dateparser.date.DateData):
                    if d.date_obj is not None:
                        new_date = d.date_obj
            elif not skip:
                # guard against a long number string being confused as a timestamp
                if len(split_phrase) == 1 and not any(
                    [c in phrase for c in ["/", "-"]]
                ):
                    new_date = None
                else:
                    new_date = dateparser.parse(
                        phrase,
                        languages=["en"],
                        settings={"STRICT_PARSING": True},
                    )

        if new_date is not None:
            # guard against a long number string being confused as a timestamp
            if len(split_phrase) == 1 and not any([c in phrase for c in ["/", "-"]]):
                new_date = None
            # guard against time duration phrases
            if any(
                [
                    e in phrase.lower()
                    for e in ["month", "year", "day", "week", "hour", "min", "h"]
                ]
            ):
                new_date = None
        if new_date is not None:
            cdate = _valid_date(new_date)
            if cdate is not None:
                dates.append(cdate)
                if debug:
                    print(
                        "Candidate text: %-24s Format rules: %-16s Parsed date: %s"
                        % (phrase, date_formats, cdate)
                    )
    return dates


def most_popular(words, ignore_outliers=True, ignore_no_winner=True):
    """Computes the most popular word from a group of words."""
    count = len(words)
    if ignore_outliers and count > 10:
        new_words = sorted(words)
        min_idx = round(count * 0.1)
        max_idx = round(count * 0.9)
        words = new_words[min_idx:max_idx]
    word_dist = word_freq(words)
    if word_dist is not None:
        if len(word_dist) > 0:
            best_val = word_dist[0][1]
            not_unique = 0
            # if there is no clear winner then return either the
            # median value of the best values
            for i in list(range(1, len(word_dist))):
                if best_val == word_dist[i][1]:
                    not_unique = i
                    break
            if not_unique:
                if ignore_no_winner:
                    med = round(i / 2)
                    return word_dist[med][0]
                else:
                    return None
            return word_dist[0][0]
    return None


def replace_case_insensitive(text, word, new_word):
    """Replaces occurences of word with new_word in text without case sensitivity"""
    ts = text.split()
    ns = []
    for t in ts:
        if word.lower() in t.lower():
            ns.append(new_word)
        else:
            ns.append(t)
    return " ".join(ns)


def replace_prov_state_names(text, case_sensitive=True):
    """Replaces any instances of Canadian province or US state names with codes"""
    rs = text
    for k, v in {**CAN_PROVINCE_CODE, **US_STATE_CODE}.items():
        if case_sensitive and k in text:
            rs = rs.replace(k, v)
        elif not case_sensitive:
            rs = replace_case_insensitive(rs, k, v)
    return rs


def replace_prov_state_codes(text, case_sensitive=True):
    """Replaces any instances of province/state codes with names"""
    rs = text
    for k, v in {**CAN_PROVINCE_NAME, **US_STATE_NAME}.items():
        if case_sensitive and k in text:
            rs = rs.replace(k, v)
        elif not case_sensitive:
            rs = replace_case_insensitive(rs, k, v)
    return rs


def replace_country_names(text):
    """Replaces any instances of country names with 2-letter ISO code"""
    text = str(text)
    rs = text
    ts = text.split()
    for t in ts:
        tc = strip_punc(t)
        try:
            country_code = pycountry.countries.get(name=tc)
        except LookupError:
            continue
        if country_code is not None:
            rs = rs.replace(tc, country_code.alpha_2)
    for ng in [2, 3, 4]:
        ngs = n_grams(rs, ng, as_list=False)
        for n in ngs:
            tc = strip_punc(n)
            try:
                country_code = pycountry.countries.get(name=tc)
            except LookupError:
                continue
            if country_code is not None:
                rs = rs.replace(tc, country_code.alpha_2)
    return rs


def replace_country_codes(text):
    """Replaces any instances of country 2-letter ISO codes with names"""
    text = str(text)
    rs = text
    ts = text.split()
    for t in ts:
        try:
            country_code = pycountry.countries.get(alpha_2=t)
        except LookupError:
            continue
        if country_code is not None:
            rs = rs.replace(t, country_code.name)
    return rs


def word_freq(words, only_words=False):
    """Computes the frequency distributions of a provided word list.
    Returns a list of word/freq pairs.  Returns just the sorted
    word list if only_words is True."""
    dist = nltk.FreqDist(words)
    common = dist.most_common()
    word_dist = list(
        itertools.chain(
            *(sorted(ys) for _, ys in itertools.groupby(common, key=lambda t: t[1]))
        )
    )
    if only_words:
        return [w[0] for w in word_dist]
    return word_dist


def word_freq_str(words, min_count=0, up_to=0, style="flat"):
    """Returns a string showing word frequency in descending order."""
    s = []
    word_dist = word_freq(words)
    limit = up_to if up_to > 0 else len(words)
    for word in word_dist[:limit]:
        if word[1] >= min_count:
            if style == "flat":
                s.append("%dx: %s " % (word[1], word[0]))
            else:
                s.append("%3dx : %s\n" % (word[1], word[0]))
    return "".join(s)


def rgb_from_hex(hexcode, as_uint8=False):
    """Returns RGB tuple from hex code string.
    RGB can be scaled as 8-bit ints or floating point 0.0 to 1.0."""
    if len(hexcode) < 6:
        return 0, 0, 0
    hs = hexcode.lstrip("#")
    if not all(c in string.hexdigits for c in hs):
        return 0, 0, 0
    [rd, gd, bd] = tuple(int(hs[i : i + 2], 16) for i in (0, 2, 4))
    if as_uint8:
        return rd, gd, bd
    r = float(rd) / 255.0
    g = float(gd) / 255.0
    b = float(bd) / 255.0
    return r, g, b


def rgb_to_hex(rgb):
    """Returns hex RGB string from a tuple of RGB.
    Automatically determines if input tuple is scaled from 0 to 1 or 0 to 255."""
    if any([c > 1 for c in rgb]):
        return "#%02X%02X%02X" % (rgb[0], rgb[1], rgb[2])
    h = tuple(int(c * 255) for c in rgb)
    return "#%02X%02X%02X" % (h)


def rgb_to_hsv(rgb):
    """Converts colour RGB tuple to HSV tuple."""
    rgb = safe_colour_tuple(rgb, as_float=False)
    bgr = np.zeros(shape=(1, 1, 3), dtype=np.uint8)
    bgr[0][0] = [rgb[2], rgb[1], rgb[0]]
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    v = hsv[0][0]
    return (v[0], v[1], v[2])


def hsv_to_rgb(hsv, as_float=False):
    """Converts colour HSV tuple to RGB tuple.
    RGB can be scaled as 8-bit ints or floating point 0.0 to 1.0."""
    c = np.zeros(shape=(1, 1, 3), dtype=np.uint8)
    c[0][0] = [hsv[0], hsv[1], hsv[2]]
    bgr = cv2.cvtColor(c, cv2.COLOR_HSV2BGR)
    v = bgr[0][0]
    rgb = (v[2], v[1], v[0])
    return safe_colour_tuple(rgb, as_float=as_float)


def colour_name_from_tuple(colour):
    """Returns a standard colour name from a RGB colour tuple."""
    if not isinstance(colour, (list, tuple)):
        return None
    val = tuple(colour)
    for k, v in NAMED_COLOURS.items():
        if v == val:
            return k
    # find nearest match
    min_key = ""
    min_diff = 1e9
    for k, v in NAMED_COLOURS.items():
        diff = math.sqrt(
            (val[0] - v[0]) ** 2 + (val[1] - v[1]) ** 2 + (val[2] - v[2]) ** 2
        )
        if diff < min_diff:
            min_diff = diff
            min_key = k
    return min_key


def colour_name_from_hex(hexcode):
    """Returns a standard colour name from a RGB hex code."""
    colour = rgb_from_hex(hexcode, as_uint8=True)
    return colour_name_from_tuple(colour)


def colour_from_name(name, as_float=False):
    """Converts a standard colour name to a RGB tuple."""
    if name in NAMED_COLOURS:
        x = NAMED_COLOURS[name]
        if as_float:
            return x[0] / 255, x[1] / 255, x[2] / 255
        return x
    return None


def high_contrast_complement(colour):
    """Estimates either a black or white colour as a high contrast complement to another colour."""
    level = colour[0] ** 2 + colour[1] ** 2 + colour[2] ** 2
    if level < 1.25:
        return (1.0, 1.0, 1.0)
    return (0.0, 0.0, 0.0)


def safe_colour_tuple(colour, as_float=True):
    """Returns a RGB colour tuple from a variety of different input colour types.
    The input type is automatically determined and mapped to a standard RGB
    tuple representation scaled either as uint8 or 0.0 to 1.0 floats."""
    if isinstance(colour, str):
        if colour in NAMED_COLOURS:
            return colour_from_name(colour, as_float=as_float)
        return rgb_from_hex(colour, as_uint8=not as_float)
    elif isinstance(colour, (tuple, list)):
        if as_float and any([c > 1 for c in colour]):
            return tuple([c / 255 for c in colour])
        elif not as_float and not any([c > 1 for c in colour]):
            return tuple([int(min(255, c * 256)) for c in colour])
        return tuple(colour)
    elif isinstance(colour, (int, float)):
        c = int(colour)
        if c in LDRAW_COLOURS:
            return rgb_from_hex(LDRAW_COLOURS[c], as_uint8=not as_float)
    return (0, 0, 0)


def clamp_value(v, min_value, max_value, auto_limit=False):
    """Clamps an input value between a minimum and maximum range.
    auto_limit ensures that min and max bounds are ordered as min and max and
    swaps them if required."""
    min_v, max_v = min_value, max_value
    if auto_limit:
        max_v = max(min_value, max_value)
        min_v = min(min_value, max_value)
    cv = min(v, max_v)
    cv = max(cv, min_v)
    return cv


def eng_units(val, units="", prefix="", sigfigs=None, unitsep=True, unitary=False):
    """Represents a numeric value in engineering (3x orders magnitude) intervals
    with optional units and length constraints."""
    mags = [18, 15, 12, 9, 6, 3, 0, -3, -6, -9, -12, -15, -18]
    mods = "E P T G M k _ m u n p f a"
    sign = ""
    if val < 0:
        val = abs(val)
        sign = "-"
    sep = " " if unitsep else ""
    ndig = 6 if sigfigs is None else sigfigs + 1
    ndig = min(ndig, 7)
    ndig = max(ndig, 2)
    s = ""
    for mag, mod in zip(mags, mods.split()):
        if val > 10 ** mag:
            s = "%.3f" % (val / 10 ** mag)
            s = s[:ndig]
            s = s.rstrip("0")
            if s.endswith("."):
                s = s + "0"
            if unitary and mod == "_":
                if s.endswith(".0"):
                    s = s[:-2]
            s = "%s%s%s%s%s%s" % (prefix, sign, s, sep, mod, units)
            break
    s = s.replace("_", "")
    return s
