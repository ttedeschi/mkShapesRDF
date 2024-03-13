import ROOT
import numpy as np

ROOT.TH1.SetDefaultSumw2(True)


def rnp_array(array, copy=True):
    """
    Convert TArray into numpy.array

    Parameters
    ----------
    array : ROOT.TArray
        a ROOT TArrayD
    copy : bool, optional
        if True returns a copy, by default True

    Returns
    -------
    np.array
        converted numpy array
    """
    if not isinstance(array, ROOT.TArrayD):
        raise ("Cannot convert ", array, "to TArrayD")
    dtype = np.double
    nx = len(array)
    arr = np.ndarray((nx,), dtype=dtype, buffer=array.GetArray())
    if copy:
        arr = arr.copy()
    return arr


def rnp_hist2array(h, include_overflow=False, copy=True):
    """
    Converts histogram into a numpy array

    Parameters
    ----------
    h : ROOT.TH
        histogram, 1, 2 or 3D
    include_overflow : bool, optional
        Includes underflow and overflow bins, by default False
    copy : bool, optional
        if true returns a copy of the array, its modification won't affect the histogram, by default True

    Returns
    -------
    np.array
        converted numpy array
    """
    arr = rnp_array(h, copy=copy)
    if isinstance(h, ROOT.TH3):
        shape = (h.GetNbinsZ() + 2, h.GetNbinsY() + 2, h.GetNbinsX() + 2)
    elif isinstance(h, ROOT.TH2):
        shape = (h.GetNbinsY() + 2, h.GetNbinsX() + 2)
    elif isinstance(h, ROOT.TH1):
        shape = (h.GetNbinsX() + 2,)
    arr = arr.reshape(shape)
    if not include_overflow:
        slices = []
        for axis, bins in enumerate(shape):
            slices.append(slice(1, -1))
        arr = arr[tuple(slices)]
    return arr


def rnp_array2hist(array, h):
    """
    Sets bin contents with a numpy array

    Parameters
    ----------
    array : np.array
        numpy array with counts
    h : ROOT.TH
        histogram
    """
    dtype = np.double
    if isinstance(h, ROOT.TH3):
        shape = (h.GetNbinsX() + 2, h.GetNbinsY() + 2, h.GetNbinsZ() + 2)
    elif isinstance(h, ROOT.TH2):
        shape = (h.GetNbinsX() + 2, h.GetNbinsY() + 2)
    elif isinstance(h, ROOT.TH1):
        shape = (h.GetNbinsX() + 2,)
    if array.shape != shape:
        slices = []
        for axis, bins in enumerate(shape):
            if array.shape[axis] == bins - 2:
                slices.append(slice(1, -1))
            elif array.shape[axis] == bins:
                slices.append(slice(None))
            else:
                raise ValueError("array and histogram are not compatible")
        array_overflow = np.zeros(shape, dtype=dtype)
        array_overflow[tuple(slices)] = array
        array = array_overflow
    if array.shape != shape:
        raise "array2hist: Different shape between array and h"
    array = np.ravel(np.transpose(array))
    nx = len(array)
    arr = memoryview(array)
    h.Set(nx, arr)


def _fold(h, ifrom, ito):
    cont = rnp_hist2array(h, copy=False, include_overflow=True)
    sumw2 = rnp_array(h.GetSumw2(), copy=False)
    if isinstance(h, ROOT.TH3):
        shape = (h.GetNbinsX() + 2, h.GetNbinsY() + 2, h.GetNbinsZ() + 2)
    elif isinstance(h, ROOT.TH2):
        shape = (h.GetNbinsX() + 2, h.GetNbinsY() + 2)
    elif isinstance(h, ROOT.TH1):
        shape = (h.GetNbinsX() + 2,)
    if array.shape != shape:
        slices = []
        for axis, bins in enumerate(shape):
            if array.shape[axis] == bins - 2:
                slices.append(slice(1, -1))
            elif array.shape[axis] == bins:
                slices.append(slice(None))

    if h.GetDimension() == 1:
        cont[ito] += cont[ifrom]
        cont[ifrom] = 0.0
        sumw2[ito] += sumw2[ifrom]
        sumw2[ifrom] = 0.0

    elif h.GetDimension() == 2:
        cont[ito, :] += cont[ifrom, :]
        cont[ifrom, :] = 0.0
        cont[:, ito] += cont[:, ifrom]
        cont[:, ifrom] = 0.0

        # sumw2 is y-major
        nx = h.GetNbinsX()
        ny = h.GetNbinsY()
        sumw2 = np.reshape(sumw2, (ny + 2, nx + 2))
        sumw2[ito, :] += sumw2[ifrom, :]
        sumw2[ifrom, :] = 0.0
        sumw2[:, ito] += sumw2[:, ifrom]
        sumw2[:, ifrom] = 0.0

    elif h.GetDimension() == 3:
        cont[ito, :, :] += cont[ifrom, :, :]
        cont[ifrom, :, :] = 0.0
        cont[:, ito, :] += cont[:, ifrom, :]
        cont[:, ifrom, :] = 0.0
        cont[:, :, ito] += cont[:, :, ifrom]
        cont[:, :, ifrom] = 0.0

        # sumw2 is y-major
        nx = h.GetNbinsX()
        ny = h.GetNbinsY()
        nz = h.GetNbinsZ()
        sumw2 = np.reshape(sumw2, (nz + 2, ny + 2, nx + 2))
        sumw2[ito, :, :] += sumw2[ifrom, :, :]
        sumw2[ifrom, :, :] = 0.0
        sumw2[:, ito, :] += sumw2[:, ifrom, :]
        sumw2[:, ifrom, :] = 0.0
        sumw2[:, :, ito] += sumw2[:, :, ifrom]
        sumw2[:, :, ifrom] = 0.0


