#!/usr/bin/env python

import os,analysis,steps,calculables,samples,organizer,plotter,utils
import ROOT as r

class topAsymm(analysis.analysis) :
    def parameters(self) :
        objects = {}
        fields =                           [ "jet",              "met",           "sumP4",                "sumPt",                 "muon",       "electron",        "photon",        "muonsInJets"]
        objects["calo"] = dict(zip(fields, [("xcak5Jet","Pat"),  "metP4AK5TypeII","xcSumP4",              "xcSumPt",               ("muon","Pat"),("electron","Pat"),("photon","Pat"), False]))
        objects["pf"]   = dict(zip(fields, [("xcak5JetPF","Pat"),"metP4PF",       "xcak5JetPFRawSumP4Pat","xcak5JetPFRawSumPtPat", ("muon","Pat"),("electron","Pat"),("photon","Pat"),   True]))

        leptons = {}
        fieldsLepton    =                            ["name","ptMin",              "isoVar", "triggerList"]
        leptons["muon"]     = dict(zip(fieldsLepton, ["muon",     20, "CombinedRelativeIso", ("HLT_Mu9","HLT_Mu15_v1")]))
        leptons["electron"] = dict(zip(fieldsLepton, ["electron", 30,         "IsoCombined", ("FIX","ME")]))
        
        bVar = "TrkCountingHighEffBJetTags"
        bCut = {"normal"   : {"index":1, "min":2.0},
                "inverted" : {"index":0, "max":2.0}}
        lIso = {"normal":  {"nMaxIso":1, "indices":"Indices"},
                "inverted":{"nMaxIso":0, "indices":"IndicesNonIso"}}
        
        return { "objects": objects,
                 "lepton" : leptons,
                 "nJets" :  [{"min":3,"max":None}],
                 "bVar" : bVar,
                 "sample" : {"top" : {"bCut":bCut["normal"],  "lIso":lIso["normal"]},
                             "Wlv" : {"bCut":bCut["inverted"],"lIso":lIso["normal"]},
                             "QCD" : {"bCut":bCut["normal"],  "lIso":lIso["inverted"]}
                             }
                 }

    def listOfCalculables(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        outList  = calculables.zeroArgs()
        outList += calculables.fromCollections(calculables.Muon, [obj["muon"]])
        outList += calculables.fromCollections(calculables.Electron, [obj["electron"]])
        outList += calculables.fromCollections(calculables.Photon, [obj["photon"]])
        outList += calculables.fromCollections(calculables.Jet, [obj["jet"]])
        outList += [
            calculables.Jet.IndicesBtagged(obj["jet"],pars["bVar"]),
            calculables.Jet.Indices(      obj["jet"],      ptMin = 30, etaMax = 3.0, flagName = "JetIDloose"),
            calculables.Muon.Indices(     obj["muon"],     ptMin = 10, combinedRelIsoMax = 0.15),
            calculables.Electron.Indices( obj["electron"], ptMin = 10, simpleEleID = "80", useCombinedIso = True),
            calculables.Photon.photonIndicesPat(           ptMin = 25, flagName = "photonIDLooseFromTwikiPat"),

            calculables.XClean.IndicesUnmatched(collection = obj["photon"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.IndicesUnmatched(collection = obj["electron"], xcjets = obj["jet"], DR = 0.5),
            calculables.XClean.xcJet(obj["jet"], applyResidualCorrectionsToData = False,
                                     gamma    = obj["photon"],      gammaDR = 0.5,
                                     electron = obj["electron"], electronDR = 0.5,
                                     muon     = obj["muon"],         muonDR = 0.5, correctForMuons = not obj["muonsInJets"]),
            calculables.XClean.SumP4(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),
            calculables.XClean.SumPt(obj["jet"], obj["photon"], obj["electron"], obj["muon"]),

            calculables.Vertex.ID(),
            calculables.Vertex.Indices(),
            calculables.Other.lowestUnPrescaledTrigger(pars["lepton"]["triggerList"]),

            calculables.Top.mixedSumP4(transverse = obj["met"], longitudinal = obj["sumP4"]),
            calculables.Top.SemileptonicTopIndex(lepton),
            
            calculables.Top.NeutrinoPz(lepton,"mixedSumP4"),
            calculables.Top.NeutrinoP4P(lepton,"mixedSumP4"),
            calculables.Top.NeutrinoP4M(lepton,"mixedSumP4"),
            calculables.Top.TopReconstruction(lepton,obj["jet"]),
            calculables.Top.NeutrinoP4(lepton),
            calculables.Top.SumP4Nu(lepton,"mixedSumP4"),
            calculables.Top.SignedRapidity(lepton,"mixedSumP4Nu"),
            calculables.Top.RelativeRapidity(lepton,"mixedSumP4Nu"),
            
            calculables.Other.Mt(lepton,"%sNeutrinoP4%s"%lepton, allowNonIso=True),
            calculables.Muon.IndicesAnyIsoIsoOrder(obj[pars["lepton"]["name"]], pars["lepton"]["isoVar"])
            ]
        return outList
    
    def listOfSteps(self, pars) :
        obj = pars["objects"]
        lepton = obj[pars["lepton"]["name"]]
        lPtMin = pars["lepton"]["ptMin"]
        bVar = ("%s"+pars["bVar"]+"%s")%calculables.Jet.xcStrip(obj["jet"])

        def cleanupSteps() :
            return ([ steps.Filter.multiplicity("vertexIndices",min=1),
                      steps.Filter.monster(),
                      steps.Filter.hbheNoise(),
                      steps.Trigger.techBitFilter([0],True),
                      steps.Trigger.physicsDeclared(),            
                      #steps.Trigger.lowestUnPrescaledTrigger(), #FIXME ele
                      ]+[
                steps.Filter.multiplicity(s, max = 0) for s in ["%sIndices%s"%obj["photon"],
                                                                "%sIndicesUnmatched%s"%obj["photon"],
                                                                "%sIndices%s"%(obj["electron" if pars["lepton"]["name"]=="muon" else "muon"]),
                                                                "%sIndicesUnmatched%s"%obj["electron"],
                                                                "%sIndicesOther%s"%obj["muon"],
                                                                "%sIndicesOther%s"%obj["jet"],
                                                                ]
                ]+[steps.Jet.uniquelyMatchedNonisoMuons(obj["jet"]),]
                    )
        
        def templateSteps() :
            return ([ steps.Filter.label('templates'),
                     steps.Histos.value(obj["sumPt"],50,0,1000),
                     steps.Histos.value("%sMt%s"%lepton+"%sNeutrinoP4%s"%lepton, 30,0,180, xtitle = "M_{T}"),
                     steps.Histos.pt("%sCorrectedP4%s"%obj['jet'], 40,0,400, index = 0, indices = "%sIndices%s"%obj['jet']),
                     steps.Histos.pt("%sCorrectedP4%s"%obj['jet'], 40,0,400, index = 0, indices = "%sIndicesBtagged%s"%obj['jet']),
                     steps.Histos.generic(("%sCorrectedP4%s"%obj['jet'],"%sIndicesBtagged%s"%obj['jet']), 30,0,6,
                                          title = ";#Delta#phi leading b-tagness jets;events / bin",
                                          funcString = "lambda x: r.Math.VectorUtil.DeltaPhi(x[0][x[1][0]],x[0][x[1][1]])"),
                     ]+
                    [steps.Histos.eta("%sCorrectedP4%s"%obj['jet'], 50,-5,5, index = i, indices = "%sIndices%s"%obj['jet']) for i in range(3)]+
                    [steps.Filter.label('endTemplates')])

        def lepIso(index) :
            return steps.Histos.value(("%s"+pars["lepton"]["isoVar"]+"%s")%lepton, 60,0,0.6, indices = "%sIndicesAnyIsoIsoOrder%s"%lepton, index=index)
        
        return ([
            steps.Print.progressPrinter(),
            steps.Other.histogrammer("genpthat",200,0,1000,title=";#hat{p_{T}} (GeV);events / bin"),
            steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = "%sIndicesAnyIso%s"%lepton, index = 0),
            ]+sum([[step,lepIso(0)] for step in cleanupSteps()],[])+[
            steps.Histos.value(obj["sumPt"],50,0,1000),
            steps.Other.compareMissing([obj["sumP4"],obj["met"]]),
            
            steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
            steps.Filter.multiplicity("%sIndices%s"%obj["jet"], **pars["nJets"]),
            lepIso(0),

            steps.Histos.value(obj["sumPt"],50,0,1000),
            steps.Other.compareMissing([obj["sumP4"],obj["met"]]),
            steps.Filter.pt("mixedSumP4",min=20),
            
            lepIso(0),
            lepIso(1),

            steps.Filter.multiplicity("%sIndices%s"%lepton, max = pars["sample"]["lIso"]["nMaxIso"]),
            steps.Filter.pt("%sP4%s"%lepton, min = lPtMin, indices = ("%s"+pars["sample"]["lIso"]["indices"]+"%s")%lepton, index = 0),
            ]+templateSteps()+[
            steps.Histos.value(bVar, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = 0),
            steps.Histos.value(bVar, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = 1),
            steps.Histos.value(bVar, 60,0,15, indices = "%sIndicesBtagged%s"%obj["jet"], index = 2),
            
            steps.Filter.value(bVar, indices = "%sIndicesBtagged%s"%obj["jet"], index = 1, min = 0.0),
            steps.Filter.value(bVar, indices = "%sIndicesBtagged%s"%obj["jet"], **pars["sample"]["bCut"]),
            
            steps.Other.compareMissing([obj["sumP4"],obj["met"]]),
            steps.Histos.multiplicity("%sIndices%s"%obj["jet"]),
            ]+templateSteps()+[
            steps.Other.topAsymmetry(lepton),

            #steps.Histos.generic(("%sNeutrinoPz%s"%lepton,"%sNeutrinoPz%s"%lepton),(100,100),(-1500,-500),(500,1500),
            #                     title=";#nu_{-} p_{z} (GeV);#nu_{+} p_{z} (GeV);events / bin", funcString = "lambda x: (x[0][0],x[0][1])"),
            
            steps.Filter.multiplicity("%sIndices%s"%obj["jet"], min=4, max=4),
            steps.Filter.value(bVar, max=2.0, indices = "%sIndicesBtagged%s"%obj["jet"], index = 2),

            steps.Other.topAsymmetry(lepton),
            ]+templateSteps()+[
            steps.Histos.generic(("%sIndicesBtagged%s"%obj["jet"],"%sCorrectedP4%s"%obj["jet"]),
                                 30,0,180, title=";M_{2-light};events / bin",
                                 funcString="lambda x: (x[1][x[0][2]] + x[1][x[0][3]]).M()"),

            #steps.Other.productGreaterFilter(0,["%s%s"%lepton+"RelativeRapiditymixedSumP4NuM","%s%s"%lepton+"RelativeRapiditymixedSumP4NuP"]),
            #steps.Other.histogrammer("%sSignedRapidity%s"%lepton, 51, -5, 5, title = ";y_lep*q_lep*sign(boost);events / bin"),
            #steps.Other.histogrammer("%s%s"%lepton+"RelativeRapiditymixedSumP4", 51, -5, 5, title = ";#Delta y;events / bin"),
            #steps.Other.histogrammer(("%s%s"%lepton+"RelativeRapiditymixedSumP4NuM","%s%s"%lepton+"RelativeRapiditymixedSumP4NuP"),
            #                         (101,101), (-5,-5), (5,5), title = ";#Delta y #nu_{-};#Delta y #nu_{+};events / bin",
            #                         funcString = "lambda x: (x[0],x[1])"),
            #steps.Other.histogrammer(("mixedSumP4NuM","mixedSumP4NuP"),(75,75),(-1500,-1500),(1500,1500),
            #                         funcString = "lambda x:(x[0].pz(),x[1].pz())", title = ";mixedSumP4NuM.pz;mixedSumP4NuP.pz;events / bin")
            
            ])
    
    def listOfSampleDictionaries(self) :
        return [samples.mc, samples.muon, samples.electron]

    def listOfSamples(self,pars) :
        from samples import specify
        def data() :
            names = { "electron": [#"EG.2010A_skim",
                                   "Electron.Run2010B_skim"
                                   ],
                      "muon": ["Mu.Run2010A_skim",
                               "Mu.Run2010B_skim"
                               ] }
            return specify( #nFilesMax = 1, nEventsMax = 40000,
                            names = names[pars["lepton"]["name"]])

        def qcd_py6(eL) :
            q6 = [0,5,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q6.index(15)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("qcd_py6_pt_%dto%d"%t)[:None if t[1] else -3] for t in zip(q6,q6[1:]+[0])[iCut:]] )
        def qcd_py8(eL) :
            q8 = [0,15,30,50,80,120,170,300,470,600,800,1000,1400,1800]
            iCut = q8.index(50)
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = [("qcd_py8_pt%dto%d"%t)[:None if t[1] else -3] for t in zip(q8,q8[1:]+[0])[iCut:]] )
        def qcd_mg(eL) :
            qM = ["%d"%t for t in [50,100,250,500,1000]]
            return specify( effectiveLumi = eL, color = r.kBlue,
                            names = ["v12_qcd_mg_ht_%s_%s"%t for t in zip(qM,qM[1:]+["inf"])])
        def ttbar_mg(eL) :
            return specify( names = "tt_tauola_mg", effectiveLumi = eL, color = r.kOrange)

        def ewk(eL, skimp=True) :
            EWK = {}
            EWK["electron"] = specify( names = "w_enu", effectiveLumi = eL, color = 28)
            EWK["muon"] = specify( names = "w_munu", effectiveLumi = eL, color = 28)
            EWK["other"] = specify( names = "w_taunu", effectiveLumi = eL, color = r.kYellow-3)
            if skimp :
                return EWK[pars["lepton"]["name"]]
            return sum(EWK.values(),[])

        eL = 100 # 1/pb
        return  ( data() +
                  qcd_py6(eL) +
                  ttbar_mg(2000) +
                  ewk(eL)
                  )

    def conclude(self) :
        for tag in self.sideBySideAnalysisTags() :
            #organize
            org=organizer.organizer( self.sampleSpecs(tag) )
            org.mergeSamples(targetSpec = {"name":"Data 2010", "color":r.kBlack, "markerStyle":20}, allWithPrefix="Mu.Run2010")
            org.mergeSamples(targetSpec = {"name":"Data 2010", "color":r.kBlack, "markerStyle":20}, sources=["EG.2010A_skim","Electron.Run2010B_skim"])
            org.mergeSamples(targetSpec = {"name":"qcd_py6", "color":r.kBlue}, allWithPrefix="qcd_py6")
            org.mergeSamples(targetSpec = {"name":"standard_model", "color":r.kGreen+3},
                             sources = ["qcd_py6","w_enu","w_munu","w_taunu","tt_tauola_mg"], keepSources = True)
            org.scale(33)
            
            #plot
            pl = plotter.plotter(org,
                                 psFileName = self.psFileName(tag),
                                 samplesForRatios = ("Data 2010","standard_model"),
                                 sampleLabelsForRatios = ("data","s.m."),
                                 #whiteList = ["lowestUnPrescaledTrigger"],
                                 #doLog = False,
                                 #compactOutput = True,
                                 #noSci = True,
                                 pegMinimum = 0.1,
                                 blackList = ["lumiHisto","xsHisto","nJobsHisto"],
                                 )
            pl.plotAll()
