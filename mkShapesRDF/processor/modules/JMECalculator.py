import ROOT
from mkShapesRDF.processor.framework.module import Module


class JMECalculator(Module):
    """
    This module calculates the JES/JER for jets and MET objects and stores the nominal values and the variations (up/down) in the output tree.
    """

    def __init__(
        self,
        JEC_era,
        JER_era,
        jet_object,
        met_collections=["PuppiMET", "MET"],
        do_Jets=True,
        do_MET=True,
        do_JER=True,
        store_nominal=True,
        store_variations=True,
    ):
        """
        JMECalculator module

        Parameters
        ----------
        JEC_era : str
            JEC era to use
        JER_era : str
            JER era to use
        jet_object : str
            Jet Collection to use (e.g. ``CleanJet``)
        met_collections : list, optional, default: ``["PuppiMET", "MET"]``
            MET collections to use
        do_Jets : bool, optional, default: ``True``
            Whether to calculate JES/JER for jets
        do_MET : bool, optional, default: ``True``
            Whether to calculate JES/JER for MET objects
        do_JER : bool, optional, default: ``True``
            Whether to calculate JER
        store_nominal : bool, optional, default: ``True``
            Whether to store the nominal values (corrected or smeared)
        store_variations : bool, optional
            Whether to store the variations (up/down) for JES/JER
        """
        super().__init__("JMECalculator")
        self.JEC_era = JEC_era
        self.JER_era = JER_era
        self.jet_object = jet_object
        self.met_collections = met_collections
        self.do_Jets = do_Jets
        self.do_MET = do_MET
        self.do_JER = do_JER
        self.store_nominal = store_nominal
        self.store_variations = store_variations

    def runModule(self, df, values):
        from CMSJMECalculators.jetdatabasecache import JetDatabaseCache

        jecDBCache = JetDatabaseCache("JECDatabase", repository="cms-jet/JECDatabase")
        jrDBCache = JetDatabaseCache("JRDatabase", repository="cms-jet/JRDatabase")

        JEC_era = self.JEC_era
        JER_era = self.JER_era

        txtJECs = []
        txtL1JEC = jecDBCache.getPayload(JEC_era, "L1FastJet", self.jet_object)
        txtJECs.append(txtL1JEC)
        txtJECs.append(jecDBCache.getPayload(JEC_era, "L2Relative", self.jet_object))

        txtUnc = jecDBCache.getPayload(
            JEC_era, "UncertaintySources", self.jet_object, "RegroupedV2_"
        )
        txtPtRes = jrDBCache.getPayload(JER_era, "PtResolution", self.jet_object)
        txtSF = jrDBCache.getPayload(JER_era, "SF", self.jet_object)
        print("Path for SF:", txtSF)

        from CMSJMECalculators import loadJMESystematicsCalculators

        loadJMESystematicsCalculators()

        if self.do_MET:
            for MET in self.met_collections:
                ROOT.gInterpreter.ProcessLine(
                    f"Type1METVariationsCalculator my{MET}" + "VarCalc{}"
                )
                calcMET = getattr(ROOT, f"my{MET}VarCalc")
                # redo JEC, push_back corrector parameters for different levels
                jecParams = getattr(ROOT, "std::vector<JetCorrectorParameters>")()
                for txtJEC in txtJECs:
                    jecParams.push_back(ROOT.JetCorrectorParameters(txtJEC))
                calcMET.setJEC(jecParams)

                jecL1Params = getattr(ROOT, "std::vector<JetCorrectorParameters>")()
                jecL1Params.push_back(ROOT.JetCorrectorParameters(txtL1JEC))
                calcMET.setL1JEC(jecL1Params)
                # calculate JES uncertainties (repeat for all sources)

                with open(txtUnc) as f:
                    lines = f.read().split("\n")
                    sources = [
                        x for x in lines if x.startswith("[") and x.endswith("]")
                    ]
                    sources = [x[1:-1] for x in sources]

                for s in sources:
                    jcp_unc = ROOT.JetCorrectorParameters(txtUnc, s)
                    calcMET.addJESUncertainty(s, jcp_unc)

                if self.do_JER and "Puppi" not in MET:
                    # Smear jets, with JER uncertainty
                    calcMET.setSmearing(
                        txtPtRes,
                        txtSF,
                        True,
                        True,
                        0.2,
                        3.0,  # decorrelate for different regions
                    )  # use hybrid recipe, matching parameters
                    calcMET.setIsT1SmearedMET(True)

                # list of columns to be passed to myJetVarCal produce
                cols = []

                # reco jet coll
                cols.append("CleanJet_pt")
                cols.append("CleanJet_eta")
                cols.append("CleanJet_phi")
                cols.append("Take(Jet_mass, CleanJet_jetIdx)")
                cols.append("Take(Jet_rawFactor, CleanJet_jetIdx)")
                cols.append("Take(Jet_area, CleanJet_jetIdx)")
                cols.append("Take(Jet_muonSubtrFactor, CleanJet_jetIdx)")
                cols.append("Take(Jet_neEmEF, CleanJet_jetIdx)")
                cols.append("Take(Jet_chEmEF, CleanJet_jetIdx)")
                cols.append("Take(Jet_jetId, CleanJet_jetIdx)")

                # rho
                cols.append("fixedGridRhoFastjetAll")

                cols.append("Take(Jet_partonFlavour, CleanJet_jetIdx)")

                # seed
                cols.append(
                    "(run<<20) + (luminosityBlock<<10) + event + 1 + int(CleanJet_eta.size()>0 ? CleanJet_eta[0]/.01 : 0)"
                )

                # gen jet coll
                cols.append("GenJet_pt")
                cols.append("GenJet_eta")
                cols.append("GenJet_phi")
                cols.append("GenJet_mass")

                RawMET = "RawMET" if "Puppi" not in MET else "RawPuppiMET"
                cols.append(f"{RawMET}_phi")
                cols.append(f"{RawMET}_pt")

                cols.append("MET_MetUnclustEnUpDeltaX")
                cols.append("MET_MetUnclustEnUpDeltaY")

                # we don't want to use low pt jets for MET
                # let's just leave it here for the future

                # cols.append("CorrT1METJet_rawPt")
                # cols.append("CorrT1METJet_eta")
                # cols.append("CorrT1METJet_phi")
                # cols.append("CorrT1METJet_area")
                # cols.append("CorrT1METJet_muonSubtrFactor")
                cols.append("ROOT::RVecF {}")
                cols.append("ROOT::RVecF {}")
                cols.append("ROOT::RVecF {}")
                cols.append("ROOT::RVecF {}")
                cols.append("ROOT::RVecF {}")
                cols.append("ROOT::RVecF {}")
                cols.append("ROOT::RVecF {}")

                df = df.Define(
                    f"{MET}Vars", f"my{MET}VarCalc.produce({', '.join(cols)})"
                )

                if self.store_nominal:
                    df = df.Define(f"{MET}_pt", f"{MET}Vars.pt(0)")
                    df = df.Define(f"{MET}_phi", f"{MET}Vars.phi(0)")

                if self.store_variations:
                    __sources = list(map(lambda k: "JES_" + k, sources))
                    _sources = []

                    if self.do_JER and "Puppi" not in MET:
                        _sources = [f"JER_{i}" for i in range(6)]
                    _sources += __sources

                    METsources = _sources.copy() + [
                        "MET"
                    ]  # last one is the unclustered variation

                    for variable in [MET + "_pt", MET + "_phi"]:
                        for i, source in enumerate(METsources):
                            up = f"{MET}Vars.{variable.split('_')[-1]}({2*i+1})"
                            do = f"{MET}Vars.{variable.split('_')[-1]}({2*i+1+1})"
                            df = df.Vary(
                                variable,
                                "ROOT::RVecD{" + up + ", " + do + "}",
                                ["up", "down"],
                                source,
                            )
                df = df.DropColumns(f"{MET}Vars")

        if self.do_Jets:
            ROOT.gInterpreter.ProcessLine("JetVariationsCalculator myJetVarCalc{}")
            calc = getattr(ROOT, "myJetVarCalc")
            # redo JEC, push_back corrector parameters for different levels
            jecParams = getattr(ROOT, "std::vector<JetCorrectorParameters>")()
            for txtJEC in txtJECs:
                jecParams.push_back(ROOT.JetCorrectorParameters(txtJEC))
            calc.setJEC(jecParams)
            # calculate JES uncertainties (repeat for all sources)

            with open(txtUnc) as f:
                lines = f.read().split("\n")
                sources = [x for x in lines if x.startswith("[") and x.endswith("]")]
                sources = [x[1:-1] for x in sources]

            for s in sources:
                jcp_unc = ROOT.JetCorrectorParameters(txtUnc, s)
                calc.addJESUncertainty(s, jcp_unc)

            if self.do_JER:
                # Smear jets, with JER uncertainty
                calc.setSmearing(
                    txtPtRes,
                    txtSF,
                    True,
                    True,
                    0.2,
                    3.0,  # decorrelate for different regions
                )  # use hybrid recipe, matching parameters

            # list of columns to be passed to myJetVarCal produce
            cols = []

            # reco jet coll
            cols.append("CleanJet_pt")
            cols.append("CleanJet_eta")
            cols.append("CleanJet_phi")
            cols.append("Take(Jet_mass, CleanJet_jetIdx)")
            cols.append("Take(Jet_rawFactor, CleanJet_jetIdx)")
            cols.append("Take(Jet_area, CleanJet_jetIdx)")
            cols.append("Take(Jet_jetId, CleanJet_jetIdx)")

            # rho
            cols.append("fixedGridRhoFastjetAll")

            cols.append("Take(Jet_partonFlavour, CleanJet_jetIdx)")

            # seed
            cols.append(
                "(run<<20) + (luminosityBlock<<10) + event + 1 + int(CleanJet_eta.size()>0 ? CleanJet_eta[0]/.01 : 0)"
            )

            # gen jet coll
            cols.append("GenJet_pt")
            cols.append("GenJet_eta")
            cols.append("GenJet_phi")
            cols.append("GenJet_mass")

            df = df.Define("jetVars", f'myJetVarCalc.produce({", ".join(cols)})')

            if self.store_nominal:
                df = df.Define("CleanJet_pt", "jetVars.pt(0)")

            df = df.Define(
                "CleanJet_sorting",
                "ROOT::VecOps::Reverse(ROOT::VecOps::Argsort(CleanJet_pt))",
            )

            if self.store_nominal:
                # stores the jet mass after JEC/JER and resorts it based on the new CleanJet_pt
                ROOT.gInterpreter.Declare(
                    """
                    using namespace ROOT;
                    RVecF propagateVector(RVecI jetIdx, RVecF jetVar, RVecF jetVar_raw) {
                        RVecF out(jetVar_raw);
                        for (int i = 0; i < jetIdx.size(); i++) {
                            out[jetIdx[i]] = jetVar[i];
                        }
                        return out;
                    }
                    """
                )
                df = df.Define(
                    "Jet_mass",
                    "propagateVector(CleanJet_jetIdx, Take(jetVars.mass(0), CleanJet_sorting), Jet_mass_raw)",
                )

            df = df.Redefine("CleanJet_pt", "Take(CleanJet_pt, CleanJet_sorting)")

            resortCols = ["CleanJet_" + prop for prop in ["pt", "eta", "phi", "jetIdx"]]
            for col in resortCols:
                df.Redefine(col, f"Take({col}, CleanJet_sorting)")

            if self.store_variations:
                sources = list(map(lambda k: "JES_" + k, sources))
                _sources = []
                if self.do_JER:
                    _sources = [f"JER_{i}" for i in range(6)]
                _sources += sources
                sources = _sources.copy()

                for variable in ["CleanJet_pt", "Jet_mass"]:
                    for i, source in enumerate(sources):
                        up = f"Take(jetVars.{variable.split('_')[-1]}({2*i+1}), CleanJet_sorting)"
                        do = f"Take(jetVars.{variable.split('_')[-1]}({2*i+1+1}), CleanJet_sorting)"
                        df = df.Vary(
                            variable,
                            "ROOT::RVec<ROOT::RVecF>{" + up + ", " + do + "}",
                            ["up", "down"],
                            source,
                        )

            df = df.DropColumns("jetVars")
            df = df.DropColumns("CleanJet_sorting")
        return df
