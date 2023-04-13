# my modules
from toolbox import *

test_text = """
Date: Feb 28, 2011
this is placeholder text which may or may not contain
email addresses such as michael.gale@me.com or info@abc.com
but should not match things like blah@google or 
123@*$@.123
Date: January 17, 2019
but could match single line addresses like
admin@eleceng.queensu.ca
this is placeholder text which may or may not contain
2022-10-09 is a date Feb 28, 2011
This is another date 2023/11/02 
and Feb 20 is a good date
this is placeholder text which may or may not contain
telephone numbers such as 613-295-1899 or (613) 207-1452
but should not match things like +44 01983 336782 or 
204-293-293 or 1-270-1999
but could match single line numbers like
613 863-2541 but not 800-GET-MILK or 876-200-S0AP
Max Headroom PYTHON Python ALL-CAPS MyCAPS
"""


def test_filter():
    t1 = TextProc(text=test_text)
    assert "2022-10-09" == t1.best_date
    assert len(t1.capitalized_words) == 9
    assert len(t1.uppercase_words) == 1
    assert len(t1.numbers) == 16
    assert len(t1.words) == 57
    assert len(t1.word_set) == 27
    assert len(t1.split_text) == 122
