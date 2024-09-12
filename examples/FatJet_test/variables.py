# lis tof FatJet variables after the module 
from mkShapesRDF.processor.modules.FatJetSel import FatJetFilter_dict

MinHisto_pt = FatJetFilter_dict['default']['pt_min']
MaxHisto_pt = FatJetFilter_dict['default']['pt_max']
MaxHistoEta = FatJetFilter_dict['default']['max_eta']
MinMassSodftDrop, MaxMassSoftDrop = FatJetFilter_dict['default']['mass_range']




variables = {}

variables['NewFatJet_n'] = {
    'name': 'Sum(CleanFatJet_pt>{MinHisto_pt})',
    'range': (10,0,10),
    'xaxis': 'number of FatJet',
}
variables['NewFatJet1_pt'] = {
    'name' : 'CleanFatJet_pt[0]',
    'range' : (50, MinHisto_pt, MaxHisto_pt),
    'xaxis' : 'pt of first FatJet [GeV]',
}
variables['NewFatJet2_pt'] = {
    'name' : 'CleanFatJet_pt[0]',
    'range' : (50, MinHisto_pt, MaxHisto_pt),
    'xaxis' : 'pt of second FatJet [GeV]',
}
variables["NewFatJet_msoftdrop"] = {
    'name' : 'CleanFatJet_msoftdrop',
    'range': (50, MinMassSodftDrop, MaxMassSoftDrop),
    'xaxis': 'm_{SD} of fatjets',
}
variables["NewFatJet_eta1"] = {
    'name': ' abs(CleanFatJet_eta[0])',
    'range': (50, 0, 0, MaxHistoEta),
    'xaxis': 'eta of first FatJet',
}
variables["NewFatJet_eta2"] ={
    'name': ' abs(CleanFatJet_eta[1])',
    'range': (50, 0, 0, MaxHistoEta),
    'xaxis': 'eta of first FatJet',
}
variables["NewFatJet_jetId"] = {
    'name': 'CleanFatJet_id',
    'range':(10,0,10),
    'xaxis': 'CleanFatJet Id',
}
variables["JetNotFat_deltaR"] = {
    'name': 'CleanJetNotFat_deltaR',
    'range':(10,0,1),
    'xaxis': "deltaR jet not fat",    
}
