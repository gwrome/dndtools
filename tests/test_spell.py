from spell import Spell


def test_higher_levels(raw_spells):
    s = Spell(raw_spells['fireball'], from_tools=True)
    assert "At Higher Levels" in s.description


def test_special_cast_time(raw_spells):
    s = Spell(raw_spells['hellish_rebuke'], from_tools=True)
    assert '1 reaction which' in s.cast_time


def test_special_duration(raw_spells):
    s = Spell(raw_spells['astral_projection'], from_tools=True)
    assert 'Special' in s.duration


def test_special_range(raw_spells):
    s = Spell(raw_spells['dream'], from_tools=True)
    assert 'Special' in s.range


def test_nonnumeric_range(raw_spells):
    s = Spell(raw_spells['shocking_grasp'], from_tools=True)
    assert 'Touch' in s.range


def test_no_components(raw_spells):
    s = Spell(raw_spells['psionic_power'], from_tools=True)
    assert 'None' in s.components


def test_list(raw_spells):
    s = Spell(raw_spells['conjure_woodlands'], from_tools=True)
    assert '*' in s.description


def test_concentration(raw_spells):
    s = Spell(raw_spells['conjure_woodlands'], from_tools=True)
    assert 'concentration' in s.duration


def test_entry_headers(raw_spells):
    s = Spell(raw_spells['control_winds'], from_tools=True)
    assert '*Gusts.*' in s.description and '*Downdraft.*' in s.description

def test_ritual(raw_spells):
    s = Spell(raw_spells['identify'], from_tools=True)
    assert s.ritual is True
    t = Spell(raw_spells['control_winds'], from_tools=True)
    assert t.ritual is False


def test_ritual(raw_spells):
    s = Spell(raw_spells['identify'], from_tools=True)
    assert 'SRD p. 123' in s.source
