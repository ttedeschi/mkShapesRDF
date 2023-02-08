import sys


class Plotter:

    @staticmethod
    def getHisto(file, path):
        h = file.Get(path)
        try:
            h.Integral()
        except:
            print('\nERROR: Could not get histogram', path, '\n\n')
            sys.exit()
        return h

    @staticmethod
    def Pad2TAxis(hist):
        xaxis = hist.GetXaxis()
        xaxis.SetLabelFont(42)
        xaxis.SetLabelOffset(0.025)
        xaxis.SetLabelSize(0.1)
        xaxis.SetNdivisions(505)
        xaxis.SetTitleFont(42)
        xaxis.SetTitleOffset(1.35)
        xaxis.SetTitleSize(0.11)

        yaxis = hist.GetYaxis()
        #yaxis.CenterTitle ( )
        yaxis.SetLabelFont(42)
        yaxis.SetLabelOffset(0.02)
        yaxis.SetLabelSize(0.1)
        yaxis.SetNdivisions(505)
        yaxis.SetTitleFont(42)
        yaxis.SetTitleOffset(.4)
        yaxis.SetTitleSize(0.11)

