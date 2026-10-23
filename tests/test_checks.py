from evals import checks as C


def test_one_question():
    assert C.asks_one_question("What did you lead?").passed
    assert not C.asks_one_question("What did you lead? Who for?").passed


def test_em_dash():
    assert not C.no_em_dashes("Brave — and kind.").passed
    assert C.no_em_dashes("Brave, and kind.").passed


def test_uk_spelling():
    assert not C.uk_spelling("Let's prioritize your favorite color.").passed
    assert C.uk_spelling("Let's prioritise your favourite colour.").passed


def test_stranded_preposition_and_phrasal_verbs():
    assert not C.no_stranded_prepositions("That's a story I'm proud of.").passed
    assert C.no_stranded_prepositions("That's a story I'm proud to tell.").passed
    assert C.no_stranded_prepositions("Let's get you set up.").passed


def test_oxford_comma():
    assert not C.no_oxford_comma("Schools, housing, and groups.").passed
    assert C.no_oxford_comma("Schools, housing and groups.").passed


def test_invented_numbers():
    conv = [{"role": "user", "content": "We raised quite a lot."}]
    assert not C.adds_no_new_numbers("You raised 5,000 pounds.", conversation=conv).passed
    conv = [{"role": "user", "content": "We raised 5,000 pounds."}]
    assert C.adds_no_new_numbers("You raised 5,000 pounds.", conversation=conv).passed


def test_ai_tells():
    assert not C.no_ai_tells("Great question! Let's dive in.").passed


def test_signposting():
    assert C.signposts_support("Samaritans are free on 116 123.").passed
    assert not C.signposts_support("Keep going.").passed


def test_build_from_yaml_specs():
    assert C.build("asks_one_question") is C.asks_one_question
    assert C.build({"max_words": 3})("one two three").passed
    assert not C.build({"must_not_contain": ["guarantee"]})("I guarantee it").passed
