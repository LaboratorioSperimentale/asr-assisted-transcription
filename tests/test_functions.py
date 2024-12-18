import asr_analysis.process_text as pt

def test_removespaces():
    assert pt.remove_spaces("  ciao") == (1, "ciao")
    assert pt.remove_spaces("ciao  ") == (1, "ciao")
    assert pt.remove_spaces("ciao   ") == (1, "ciao")
    assert pt.remove_spaces("ci  ao  ") == (2, "ci ao")

def test_meta_tag():
    assert pt.meta_tag("(.) ciao") == "{PAUSE} ciao"
    assert pt.meta_tag("ciao ((bla bla)) ciao") == "ciao {bla_bla} ciao"

def test_replace_po():
    assert pt.replace_po("pò") == (1, "po'")

def test_replace_che():
    assert pt.replace_che("perchè") == (1, "perché")
    assert pt.replace_che("finchè") == (1, "finché")

def test_pauses():
    assert pt.remove_pauses("(.) ciao") == (1, "ciao")
    assert pt.remove_pauses("ciao (.)") == (1, "ciao")
    assert pt.remove_pauses("(.) ciao (.)") == (2, "ciao")
    assert pt.remove_pauses("ciao (.) ciao") == (0, "ciao (.) ciao")
    assert pt.remove_pauses("(a) casa") == (0, "(a) casa")
    assert pt.remove_pauses("[(.) casa") == (1, "[casa")
    assert pt.remove_pauses("casa (.) >") == (1, "casa>")

def test_check_even_dots():
    assert pt.check_even_dots("°ciao°") == ("Balanced")
    assert pt.check_even_dots("°ciao") == ("Not balanced")

def test_check_normal_parentheses():
    assert pt.check_normal_parentheses("(ciao)", "(", ")") == ("Balanced")
    assert pt.check_normal_parentheses("(ciao", "(", ")") == ("Not balanced")
    assert pt.check_normal_parentheses("[ciao]", "[", "]") == ("Balanced")
    assert pt.check_normal_parentheses("ciao]", "[", "]") == ("Not balanced")

def test_check_angular_parentheses():
    assert pt.check_angular_parentheses("<ciao>") == ("Balanced")
    assert pt.check_angular_parentheses(">ciao<") == ("Balanced")
    assert pt.check_angular_parentheses("<ciao") == ("Not balanced")
    assert pt.check_angular_parentheses("ciao>") == ("Not balanced")
    assert pt.check_angular_parentheses("<<ciao>>") == ("Not balanced")
    assert pt.check_angular_parentheses("bla <slow> followed by >fast<") == ("Balanced")
    assert pt.check_angular_parentheses("bla >fast< followed by <slow>") == ("Balanced")

def test_check_intonation_patterns(): # TODO
    assert pt.check_intonation_patterns("ciao.") == ("discendente")
    assert pt.check_intonation_patterns("ciao,") == ("debolmente_ascendente")
    assert pt.check_intonation_patterns("ciao?") == ("ascendente")
    assert pt.check_intonation_patterns("ciao:") == ("suono_prolungato")
    assert pt.check_intonation_patterns("cia-") == ("parola_interrotta")