def _postplot(hTotal, doFold, unroll=True):
    if doFold == 1 or doFold == 3:
        _fold(hTotal, 0, 1)
    if doFold == 2 or doFold == 3:
        _fold(hTotal, -1, -2)

    # if unroll and hTotal.InheritsFrom(ROOT.TH2.Class()):
    if unroll and isinstance(hTotal, ROOT.TH2) and hTotal.GetDimension() == 2:
        # --- transform 2D into 1D
        #
        #      3    6    9
        #      2    5    8
        #      1    4    7
        #
        # over/underflow are discarded
        hTotal_rolled = hTotal

        nx = hTotal_rolled.GetNbinsX()
        ny = hTotal_rolled.GetNbinsY()
        name = hTotal.GetName()
        hTotal = ROOT.TH1D(
            name + "_tmp", hTotal.GetTitle(), nx * ny, 0.0, float(nx * ny)
        )
        hTotal.GetXaxis().SetTitle(hTotal_rolled.GetXaxis().GetTitle())

        # contents
        cont = rnp_hist2array(hTotal_rolled, copy=False).reshape(-1)
        # hist2array for TH2 returns [x, y] arrays -> reshape -1 achieves the desired bin numbering
        rnp_array2hist(cont, hTotal)

        # sumw2
        # Sumw2 array follows the ROOT bin numbering (y-major)
        sumw22d = rnp_array(hTotal_rolled.GetSumw2(), copy=False).reshape(
            (ny + 2, nx + 2)
        )
        # chop off overflow and underflow bins
        sumw22d = sumw22d[1:-1, 1:-1]
        sumw2 = rnp_array(hTotal.GetSumw2(), copy=False)
        # transpose to change the bin numbering
        sumw2[1:-1] = sumw22d.T.flat

        # stats
        stats2d = ROOT.TArrayD(7)
        hTotal_rolled.GetStats(stats2d.GetArray())
        stats1d = ROOT.TArrayD(4)
        stats1d[0] = stats2d[0]
        stats1d[1] = stats2d[1]
        stats1d[2] = stats2d[2] + stats2d[4]
        stats1d[3] = stats2d[3] + stats2d[5]
        hTotal.PutStats(stats1d.GetArray())

        hTotal_rolled.Delete()

    if unroll and isinstance(hTotal, ROOT.TH3) and hTotal.GetDimension() == 3:
        # --- transform 2D into 1D
        #
        #      3    6    9
        #      2    5    8
        #      1    4    7
        #
        # over/underflow are discarded
        hTotal_rolled = hTotal

        nx = hTotal_rolled.GetNbinsX()
        ny = hTotal_rolled.GetNbinsY()
        nz = hTotal_rolled.GetNbinsZ()
        name = hTotal.GetName()
        hTotal = ROOT.TH1D(
            name + "_tmp", hTotal.GetTitle(), nx * ny * nz, 0.0, float(nx * ny * nz)
        )
        hTotal.GetXaxis().SetTitle(hTotal_rolled.GetXaxis().GetTitle())

        # contents
        cont = rnp_hist2array(hTotal_rolled, copy=False).reshape(-1)
        # hist2array for TH3 returns [x, y, z] arrays -> reshape -1 achieves the desired bin numbering
        rnp_array2hist(cont, hTotal)

        # sumw2
        # Sumw2 array follows the ROOT bin numbering (z-major)
        sumw22d = rnp_array(hTotal_rolled.GetSumw2(), copy=False).reshape(
            (nz + 2, ny + 2, nx + 2)
        )
        # chop off overflow and underflow bins
        sumw22d = sumw22d[1:-1, 1:-1, 1:-1]
        sumw2 = rnp_array(hTotal.GetSumw2(), copy=False)
        # transpose to change the bin numbering
        sumw2[1:-1] = sumw22d.T.flat

        # stats in 3D
        # stats[0] = sumw
        # stats[1] = sumw2
        # stats[2] = sumwx
        # stats[3] = sumwx2
        # stats[4] = sumwy
        # stats[5] = sumwy2
        # stats[6] = sumwxy
        # stats[7] = sumwz
        # stats[8] = sumwz2
        # stats[9] = sumwxz
        # stats[10]= sumwyz

        stats3d = ROOT.TArrayD(11)
        hTotal_rolled.GetStats(stats3d.GetArray())
        stats1d = ROOT.TArrayD(4)
        stats1d[0] = stats3d[0]
        stats1d[1] = stats3d[1]
        stats1d[2] = stats3d[2] + stats3d[4] + stats3d[7]
        stats1d[3] = stats3d[3] + stats3d[5] + stats3d[8]
        hTotal.PutStats(stats1d.GetArray())

        hTotal_rolled.Delete()

    return hTotal
