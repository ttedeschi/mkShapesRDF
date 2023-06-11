import pytest
from mkShapesRDF.lib.parse_cpp import ParseCpp


def test_parse():
    """
    Test the parsing of a C++ expression
    """
    s = "Lepton_pt[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    a = ParseCpp.parse(s)
    assert a == [
        "Lepton_pt",
        "[",
        "0",
        "]",
        ">",
        "0",
        " ",
        "&&",
        " ",
        "Lepton_phi",
        "[",
        "1",
        "]",
        "<",
        "2",
        "*",
        "3",
        ".",
        "1415",
        " ",
        "&&",
        " ",
        "CleanJet_jetIdx",
        "[",
        "0",
        "]",
        ">",
        "=",
        "0",
    ]


def test_format():
    """
    Test the formatting of a C++ expression after the parsing. It should be the same as the original string.
    """
    s = "Lepton_pt[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    a = ParseCpp.parse(s)
    assert ParseCpp.format(a) == s


def test_replace():
    """
    Test the replacement of a variable in a C++ expression. First parse, then replace, finally format.
    """
    s = "Lepton_pt[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    a = ParseCpp.parse(s)
    assert (
        ParseCpp.format(ParseCpp.replace(a, "Lepton_pt", "Lepton_pt__elept_up"))
        == "Lepton_pt__elept_up[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    )


def test_noreplace():
    """
    Test the replacement of a variable not present in a C++ expression. First parse, then replace, finally format.
    It should be the same as the original string.
    """

    s = "Lepton_pt__mupt_up[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    a = ParseCpp.parse(s)
    assert ParseCpp.format(ParseCpp.replace(a, "Lepton_pt", "Lepton_pt__elept_up")) == s


def test_listOfVariables():
    """
    Test the list of variables in a C++ expression. It removes all separator and returns the list of variables.
    """
    s = "Lepton_pt[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0 && CleanJet_jetIdx[0] < 10"
    a = ParseCpp.parse(s)
    assert ParseCpp.listOfVariables(a) == ["CleanJet_jetIdx", "Lepton_phi", "Lepton_pt"]
