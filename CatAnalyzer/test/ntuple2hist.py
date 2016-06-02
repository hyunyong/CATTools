#!/usr/bin/env python
import ROOT, os, sys, copy
from array import array

ROOT.gROOT.SetBatch()
pi = ROOT.TMath.Pi()

in_type = sys.argv[1]
in_f = sys.argv[2]

out_f = in_f.replace(".root", "_hist.root").split("/")[-1]
in_rf = ROOT.TFile(in_f)
mc = True

if not in_type == 'mc':
  mc = False


def hist_maker(name, title, bin_set, x_name, y_name, tr, br, w):
  if bin_set[2] == 2500:
    bin = []
    for x in xrange(15):
      bin.append(2500.0/2.0*float(x)/15.0)
    bin.append(1500)
    bin.append(2000)
    bin.append(2500)
    pt_bin = array('d', bin)
    hist = ROOT.TH1F(name, title, len(pt_bin)-1, pt_bin)
  else:
    hist = ROOT.TH1F(name, title, bin_set[0], bin_set[1], bin_set[2])
  hist.GetXaxis().SetTitle(x_name)
  hist.GetYaxis().SetTitle(y_name)
  hist.Sumw2()
  tr.Project(name, br, w)
  return hist

def prof_maker(name, title, bin_set, x_name, y_name, tr, br, w):
  prof = ROOT.TProfile(name, title, bin_set[0], bin_set[1], bin_set[3])
  prof.GetXaxis().SetTitle(x_name)
  prof.GetYaxis().SetTitle(y_name)
  prof.Sumw2()
  tr.Project(name, br, w)
  return prof

def hist2_maker(name, title, bin_set, x_name, y_name, tr, br_x, br_y, w):
  hist2 = ROOT.TH2F(name, title, bin_set[0][0], bin_set[0][1], bin_set[0][2], bin_set[1][0], bin_set[1][1], bin_set[1][2])
  hist2.GetXaxis().SetTitle(x_name)
  hist2.GetYaxis().SetTitle(y_name)
  hist2.Sumw2()
  tr.Project(name, br_y+":"+br_x, w)
  return hist2

## event selection
r_mass_cut = "(raw_mass > 220)*"
dp12_cut = "(abs(abs(del_phi12)-%f)<1.0)*"%pi
eta_cut = "(abs(jet1_eta)<2.5)*"
met_cut = "(metSig<0.3)*"
d_cut = r_mass_cut+dp12_cut+eta_cut+met_cut

## event classification
l_eta = "(abs(jet2_eta)>0.0)*(abs(jet2_eta)<0.8)*(jet3_pt>30)*"#(jet3_pt>30)*(jet3_p<100)*"#(abs(jet3_eta)>0.08)*"
m_eta = "(abs(jet2_eta)>0.8)*(abs(jet2_eta)<1.5)*(jet3_pt>30)*"#(jet3_pt>30)*(jet3_p<200)*"#(abs(jet3_eta)>0.9)*"
h_eta = "(abs(jet2_eta)>1.5)*(abs(jet2_eta)<2.5)*(jet3_pt>30)*"#(jet3_pt>30)*(jet3_p<300)*"#(abs(jet3_eta)>1.92)*"

h_pt = "(jet1_pt>510)*(jet1_pt<2500)*(hlt_450_pass == 1)*"
m_pt = "(jet1_pt>400)*(jet1_pt<500)*(hlt_320_pass == 1)*"
l_pt = "(jet1_pt>170)*(jet1_pt<350)*(hlt_140_pass == 1)*"

dr_cut = "(del_r23>0.4)*(del_r23<1.5)*"
dr_small = "(del_r23>0.4)*(del_r23<1.0)*"
dr_large = "(del_r23>1.0)*(del_r23<1.5)*"

pt3_non = "(1.0)*"
pt3_low = "(jet3_pt/jet2_pt < 0.3)*"
pt3_high = "(jet3_pt/jet2_pt > 0.7)*"

eta_bin = ["low_eta", "medium_eta", "high_eta"]
eta_bin_cut = [l_eta, m_eta, h_eta]
pt_bin = ["low_pt", "medium_pt", "high_pt"]
pt_bin_cut = [l_pt, m_pt, h_pt]
dr_bin = ["dr", "sdr", "ldr"]
dr_bin_cut = [dr_cut, dr_small, dr_large]
pt3_bin = ["non", "lpt3", "hpt3"]
pt3_bin_cut = [pt3_non, pt3_low, pt3_high]

