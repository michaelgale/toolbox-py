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
all_words_str = "abc def ghi jklmnop Important important ImPoRtAnT"


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
    x = are_words_in_word_list("important", all_words_str, case_sensitive=False)
    assert x
    x = are_words_in_word_list(["abc", "def"], all_words, case_sensitive=False)
    assert x
    x = are_words_in_word_list(["abc", "def"], all_words_str, case_sensitive=False)
    assert x
    x = are_words_in_word_list(["abc", "Def"], all_words, case_sensitive=True)
    assert not x
    x = are_words_in_word_list(["important", "Def"], all_words, case_sensitive=True)
    assert not x
    x = are_words_in_word_list(["important", "Def"], all_words, case_sensitive=False)
    assert x
    x = are_words_in_word_list("jk*", all_words, case_sensitive=True)
    assert x
    x = are_words_in_word_list("jk*", all_words_str, case_sensitive=True)
    assert x
    x = are_words_in_word_list("Jk*", all_words, case_sensitive=True)
    assert not x
    x = are_words_in_word_list("Jk*", all_words_str, case_sensitive=True)
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


def test_has_numbers():
    assert has_numbers("$53.09")
    assert has_numbers("K7L4G8")
    assert not has_numbers("DR.WHITE")
    assert has_numbers("DR.WHITE73")
    assert not has_numbers("Alice")
    assert not has_numbers("cat")


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
    v = parse_value(value_text, "footnote %t")
    assert v == "text"
    x = 13
    z = parse_value_into(x, value_text, "Total: %v")
    assert abs(z - 74.82) < 1e-3
    x = 15
    z = parse_value_into(x, value_text, "Other value: %v")
    assert z == 15
    y = parse_value(value_text, "Pays: %v %t")
    assert len(y) == 2
    assert abs(y[0] - 16.32) < 1e-3
    assert y[1] == "dollars"
    z = parse_value(value_text, "placeholder %t that %t contain")
    assert len(z) == 2
    assert z[0] == "text"
    assert z[1] == "could"
    z = parse_value(value_text, "placeholder %t that %t blah")
    assert z is None
    v = parse_value(value_text, "Pays: %v %*")
    assert len(v) == 2
    assert abs(v[0] - 16.32) < 1e-3
    assert v[1] == "dollars footnote text under the document"
    z = parse_value(value_text, "placeholder %t that %t contain", first=True)
    assert z is not None
    assert z == "text"
    z = parse_value(value_text, "placeholder %t that %t contain", last=True)
    assert z is not None
    assert z == "could"


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


def test_prov_state_lookup():
    x = CAN_PROVINCE_CODE["Ontario"]
    assert x == "ON"
    y = CAN_PROVINCE_NAME["AB"]
    assert y == "Alberta"
    x = US_STATE_CODE["Vermont"]
    assert x == "VT"
    y = US_STATE_NAME["FL"]
    assert y == "Florida"

    s1 = "Ontario alberta Onttario"
    s2 = replace_prov_state_names(s1)
    assert s2 == "ON alberta Onttario"

    s1 = "Ontario alberta Onttario"
    s2 = replace_prov_state_names(s1, case_sensitive=False)
    assert s2 == "ON AB Onttario"

    s1 = "Vermont florida"
    s2 = replace_prov_state_names(s1)
    assert s2 == "VT florida"

    s1 = "Vermont florida"
    s2 = replace_prov_state_names(s1, case_sensitive=False)
    assert s2 == "VT FL"

    s1 = "blah blah ON FL vt"
    s2 = replace_prov_state_codes(s1)
    assert s2 == "blah blah Ontario Florida vt"


def test_country_lookup():
    s1 = "Canada, Ontario"
    s2 = replace_country_names(s1)
    assert s2 == "CA, Ontario"

    s1 = "blah blah canada United Kingdom"
    s2 = replace_country_names(s1)
    assert s2 == "blah blah CA GB"

    s1 = "blah blah CA blah DE"
    s2 = replace_country_codes(s1)
    assert s2 == "blah blah Canada blah Germany"


def almost_same(x, y):
    if any([abs(x[i] - y[i]) > 2e-3 for i in range(3)]):
        return False
    return True


