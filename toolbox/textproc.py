#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
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

import copy
import string
import nltk

from toolbox.datautils import *


class TextProc:
    def __init__(self, text, **kwargs):
        self.debug = False
        self.ignore_case = False
        self.filter = nltk.corpus.stopwords.words("english")
        self.filter.extend(nltk.corpus.stopwords.words("french"))
        self.tokens = []
        self.dates = []
        self.numbers = []
        self.word_dist = []
        self.capitalized_words = []
        self.uppercase_words = []
        self.telephone_no = []
        self.email_address = []
        self.raw_text = copy.copy(text)
        self.split_text = self.raw_text.split()
        self.raw_words = self.filter_text(ignore_numbers=True)
        self.words = [w.lower() for w in self.raw_words]
        self.word_set = word_freq(self.words, only_words=True)
        self.tokens = self.filter_text(ignore_numbers=False)
        self.capitalized_words = get_capitalized_words(self.raw_words)
        self.uppercase_words = get_uppercase_words(self.raw_words)
        self.numbers = get_numbers(self.tokens)
        self.telephone_no = get_telephone_numbers(self.tokens)
        self.email_address = get_email_addresses(self.tokens)
        self.get_dates()
        # filter ISO formatted dates out of the numbers list
        new_numbers = []
        for n in self.numbers:
            ok = True
            for d in self.dates:
                ds = d.isoformat(timespec="hours").replace("T00", "")
                if n == ds:
                    ok = False
            if ok:
                new_numbers.append(n)
        self.numbers = new_numbers

    def __str__(self):
        s = []
        s.append(
            "Word count: %-5d Filtered word count: %-5d Unique word count: %-5d"
            % (len(self.split_text), len(self.words), len(self.word_set))
        )
        if len(self.dates) > 0:
            s.append(
                "Dates found: %d    Common: %s Oldest: %s Newest: %s"
                % (
                    len(self.dates),
                    most_popular(self.dates, ignore_outliers=True)
                    .isoformat(timespec="hours")
                    .replace("T00", ""),
                    self.dates[0].isoformat(timespec="hours").replace("T00", ""),
                    self.dates[-1].isoformat(timespec="hours").replace("T00", ""),
                )
            )
        s.append(
            "Captialized count: %-5d Uppercase count: %-5d Numbers: %-5d"
            % (
                len(self.capitalized_words),
                len(self.uppercase_words),
                len(self.numbers),
            )
        )
        x = word_freq_str(self.words, up_to=5, style="flat")
        s.append("Top 5 words          : %s" % (x))
        x = word_freq_str(self.capitalized_words, up_to=5, style="flat")
        s.append("Top 5 capital words  : %s" % (x))
        x = word_freq_str(self.uppercase_words, up_to=5, style="flat")
        s.append("Top 5 uppercase words: %s" % (x))
        x = word_freq_str(self.numbers, up_to=5, style="flat")
        s.append("Top 5 numbers        : %s" % (x))
        x = word_freq_str(self.telephone_no, up_to=5, style="flat")
        s.append("Top 5 telephone no   : %s" % (x))
        x = word_freq_str(self.email_address, up_to=5, style="flat")
        s.append("Top 5 email address  : %s" % (x))
        s.append("".join("=" * 90))
        return "\n".join(s)

    def filter_text(self, text=None, ignore_numbers=False):
        s = []
        if text is not None:
            words = text
        else:
            words = self.split_text
        for word in words:
            if len(word) == 1 and word in [*string.punctuation, "•", "»"]:
                continue
            if len(word) > 0 and word.lower() not in self.filter:
                w = strip_punc(word, filter_chars="{ } [ ] ( ) | “ ” , • » ! ? * §")
                if not has_numbers(w):
                    w = strip_punc(
                        w, filter_chars=". - : ;", from_right=True, from_left=True
                    )
                if not (ignore_numbers and has_numbers(w)):
                    s.append(w)
        return s

    @property
    def best_date(self):
        if len(self.dates) > 0:
            best = most_popular(
                self.dates, ignore_outliers=False, ignore_no_winner=False
            )
            if best is not None:
                return best.isoformat(timespec="hours").replace("T00", "")
            new_dates = [str(d)[:7] for d in self.dates]
            date_dict = {nd: d for nd, d in zip(new_dates, self.dates)}
            best = most_popular(new_dates, ignore_outliers=False, ignore_no_winner=True)
            return date_dict[best].isoformat(timespec="hours").replace("T00", "")
        return None

    def get_dates(self, preferred_format=None):

        lines = self.raw_text.splitlines()
        dates = get_dates_from_text(lines, debug=self.debug)
        # if no dates are found, try a last ditch effort by feeding lines with
        # triple-wise words for candidates such as "July 21, 2019"
        if len(dates) < 4:
            if self.debug:
                print(
                    "Only %d candidate dates found, searching token list" % (len(dates))
                )
            for line in self.tokens:
                line = cleanup_date(line)
                dates.extend(get_dates_from_text([line], debug=self.debug))
        if len(dates) < 4:
            if self.debug:
                print("Only %d candidate dates found, searching 3-grams" % (len(dates)))
            for line in lines:
                line = cleanup_date(line, use_space=True)
                triples = n_grams(line, 3, as_list=False)
                if len(triples) > 0:
                    dates.extend(get_dates_from_text(triples, debug=self.debug))
        if len(dates) < 4:
            if self.debug:
                print("Only %d candidate dates found, searching 2-grams" % (len(dates)))
            for line in lines:
                line = cleanup_date(line, use_space=True)
                pairs = n_grams(line, 2, as_list=False)
                if len(pairs) > 0:
                    dates.extend(get_dates_from_text(pairs, debug=self.debug))
        if preferred_format is not None:
            return sorted(dates)
        self.dates = sorted(dates)
        if self.debug:
            for i, d in enumerate(self.dates):
                print(
                    "%d. %s" % (i + 1, d.isoformat(timespec="hours").replace("T00", ""))
                )
        return self.dates
