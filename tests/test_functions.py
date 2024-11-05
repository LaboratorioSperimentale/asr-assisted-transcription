import asr_analysis.process_text as pt

def test_removespaces():
    assert pt.remove_spaces("  ciao") == (1, "ciao")
    assert pt.remove_spaces("ciao  ") == (1, "ciao")
    assert pt.remove_spaces("ciao   ") == (1, "ciao")
    assert pt.remove_spaces("ci  ao  ") == (2, "ci ao")


def test_meta_tag():
    assert pt.meta_tag("(.) ciao") == "{PAUSE} ciao"
    assert pt.meta_tag("ciao ((bla bla)) ciao") == "ciao {bla_bla} ciao"

def test_replace_pò():
    assert pt.replace_pò("pò") 

def test_replace_perchè():
    assert pt.replace_perchè("perchè") 