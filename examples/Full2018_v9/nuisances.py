# merge cuts
_mergedCuts = []
for cut in list(cuts.keys()):
    __cutExpr = ""
    if type(cuts[cut]) == dict:
        __cutExpr = cuts[cut]["expr"]
        for cat in list(cuts[cut]["categories"].keys()):
            _mergedCuts.append(cut + "_" + cat)
    elif type(cuts[cut]) == str:
        _mergedCuts.append(cut)

cuts2j = _mergedCuts

nuisances = {}

nuisances["lumi_Uncorrelated"] = {
    "name": "lumi_13TeV_2018",
    "type": "lnN",
    "samples": dict(
        (skey, "1.015") for skey in mc if skey not in ["WW", "top", "dyll", "dytt"]
    ),
}

nuisances["lumi_XYFact"] = {
    "name": "lumi_13TeV_XYFact",
    "type": "lnN",
    "samples": dict(
        (skey, "1.02") for skey in mc if skey not in ["WW", "top", "dyll", "dytt"]
    ),
}

nuisances["lumi_LScale"] = {
    "name": "lumi_13TeV_LSCale",
    "type": "lnN",
    "samples": dict(
        (skey, "1.002") for skey in mc if skey not in ["WW", "top", "dyll", "dytt"]
    ),
}

nuisances["lumi_CurrCalib"] = {
    "name": "lumi_13TeV_CurrCalib",
    "type": "lnN",
    "samples": dict(
        (skey, "1.002") for skey in mc if skey not in ["WW", "top", "dyll", "dytt"]
    ),
}

#### FAKES

nuisances["fake_syst_e"] = {
    "name": "CMS_fake_syst_e",
    "type": "lnN",
    "samples": {"Fake_e": "1.3"},
    #'cutspost': lambda self, cuts: [cut for cut in cuts if 'mm' not in cut],
}

nuisances["fake_syst_m"] = {
    "name": "CMS_fake_syst_m",
    "type": "lnN",
    "samples": {"Fake_m": "1.3"},
    #'cutspost': lambda self, cuts: [cut for cut in cuts if 'ee' not in cut],
}

nuisances["fake_ele"] = {
    "name": "CMS_fake_e_2018",
    "kind": "weight",
    "type": "shape",
    "samples": {
        "Fake": ["fakeWEleUp", "fakeWEleDown"],
    },
}

nuisances["fake_ele_stat"] = {
    "name": "CMS_fake_stat_e_2018",
    "kind": "weight",
    "type": "shape",
    "samples": {"Fake": ["fakeWStatEleUp", "fakeWStatEleDown"]},
}

nuisances["fake_mu"] = {
    "name": "CMS_fake_m_2018",
    "kind": "weight",
    "type": "shape",
    "samples": {
        "Fake": ["fakeWMuUp", "fakeWMuDown"],
    },
}

nuisances["fake_mu_stat"] = {
    "name": "CMS_fake_stat_m_2018",
    "kind": "weight",
    "type": "shape",
    "samples": {
        "Fake": ["fakeWStatMuUp", "fakeWStatMuDown"],
    },
}

### B-tagger
for shift in [
    "jes",
    "lf",
    "hf",
    "hfstats1",
    "hfstats2",
    "lfstats1",
    "lfstats2",
    "cferr1",
    "cferr2",
]:
    btag_syst = ["(btagSF%sup)/(btagSF)" % shift, "(btagSF%sdown)/(btagSF)" % shift]

    name = "CMS_btag_%s" % shift
    if "stats" in shift:
        name += "_2018"

    nuisances["btag_shape_%s" % shift] = {
        "name": name,
        "kind": "weight",
        "type": "shape",
        "samples": dict((skey, btag_syst) for skey in mc),
    }

##### Trigger Efficiency

trig_syst = [
    "((TriggerEffWeight_2l_u)/(TriggerEffWeight_2l))*(TriggerEffWeight_2l>0.02) + (TriggerEffWeight_2l<=0.02)",
    "(TriggerEffWeight_2l_d)/(TriggerEffWeight_2l)",
]

nuisances["trigg"] = {
    "name": "CMS_eff_hwwtrigger_2018",
    "kind": "weight",
    "type": "shape",
    "samples": dict((skey, trig_syst) for skey in mc),
}

##### Electron Efficiency and energy scale

nuisances["eff_e"] = {
    "name": "CMS_eff_e_2018",
    "kind": "weight",
    "type": "shape",
    "samples": dict((skey, ["SFweightEleUp", "SFweightEleDown"]) for skey in mc),
}

nuisances["electronpt"] = {
    "name": "CMS_scale_e_2018",
    "kind": "suffix",
    "type": "shape",
    "mapUp": "ElepTup",
    "mapDown": "ElepTdo",
    "samples": dict((skey, ["1", "1"]) for skey in mc),
    "folderUp": makeMCDirectory("ElepTup_suffix"),
    "folderDown": makeMCDirectory("ElepTdo_suffix"),
    "AsLnN": "1",
}

##### Muon Efficiency and energy scale

nuisances["eff_m"] = {
    "name": "CMS_eff_m_2018",
    "kind": "weight",
    "type": "shape",
    "samples": dict((skey, ["SFweightMuUp", "SFweightMuDown"]) for skey in mc),
}

nuisances["muonpt"] = {
    "name": "CMS_scale_m_2018",
    "kind": "suffix",
    "type": "shape",
    "mapUp": "MupTup",
    "mapDown": "MupTdo",
    "samples": dict((skey, ["1", "1"]) for skey in mc),
    "folderUp": makeMCDirectory("MupTup_suffix"),
    "folderDown": makeMCDirectory("MupTdo_suffix"),
    "AsLnN": "1",
}

# PDF
pdf_variations = [
    "LHEPdfWeight[%d]" % i for i in range(1, 101)
]  # Float_t LHE pdf variation weights (w_var / w_nominal) for LHA IDs  320901 - 321000
nuisances["pdf_DY"] = {
    "name": "CMS_hww_pdf_DY",
    "kind": "weight_rms",
    "type": "shape",
    "AsLnN": "0",
    "samples": {
        "dyll": pdf_variations,
    },
}

variations = [
    "LHEScaleWeight[0]",
    "LHEScaleWeight[1]",
    "LHEScaleWeight[3]",
    "LHEScaleWeight[nLHEScaleWeight-4]",
    "LHEScaleWeight[nLHEScaleWeight-2]",
    "LHEScaleWeight[nLHEScaleWeight-1]",
]

nuisances["QCDscale_V"] = {
    "name": "QCDscale_V",
    "skipCMS": 1,
    "kind": "weight_envelope",
    "type": "shape",
    "samples": {"dyll": variations},
    "AsLnN": "0",
}
##### MET energy scale

nuisances["met"] = {
    "name": "CMS_scale_met_2018",
    "kind": "suffix",
    "type": "shape",
    "mapUp": "METup",
    "mapDown": "METdo",
    "samples": dict((skey, ["1", "1"]) for skey in mc),
    "folderUp": makeMCDirectory("METup_suffix"),
    "folderDown": makeMCDirectory("METdo_suffix"),
    "AsLnN": "1",
}


autoStats = False
if autoStats:
    ## Use the following if you want to apply the automatic combine MC stat nuisances.
    nuisances["stat"] = {
        "type": "auto",
        "maxPoiss": "10",
        "includeSignal": "0",
        #  nuisance ['maxPoiss'] =  Number of threshold events for Poisson modelling
        #  nuisance ['includeSignal'] =  Include MC stat nuisances on signal processes (1=True, 0=False)
        "samples": {},
    }
