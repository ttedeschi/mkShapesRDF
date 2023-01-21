

groupPlot = {}

groupPlot['Fake']  = {
                  'nameHR' : 'nonprompt',
                  'isSignal' : 0,
                  'color': 921,    # kGray + 1
                  'samples'  : ['Fake_m', 'Fake_e']
}

groupPlot['top']  = {  
                  'nameHR' : 'tW and t#bar{t}',
                  'isSignal' : 0,
                  #'color': 400,   # kYellow
                  'color': ROOT.kYellow,   # kYellow
                  'samples'  : ['top']
              }

_bins = [30, 50, 70, 100, 130, 160, 200, 250, 300, 350, 400, 500, 700]
dys = {}
for i in range(-1, len(_bins)-1):
    if i == -1:
        # underflow bin
        dys[f'DY{i+1}'] = f'(ptll < {_bins[i+1]})'
    elif i == len(_bins)-2:
        # overflow bin
        dys[f'DY{i+1}'] = f'(ptll >= {_bins[i]})'
    else:
        dys[f'DY{i+1}'] = f'(ptll >= {_bins[i]} && ptll < {_bins[i+1]})'

_i = 0
for dy in dys.keys():
    groupPlot[dy] = {
            'nameHR': dy,
            'isSignal': 0,
            'color': ROOT.kGreen - 7 + _i,
            'samples': ['DY_' + dy]
            }
    _i +=1


"""
groupPlot['DY']  = {  
                  'nameHR' : ,
                  'isSignal' : 0,
                  #'color': 418,    # kGreen+2
                  'color': ROOT.kGreen+2,    # kGreen+2
                  'samples'  : ['DY_hardJets']
              }
groupPlot['DY_PUJets']  = {  
                  'nameHR' : "DY 1 PU jet",
                  'isSignal' : 0,
                  'color': 416,    # kGreen
                  'samples'  : ['DY_PUJets']
              }
"""


groupPlot['Multiboson']  = {  
                  'nameHR' : 'Multiboson',
                  'isSignal' : 0,
                  'color': 617, # kViolet + 1  
                  #'samples'  : ['WWewk','WW', 'ggWW', 'VVV', 'VZ', 'WZ', 'ZZ', 'Vg', 'Wg', 'VgS_H', 'VgS_L']
                  'samples'  : ['WWewk','WW', 'ggWW', 'Vg', 'VgS_H', 'VgS_L', 'VZ', 'VVV']
                  #'VVV', 'VZ', 'WZ', 'ZZ', 'Vg', 'Wg', 'VgS_H', 'VgS_L']
              }

groupPlot['Zjj']  = {  
                  'nameHR': 'Zjj',
                  'isSignal' : 1,
                  'color': 600,    # kBlue
                  'samples'    : ['Zjj']
              }

groupPlot['DATA']  = { 
                  'nameHR' : 'Data',
                  'color': 1 ,  
                  'isSignal' : 0,
                  'isData'   : 1 ,
                  'isBlind'  : 0
              }

plot = {}

# merge cuts
_mergedCuts = []
for cut in list(cuts.keys()):
    __cutExpr = ''
    if type(cuts[cut]) == dict:
        __cutExpr = cuts[cut]['expr']
        for cat in list(cuts[cut]['categories'].keys()):
            _mergedCuts.append(cut + '_' + cat)
    elif type(cuts[cut]) == str:
        _mergedCuts.append(cut)

cuts2j = _mergedCuts
cuts2j_ee = list(filter(lambda k: k.endswith('ee'), cuts2j))
cuts2j_mm = list(filter(lambda k: k.endswith('mm'), cuts2j))
cuts2j_sr = list(filter(lambda k: k.startswith('sr'), cuts2j))
cuts2j_cr = list(set(cuts2j).difference(set(cuts2j_sr)))

plot['DATA']  = { 
                  'nameHR' : 'Data',
                  'color': 1 ,  
                  'isSignal' : 0,
                  'isData'   : 1 ,
                  'isBlind'  : 0,
                  'blind'   :  dict([(cut, 'full') for cut in cuts2j_sr])
              }