beta_l = ["beta23", "del_eta23", "del_phi23", "del_r23", "raw_mass","jet3_pt/jet2_pt"]
gbeta_l = ["gbeta", "gdel_eta", "gdel_phi", "gdel_r", "raw_mass","gjet3_pt/gjet2_pt"]
beta_bin = [[18, 0, pi], [30, -3, 3], [30, -3, 3], [30, 0, 3], [50, 0, 5000], [10,0,1]]
jet_l = ["pt", "eta", "phi"]
jet_bin = [[30,0,2500],[30,-3,3],[30,-pi,pi]]
ev_l = ["njet", "metSig", "nvtx"]  
ev_bin = [[30, 0, 30],[10, 0, 1], [50, 0, 50]]

cut_l = []
cut_name = []

for i, eta in enumerate(eta_bin_cut):
  for j, pt in enumerate(pt_bin_cut):
    for k, dr in enumerate(dr_bin_cut):
      for l, pt3 in enumerate(pt3_bin_cut):
        cut_l.append(eta+pt+dr+pt3+"(1.0)")
        cut_name.append(eta_bin[i]+"_"+pt_bin[j]+"_"+dr_bin[k]+"_"+pt3_bin[l])

if mc:
    sys_e = ["nom", "jer_u", "jer_d", "jar", "pu_u", "pu_d"]
else:
    sys_e = ["nom", "jes_u", "jes_d"]    
hist_l = []

for sys in sys_e:
  if mc:
    e_w = "(1.0*pileupWeight)"
    if sys.startswith("pu"):
      if sys == "pu_u":
        e_w = "(1.0*pileupWeight_up)"
      else:
        e_w = "(1.0*pileupWeight_dn)"
  else:
    e_w = "(1.0)"
  for i, cut in enumerate(cut_l):
    if sys.startswith("pu"):
      tr = in_rf.Get("cc/nom").Clone(cut_name[i])
    else:
      tr = in_rf.Get("cc/%s"%sys).Clone(cut_name[i])
    tr.Draw(">>eventList", cut)
    el = ROOT.gDirectory.Get("eventList")
    tr.SetEventList(el)
 
    for bi, beta_loop in enumerate(beta_l):
      name = cut_name[i]+"_"+sys+"_"+beta_loop
      name = name.replace("/","_")
      title = name
      bin_set = beta_bin[bi]
      x_name = beta_loop
      y_name = "count"
      br = beta_loop
      hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, e_w)))
    for ji in xrange(3):
      for jii, jet_loop in enumerate(jet_l):
        name = cut_name[i]+"_"+sys+"_jet%d_"%(ji+1)+jet_loop
        title = name
        bin_set = jet_bin[jii]
        x_name = jet_loop
        y_name = "count"
        br = "jet%d_"%(ji+1)+jet_loop
        hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, e_w)))
    for ei, ev_loop in enumerate(ev_l):
      name = cut_name[i]+"_"+sys+"_"+ev_loop
      title = name
      bin_set = ev_bin[ei]
      x_name = ev_loop
      y_name = "count"
      br = ev_loop
      hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, e_w)))
    # unfolding part
    if (sys == "nom" and mc):
      for bi, beta_loop in enumerate(beta_l):
        if beta_loop == "raw_mass": continue
        name = cut_name[i]+"_gen_"+beta_loop
        name = name.replace("/","_")
        title = name
        bin_set = beta_bin[bi]
        x_name = gbeta_l[bi]
        y_name = "count"
        br = gbeta_l[bi]
        hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, e_w)))

        name = cut_name[i]+"_resM_"+beta_loop
        name = name.replace("/","_")
        title = name
        hist_l.append(copy.deepcopy(hist2_maker(name, title, [bin_set,bin_set],"RECO", "GEN", tr, beta_loop, gbeta_l[bi], e_w)))

    del tr
    del el


