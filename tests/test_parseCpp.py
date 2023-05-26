import pytest
from mkShapesRDF.lib.parseCpp import ParseCpp


def test_parse():
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
    s = "Lepton_pt[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    a = ParseCpp.parse(s)
    assert ParseCpp.format(a) == s


def test_replace():
    s = "Lepton_pt[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    a = ParseCpp.parse(s)
    assert (
        ParseCpp.format(ParseCpp.replace(a, "Lepton_pt", "Lepton_pt__elept_up"))
        == "Lepton_pt__elept_up[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    )


def test_noreplace():
    s = "Lepton_pt__mupt_up[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0"
    a = ParseCpp.parse(s)
    assert ParseCpp.format(ParseCpp.replace(a, "Lepton_pt", "Lepton_pt__elept_up")) == s


def test_listOfVariables():
    s = "Lepton_pt[0]>0 && Lepton_phi[1]<2*3.1415 && CleanJet_jetIdx[0]>=0 && CleanJet_jetIdx[0] < 10"
    a = ParseCpp.parse(s)
    assert ParseCpp.listOfVariables(a) == ["CleanJet_jetIdx", "Lepton_phi", "Lepton_pt"]
