variables = {}

variables['ptj1'] = {
        'name': 'CleanJet_pt[0]',
        'range': (100, 30, 500),
        'xaxis': 'p_{T} 1st jet',
        'fold' :3
}

variables['ptj2'] = {
        'name': 'CleanJet_pt[1]',
        'range': (100, 30, 500),
        'xaxis': 'p_{T} 2nd jet',
        'fold' :3
}

variables['mjj']      = {   'name': 'mjj',            #   variable name    
                            'range' : (50, 200, 3000),    #   variable range
                            'xaxis' : 'm_{jj} [GeV]',  #   x axis name
                            'fold' :3
                        }

variables['mjjbins']      = {   'name': 'mjj',            #   variable name    
                            'range' : (5, 500, 4000),    #   variable range
                            'xaxis' : 'm_{jj} [GeV]',  #   x axis name
                            'fold' :3
                        }

variables['ptll']  = {   'name': 'ptll',
                        'range' : (70, 30, 600),
                        'xaxis' : 'p_{T}^{ll} [GeV]',
                        'fold' : 3
                        }

#variables['ptll_few']  = {   'name': 'ptll',
#                        'range' : (20, 30, 600),
#                        'xaxis' : 'p_{T}^{ll} [GeV]',
#                        'fold' : 3
#                        }

# np.logspace(np.log(30)/np.log(10),np.log(600)/np.log(10),20) 

variables['ptll_few']  = {   'name': 'ptll',
                        'range': ([0, 30, 50, 70, 100, 130, 160, 200, 250, 300, 350, 400, 500, 700],),
#                        'range' : ([ 30.        ,  35.12339741,  41.12176819,  48.14454022,
#                                    56.36666064,  65.99295408,  77.26322508,  90.458232  ,
#                                           105.90668105, 123.99341491, 145.16899961, 169.96094884,
#                                                  198.98686501, 232.96982465, 272.75639121, 319.33770416,
#                                                         373.87416973, 437.72436818, 512.47889801, 600.        ],),
                        'xaxis' : 'p_{T}^{ll} [GeV]',
                        'fold' : 3,
                        #'setLogx': 1
                        }

variables['mll']  = {   'name': 'mll',
                        'range' : (100, 66,107),
                        'xaxis' : 'm_{ll} [GeV]',
                        'fold' : 3
                        }

"""
variables['mllOut']  = {   'name': 'mll',
                        'range' : (100, 50,150),
                        'xaxis' : 'm_{ll} [GeV]',
                        'fold' : 3
                        }
                        """



variables['ptl1']  = {   'name': 'Lepton_pt[0]',
                        'range' : (60,30,300),
                        'xaxis' : 'p_{T} 1st lep',
                        'fold'  : 3
                        }

variables['ptl2']  = {   'name': 'Lepton_pt[1]',
                        'range' : (60,20,300),
                        'xaxis' : 'p_{T} 2nd lep',
                        'fold'  : 3
                        }


variables['puppimet']  = {
                        'name': 'PuppiMET_pt',
                        'range' : (20,0,200),
                        'xaxis' : 'puppimet [GeV]',
                        'fold'  : 3
                        }

variables['detajj']  = {  'name': 'detajj',
                        'range' : (40, 0.0, 10.0),
                        'xaxis' : '#Delta#eta_{jj}',
                        'fold'  : 3
                        }

variables['detajj_low']  = {  'name': 'detajj',
                        'range' : (20, 0.0, 3.0),
                        'xaxis' : '#Delta#eta_{jj}',
                        'fold'  : 3
                        }

variables['detajj_high']  = {  'name': 'detajj',
                        'range' : (15, 3.0, 7.0),
                        'xaxis' : '#Delta#eta_{jj}',
                        'fold'  : 3
                        }

variables['dphijj']  = {  'name': 'dphijj',
                        'range' : (40, 0, 6.5),
                        'xaxis' : '#Delta#phi_{jj}',
                        'fold'  : 3
                        }