# gen jet 
if mc:
  ## event selection
  r_mass_cut = "(gen_raw_mass > 220)*"
  dp12_cut = "(abs(abs(gen_del_phi12)-%f)<1.0)*"%pi
  eta_cut = "(abs(gen_jet1_eta)<2.5)*"
  d_cut = r_mass_cut+dp12_cut+eta_cut
  
  ## event classification
  l_eta = "(abs(gen_jet2_eta)>0.0)*(abs(gen_jet2_eta)<0.8)*(gen_jet3_pt>30)*"
  m_eta = "(abs(gen_jet2_eta)>0.8)*(abs(gen_jet2_eta)<1.5)*(gen_jet3_pt>30)*"
  h_eta = "(abs(gen_jet2_eta)>1.5)*(abs(gen_jet2_eta)<2.5)*(gen_jet3_pt>30)*"
  
  h_pt = "(gen_jet1_pt>510)*(gen_jet1_pt<2500)*"
  m_pt = "(gen_jet1_pt>400)*(gen_jet1_pt<500)*"
  l_pt = "(gen_jet1_pt>170)*(gen_jet1_pt<350)*"
  
  dr_cut = "(gen_del_r23>0.4)*(gen_del_r23<1.5)*"
  dr_small = "(gen_del_r23>0.4)*(gen_del_r23<1.0)*"
  dr_large = "(gen_del_r23>1.0)*(gen_del_r23<1.5)*"
  
  pt3_non = "(1.0)*"
  pt3_low = "(gen_jet3_pt/gen_jet2_pt < 0.3)*"
  pt3_high = "(gen_jet3_pt/gen_jet2_pt > 0.7)*"
  
  eta_bin = ["low_eta", "medium_eta", "high_eta"]
  eta_bin_cut = [l_eta, m_eta, h_eta]
  pt_bin = ["low_pt", "medium_pt", "high_pt"]
  pt_bin_cut = [l_pt, m_pt, h_pt]
  dr_bin = ["dr", "sdr", "ldr"]
  dr_bin_cut = [dr_cut, dr_small, dr_large]
  pt3_bin = ["non", "lpt3", "hpt3"]
  pt3_bin_cut = [pt3_non, pt3_low, pt3_high]
  
  beta_l = ["beta23", "del_eta23", "del_phi23", "del_r23", "raw_mass","jet3_pt/jet2_pt"]
  beta_bin = [[18, 0, pi], [30, -3, 3], [30, -3, 3], [30, 0, 3], [50, 0, 5000], [10,0,1]]
  jet_l = ["pt", "eta", "phi"]
  jet_bin = [[30,0,2500],[30,-3,3],[30,-pi,pi]]
  
  cut_l = []
  cut_name = []
  
  for i, eta in enumerate(eta_bin_cut):
    for j, pt in enumerate(pt_bin_cut):
      for k, dr in enumerate(dr_bin_cut):
        for l, pt3 in enumerate(pt3_bin_cut):
          cut_l.append(eta+pt+dr+pt3+"(1.0)")
          cut_name.append(eta_bin[i]+"_"+pt_bin[j]+"_"+dr_bin[k]+"_"+pt3_bin[l])
  
  for i, cut in enumerate(cut_l):
    tr = in_rf.Get("cc/nom").Clone(cut_name[i])
    tr.Draw(">>eventList", cut)
    el = ROOT.gDirectory.Get("eventList")
    tr.SetEventList(el)
    e_w = "(1.0)"  
    for bi, beta_loop in enumerate(beta_l):
      name = cut_name[i]+"_genJet_"+beta_loop
      name = name.replace("/","_")
      title = "Gen Jet "+name
      bin_set = beta_bin[bi]
      x_name = beta_loop
      y_name = "count"
      br = "gen_"+beta_loop
      hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, e_w)))
    for ji in xrange(3):
      for jii, jet_loop in enumerate(jet_l):
        name = cut_name[i]+"_genJet_jet%d_"%(ji+1)+jet_loop
        title = "Gen Jet "+name
        bin_set = jet_bin[jii]
        x_name = jet_loop
        y_name = "count"
        br = "gen_jet%d_"%(ji+1)+jet_loop
        hist_l.append(copy.deepcopy(hist_maker(name, title, bin_set, x_name, y_name, tr, br, e_w)))
  


# out file write


out_rf = ROOT.TFile(out_f, "RECREATE")
for x in hist_l:
  print x.GetName(), x.GetEntries()
  x.Write()
out_rf.Write()
out_rf.Close()
in_rf.Close()