dys_renorms = [ ('CMS_hww_DYnorm2j_DY0', 0.9392603267590494), ('CMS_hww_DYnorm2j_DY1', 0.95688873459445), ('CMS_hww_DYnorm2j_DY2', 0.9585358979880855), ('CMS_hww_DYnorm2j_DY3', 0.9533120891845211), ('CMS_hww_DYnorm2j_DY4', 0.9624481324870333), ('CMS_hww_DYnorm2j_DY5', 1.000501248601684), ('CMS_hww_DYnorm2j_DY6', 0.9928228630269565), ('CMS_hww_DYnorm2j_DY7', 1.0019779396615047), ('CMS_hww_DYnorm2j_DY8', 0.9882469350967062), ('CMS_hww_DYnorm2j_DY9', 0.9029095923018013), ('CMS_hww_DYnorm2j_DY10', 0.8820849092100003), ('CMS_hww_DYnorm2j_DY11', 0.8337083847015078), ('CMS_hww_DYnorm2j_DY12', 0.8783211096037533)]

#dys_renorms = [ ('CMS_hww_DYnorm2j_DY0', 0), ('CMS_hww_DYnorm2j_DY1', 0.95688873459445), ('CMS_hww_DYnorm2j_DY2', 0.9585358979880855), ('CMS_hww_DYnorm2j_DY3', 0.9533120891845211), ('CMS_hww_DYnorm2j_DY4', 0.9624481324870333), ('CMS_hww_DYnorm2j_DY5', 1.000501248601684), ('CMS_hww_DYnorm2j_DY6', 0.9928228630269565), ('CMS_hww_DYnorm2j_DY7', 1.0019779396615047), ('CMS_hww_DYnorm2j_DY8', 0.9882469350967062), ('CMS_hww_DYnorm2j_DY9', 0.9029095923018013), ('CMS_hww_DYnorm2j_DY10', 0.8820849092100003), ('CMS_hww_DYnorm2j_DY11', 0.8337083847015078), ('CMS_hww_DYnorm2j_DY12', 0.8783211096037533)]



dys_renorms_ee = [ ('CMS_hww_DYnorm2j_ee_DY0', 1.0026350609019545), ('CMS_hww_DYnorm2j_ee_DY1', 1.0277531005697302), ('CMS_hww_DYnorm2j_ee_DY2', 1.0168507142476406), ('CMS_hww_DYnorm2j_ee_DY3', 1.0100998907631782), ('CMS_hww_DYnorm2j_ee_DY4', 0.9921164342167571), ('CMS_hww_DYnorm2j_ee_DY5', 1.0813154499366064), ('CMS_hww_DYnorm2j_ee_DY6', 0.9689146003839226), ('CMS_hww_DYnorm2j_ee_DY7', 1.049870317384973), ('CMS_hww_DYnorm2j_ee_DY8', 0.9579293300770655), ('CMS_hww_DYnorm2j_ee_DY9', 0.8629022177774078), ('CMS_hww_DYnorm2j_ee_DY10', 0.849247952062298), ('CMS_hww_DYnorm2j_ee_DY11', 0.8845092701184382), ('CMS_hww_DYnorm2j_ee_DY12', 0.7968156141812227)]

dys_renorms_mm = [('CMS_hww_DYnorm2j_mm_DY0', 0.9165379904411813), ('CMS_hww_DYnorm2j_mm_DY1', 0.9305606999714235), ('CMS_hww_DYnorm2j_mm_DY2', 0.9358279845680133), ('CMS_hww_DYnorm2j_mm_DY3', 0.9299498481242454), ('CMS_hww_DYnorm2j_mm_DY4', 0.9493752800190959), ('CMS_hww_DYnorm2j_mm_DY5', 0.965864669443437), ('CMS_hww_DYnorm2j_mm_DY6', 1.0042246407476225), ('CMS_hww_DYnorm2j_mm_DY7', 0.9796299144476369), ('CMS_hww_DYnorm2j_mm_DY8', 1.0026626349369017), ('CMS_hww_DYnorm2j_mm_DY9', 0.9240642033314306), ('CMS_hww_DYnorm2j_mm_DY10', 0.898310565641909), ('CMS_hww_DYnorm2j_mm_DY11', 0.8093774027362743), ('CMS_hww_DYnorm2j_mm_DY12', 0.942861352084504)]

_i = 0
for dy in dys.keys():
    plot[dy] = {
            'scale': 1,
            'cuts': dict(tuple([(cut,dys_renorms_ee[_i][1]) for cut in cuts2j_ee])  + \
                        tuple([(cut,dys_renorms_mm[_i][1]) for cut in cuts2j_mm]))
            }
    _i+=1
print(plot)
