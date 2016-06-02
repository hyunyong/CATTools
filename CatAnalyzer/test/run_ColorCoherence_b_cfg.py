import FWCore.ParameterSet.Config as cms
import os, sys
process = cms.Process("ColorCoherenceAnalyzer")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )
process.options.allowUnscheduled = cms.untracked.bool(True)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring()
)
in_txt = open(sys.argv[2])
for f in in_txt:
    if f.find("failed") > 0 : continue
    process.source.fileNames.append(f)

print process.source.fileNames

#process.load("CATTools.CatProducer.pileupWeight_cff")
#from CATTools.CatProducer.pileupWeight_cff import pileupWeightMap
#process.pileupWeight.weightingMethod = "RedoWeight"
#process.pileupWeight.pileupRD = pileupWeightMap["Run2015_25nsV1"]
#process.pileupWeight.pileupUp = pileupWeightMap["Run2015Up_25nsV1"]
#process.pileupWeight.pileupDn = pileupWeightMap["Run2015Dn_25nsV1"]



"""
runOnMC=False
lumiFile = 'Cert_246908-255031_13TeV_PromptReco_Collisions15_50ns_JSON.txt'
for i in process.source.fileNames:
    if 'Run2015' in i:
        runOnMC=False
if not runOnMC:
    from FWCore.PythonUtilities.LumiList import LumiList
    lumiList = LumiList(os.environ["CMSSW_BASE"]+'/src/CATTools/CatProducer/prod/LumiMask/'+lumiFile)
    process.source.lumisToProcess = lumiList.getVLuminosityBlockRange()
    print process.source.lumisToProcess
"""
process.cc = cms.EDAnalyzer("ColorCoherenceAnalyzer",
    lumiSelection = cms.InputTag("lumiMask","","CAT"),
    vtx = cms.InputTag("catVertex", "nPV"),
    jets = cms.InputTag("catJets"),
    genjets = cms.InputTag("slimmedGenJets","","PAT"),
    mets = cms.InputTag("catMETs"),
    triggerBits = cms.InputTag("TriggerResults","","HLT"),
    triggerObjects = cms.InputTag("catTrigger"),
    pileupWeight = cms.InputTag("pileupWeight",""),
    pileupWeight_up = cms.InputTag("pileupWeight","up"),
    pileupWeight_dn = cms.InputTag("pileupWeight","dn")
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(sys.argv[2].split("/")[-1].replace(".txt", ".root"))
)
process.p = cms.Path(process.cc)
process.MessageLogger.cerr.FwkReport.reportEvery = 50000