def test_colours():
    c1 = rgb_from_hex("#000000")
    assert c1 == (0.0, 0.0, 0.0)
    c2 = rgb_from_hex("#FFFFFF")
    assert c2 == (1.0, 1.0, 1.0)
    c3 = rgb_from_hex("FFFFFF")
    assert c3 == (1.0, 1.0, 1.0)
    c2 = rgb_from_hex("#FFFFFF", as_uint8=True)
    assert c2 == (255, 255, 255)
    nc1 = colour_name_from_tuple((165, 42, 42))
    assert nc1 == "brown"
    nc2 = colour_name_from_tuple((46, 46, 46))
    assert nc2 == "gray18"
    c1 = colour_from_name("DarkOrchid")
    assert c1 == (153, 50, 204)
    c2 = colour_name_from_tuple((205, 38, 38))
    assert c2 == "firebrick3"
    c2 = colour_name_from_tuple((205, 38, 37))
    assert c2 == "firebrick3"
    c2 = colour_name_from_tuple((202, 38, 37))
    assert c2 == "firebrick3"

    cs = safe_colour_tuple("#808080")
    assert almost_same(cs, (0.5, 0.5, 0.5))
    cs = safe_colour_tuple("gray18")
    assert almost_same(cs, (0.18, 0.18, 0.18))
    cs = safe_colour_tuple((205, 40, 80))
    assert almost_same(cs, (0.803, 0.156, 0.313))
    cs = safe_colour_tuple(15)
    assert almost_same(cs, (1, 1, 1))
    cs = safe_colour_tuple(71, as_float=False)
    assert almost_same(cs, (int("a0", 16), int("a5", 16), int("a9", 16)))

    ch = rgb_to_hex((0, 128, 64))
    assert ch == "#008040"
    ch = rgb_to_hex((0.5, 0, 1.0))
    assert ch == "#7F00FF"

    cvs = [
        ((255, 0, 0), (0, 255, 255)),
        ((0, 255, 0), (60, 255, 255)),
        ((0, 0, 255), (120, 255, 255)),
        ((0, 0, 128), (120, 255, 128)),
        ((128, 128, 128), (0, 0, 128)),
        ((0.5, 0.5, 0.5), (0, 0, 128)),
        ("#00FF00", (60, 255, 255)),
    ]
    for rgb, hsv in cvs:
        cv = rgb_to_hsv(rgb)
        assert cv == hsv

    for rgb, hsv in cvs:
        cv = hsv_to_rgb(hsv)
        srgb = safe_colour_tuple(rgb, as_float=False)
        assert cv == srgb

    assert rgb_to_hsv(15) == (0, 0, 255)
    assert rgb_to_hsv(4) == (3, 244, 201)


def test_clamp():
    x = clamp_value(3, 1, 5)
    assert x == 3
    x = clamp_value(-3, 1, 5)
    assert x == 1
    x = clamp_value(10, 1, 5)
    assert x == 5
    x = clamp_value(3, 5, 1)
    assert x == 5
    x = clamp_value(10, 5, 1)
    assert x == 5


def test_eng_units():
    r = []
    for x in [800e-9, 1.2e-6, -3, 2.5, 11.239, 150e3, 2.2e6, 80e9]:
        s = eng_units(x, units="B", unitary=True, sigfigs=4)
        r.append(s)
    rs = [
        "800.0 nB",
        "1.2 uB",
        "-3 B",
        "2.5 B",
        "11.23 B",
        "150.0 kB",
        "2.2 MB",
        "80.0 GB",
    ]
    for v, vr in zip(r, rs):
        assert v == vr
    r = []
    for x in [800e-9, 1.2e-6, -3, 2.5, 11.239, 150e3, 2.2e6, 80e9]:
        s = eng_units(x, units="s", unitsep=False)
        r.append(s)
    rs = ["800.0ns", "1.2us", "-3.0s", "2.5s", "11.239s", "150.0ks", "2.2Ms", "80.0Gs"]
    for v, vr in zip(r, rs):
        assert v == vr


def test_month_day_num():
    months = "jan January Mar Ma MAY dec"
    results = [1, 1, 3, 0, 5, 12]
    for m, r in zip(months.split(), results):
        assert month_num(m) == r

    days = "mon sun Fri WED saturday stat"
    results = [2, 1, 6, 4, 7, 0]
    for m, r in zip(days.split(), results):
        assert day_week_num(m) == r
    results = [1, 7, 5, 3, 6, 0]
    for m, r in zip(days.split(), results):
        assert day_week_num(m, sunday_first=False) == r


def test_clean_filename():
    fns = [
        "a;ks*fjhsl-3.pdf",
        "File = 3/9;.doc",
        "-=abs=-93.zip",
    ]
    clean = [
        "a_ks_fjhsl-3.pdf",
        "File_=_3_9.doc",
        "-=abs=-93.zip",
    ]
    for f, c in zip(fns, clean):
        fc = clean_filename(f, replacement="_", no_spaces=True)
        assert fc == c


def test_word_split():
    t1 = "word0asfgja1Word1sdfasdlkas ;fdgj sdf gj;lkdsf2 wordals 2gjWORDksldhf3word 3alskdjfla;sd"
    s1 = word_split(t1, word_list="word als", case_sensitive=True)
    assert (
        s1
        == "word 0asfgja1Word1sdfasdlkas ;fdgj sdf gj;lkdsf2 word als 2gjWORDksldhf3 word 3 als kdjfla;sd"
    )
    s2 = word_split(t1, word_list="word als", case_sensitive=False)
    assert (
        s2
        == "word 0asfgja1 Word 1sdfasdlkas ;fdgj sdf gj;lkdsf2 word als 2gj WORD ksldhf3 word 3 als kdjfla;sd"
    )
