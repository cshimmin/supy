import samples

ph = samples.SampleHolder()

dir = "/vols/cms02/elaird1/11_skims/09_photons_skim/"

#data
ph.add("Run2010A_JMT_skim_skim",       'utils.fileListFromDisk(location = "%s/Run2010A_JMT_skim_*_skim.root", isDirectory = False)'     %dir,  lumi = 1.720000e-01)
ph.add("Run2010A_JM_skim_skim",        'utils.fileListFromDisk(location = "%s/Run2010A_JM_skim_*_skim.root", isDirectory = False)'      %dir,  lumi = 2.889000e+00)
ph.add("Run2010B_J_skim_skim",         'utils.fileListFromDisk(location = "%s/Run2010B_J_skim_*_skim.root", isDirectory = False)'       %dir,  lumi = 3.897000e+00)

#MG
ph.add("v12_g_jets_mg_pt200_skim",     'utils.fileListFromDisk(location = "%s/v12_g_jets_mg_pt200_*_skim.root", isDirectory = False)'   %dir,  xs = 1.189819e-02 * 6.159500e+02)
ph.add("v12_qcd_mg_ht_1000_inf_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_1000_inf_*_skim.root", isDirectory = False)'%dir,  xs = 2.081387e-04 * 1.054100e+02)
ph.add("v12_qcd_mg_ht_250_500_skim",   'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_250_500_*_skim.root", isDirectory = False)' %dir,  xs = 2.343954e-06 * 2.171700e+05)
ph.add("v12_qcd_mg_ht_500_1000_skim",  'utils.fileListFromDisk(location = "%s/v12_qcd_mg_ht_500_1000_*_skim.root", isDirectory = False)'%dir,  xs = 1.648990e-04 * 6.604000e+03)
#ph.add("v12_g_jets_mg_pt100_200_skim", 'utils.fileListFromDisk(location = dir+"/v12_g_jets_mg_pt100_200_*_skim.root", isDirectory = False)', xs = 0.000000e+00 * 4.414520e+03)
#ph.add("v12_g_jets_mg_pt40_100_skim",  'utils.fileListFromDisk(location = dir+"/v12_g_jets_mg_pt40_100_*_skim.root", isDirectory = False)',  xs = 0.000000e+00 * 2.999740e+04)
#ph.add("v12_qcd_mg_ht_100_250_skim",   'utils.fileListFromDisk(location = dir+"/v12_qcd_mg_ht_100_250_*_skim.root", isDirectory = False)',   xs = 0.000000e+00 * 8.890000e+06)
#ph.add("v12_qcd_mg_ht_50_100_skim",    'utils.fileListFromDisk(location = dir+"/v12_qcd_mg_ht_50_100_*_skim.root", isDirectory = False)',    xs = 0.000000e+00 * 3.810000e+07)

#PYTHIA
ph.add("v12_g_jets_py6_pt170_skim", 'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt170_*_skim.root", isDirectory = False)'%dir,xs = 5.790000e-02 * 2.437000e+01)
ph.add("v12_g_jets_py6_pt80_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt80_*_skim.root", isDirectory = False)'%dir, xs = 2.430000e-03 * 5.321300e+02)
ph.add("v12_qcd_py6_pt170_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt170_*_skim.root", isDirectory = False)'%dir,   xs = 1.456517e-04 * 2.421400e+04)
ph.add("v12_qcd_py6_pt300_skim",    'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt300_*_skim.root", isDirectory = False)'%dir,   xs = 8.832841e-04 * 1.256000e+03)
ph.add("v12_qcd_py6_pt80_skim",     'utils.fileListFromDisk(location = "%s/v12_qcd_py6_pt80_*_skim.root", isDirectory = False)'%dir,    xs = 9.681517e-07 * 8.983300e+05)
#ph.add("v12_g_jets_py6_pt30_skim",  'utils.fileListFromDisk(location = "%s/v12_g_jets_py6_pt30_*_skim.root", isDirectory = False)'%dir, xs = 0.000000e+00 * 1.951350e+04)