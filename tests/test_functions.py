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
    assert pt.replace_pò("po") 

def test_replace_che():
    assert pt.replace_che("perchè") == (1, "perché")
    assert pt.replace_che("finchè") == (1, "finché")

def test_pauses():
    assert pt.remove_pauses("(.) ciao") == (1, "ciao")
    assert pt.remove_pauses("ciao (.)") == (1, "ciao")
    assert pt.remove_pauses("(.) ciao (.)") == (2, "ciao")
    assert pt.remove_pauses("ciao (.) ciao") == (0, "ciao (.) ciao")
    assert pt.remove_pauses("(a) casa") == (0, "(a) casa")

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