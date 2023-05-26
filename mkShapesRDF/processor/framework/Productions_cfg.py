# flake8: noqa E265, E266
# IMPORTANT: all paths are relative to the mkShapesRDF/mkShapesRDF/processor/framework folder
Productions = {
    #################################### nAODv9 UL DATA  ##############################################
    # -------- 2016 DATA UL2016 nAODv9: Full2016v9
    "Run2016_UL2016_nAODv9_HIPM_Full2016v9": {
        "isData": True,
        "jsonFile": "../data/certification/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
        "samples": "framework/samples/Run2016_UL2016_HIPM_nAODv9.py",
        "cmssw": "Full2016v9HIPM",
        "year": "2016",
    },
    "Run2016_UL2016_nAODv9_noHIPM_Full2016v9": {
        "isData": True,
        "jsonFile": "../data/certification/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
        "samples": "framework/samples/Run2016_UL2016_noHIPM_nAODv9.py",
        "cmssw": "Full2016v9noHIPM",
        "year": "2016",
    },
    # -------- 2017 DATA UL2017 nAODv9: Full2017v9
    "Run2017_UL2017_nAODv9_Full2017v9": {
        "isData": True,
        "jsonFile": "../data/certification/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt",
        "samples": "framework/samples/Run2017_UL2017_nAODv9.py",
        "cmssw": "Full2017v9",
        "year": "2017",
    },
    # -------- 2018 DATA UL2018 nAODv9: Full2018v9
    "Run2018_UL2018_nAODv9_Full2018v9": {
        "isData": True,
        "jsonFile": "../data/certification/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt",
        "samples": "../framework/samples/Run2018_UL2018_nAODv9.py",
        "cmssw": "Full2018v9",
        "year": "2018",
    },
    #################################### nAODv9 MC ##############################################
    # -------- 2016 MC 106X nAODv8: Full2016v8
    "Summer20UL16_106x_nAODv9_HIPM_Full2016v9": {
        "isData": False,
        "samples": "../framework/samples/Summer20UL16_106x_HIPM_nAODv9.py",
        "cmssw": "Full2016v9HIPM",
        "year": "2016",
        #'JESGT'   : 'Summer16_07Aug2017_V11_MC' ,
        "xsFile": "../framework/samples/samplesCrossSections_UL.py",
        "YRver": ["YR4", "13TeV"],
    },
    "Summer20UL16_106x_nAODv9_noHIPM_Full2016v9": {
        "isData": False,
        "samples": "../framework/samples/Summer20UL16_106x_noHIPM_nAODv9.py",
        "cmssw": "Full2016v9noHIPM",
        "year": "2016",
        #'JESGT'   : 'Summer16_07Aug2017_V11_MC' ,
        "xsFile": "../framework/samples/samplesCrossSections_UL.py",
        "YRver": ["YR4", "13TeV"],
    },
    # -------- 2017 MC UL
    "Summer20UL17_106x_nAODv9_Full2017v9": {
        "isData": False,
        "samples": "../framework/samples/Summer20UL17_106x_nAODv9.py",
        "cmssw": "Full2017v9",
        "year": "2017",
        #                      'JESGT'   : 'Fall17_17Nov2017_V32_MC' ,
        "xsFile": "../framework/samples/samplesCrossSections_UL.py",
        "YRver": ["YR4", "13TeV"],
    },
    # -------- 2018 MC UL
    "Summer20UL18_106x_nAODv9_Full2018v9": {
        "isData": False,
        "samples": "../framework/samples/Summer20UL18_106x_nAODv9.py",
        "cmssw": "Full2018v9",
        "year": "2018",
        #                      'JESGT'   : 'Autumn18_V19_MC',
        "xsFile": "../framework/samples/samplesCrossSections_UL.py",
        "YRver": ["YR4", "13TeV"],
    },
}
