import numpy as np
import ROOT


def hist2array(h, flow=False, copy=True, include_sumw2=False):
    """hist2array takes a ROOT TH1 and returns an array with the bin contents

    Parameters
    ----------
        h : ROOT.TH1
            histogram
        flow : bool, optional, default: False
            if True include underflow and overflow bins
        copy : bool, optional, default: True
            if True returns a copy of original bin content, otherwise modifications of the array will affect the original histogram
        include_sumw2 : bool, optional, default: False
            if True returns a ``(bin contents array, sumw2 array)

    Returns
    -------
        `np.array` / `tuple(np.array, np.array)`
            Array of bin contents or tuple of arrays (bin contents and sumw2)
    """

    nx = h.GetNbinsX() + 2
    dtype = 0
    if isinstance(h, ROOT.TH1D):
        dtype = np.double
    elif isinstance(h, ROOT.TH1F):
        dtype = np.float
    elif isinstance(h, ROOT.TH1I):
        dtype = np.int
    else:
        print("Histogram of type", h, "is not supperted", file=sys.stderr)
        sys.exit(1)

    vals = np.ndarray((nx,), dtype=dtype, buffer=h.GetArray())
    sumw2 = np.ndarray((nx,), dtype=dtype, buffer=h.GetSumw2().GetArray())

    shift = 1
    if flow:
        shift = 0
    vals = vals[shift : nx - shift]
    sumw2 = sumw2[shift : nx - shift]

    if copy:
        vals = vals.copy()
        sumw2 = sumw2.copy()
    if include_sumw2:
        return vals, sumw2
    else:
        return vals
