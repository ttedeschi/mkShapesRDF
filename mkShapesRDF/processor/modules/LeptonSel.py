import ROOT

def run(df, values, keepColumns):
    values.append(
            [df.Count(), 'begin count of LeptonSel']
            )
    a = len(values) - 1
    df = df.Filter('Leptons_pt[1]>10')
    values.append(
            [df.Count(), 'end count of LeptonSel']
            )

    b = len(values) - 1
    def fun(a, b):
        bVal = values[b] 
        aVal = values[a] 
        if 'list' in str(type(bVal)):
            bVal = bVal[0]
        if 'list' in str(type(aVal)):
            aVal = aVal[0]
        return ['Efficiency of 2 lep cut', str(round(bVal.GetValue()/aVal.GetValue()*100, 3)) + '%']

    values.append([fun, a, b])
