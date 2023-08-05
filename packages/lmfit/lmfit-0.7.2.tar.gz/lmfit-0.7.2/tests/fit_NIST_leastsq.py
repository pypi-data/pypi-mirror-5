# from __future__ import print_function
import sys
import math

try:
    import matplotlib
    matplotlib.use('WXAgg')
    import pylab
    HASPYLAB = True
except ImportError:
    HASPYLAB = False

from scipy.optimize import leastsq, curve_fit

from NISTModels import Models, ReadNistData


def ndig(a, b):
    return int(0.5-math.log10(abs(abs(a)-abs(b))/abs(b)))

def Compare_NIST_Results(DataSet, params, NISTdata):
    print(' ======================================')
    print(' %s: ' % DataSet)
    print(' | Parameter Name |  Value Found   |  Certified Value | # Matching Digits |')
    print( ' |----------------+----------------+------------------+-------------------|')

    val_dig_min = 1000
    err_dig_min = 1000
    for i in range(NISTdata['nparams']):
        parname = 'b%i' % (i+1)
        par = params[parname]
        thisval = par.value
        certval = NISTdata['cert_values'][i]

        thiserr = par.stderr
        certerr = NISTdata['cert_stderr'][i]
        vdig   = ndig(thisval, certval)
        edig   = ndig(thiserr, certerr)

        pname = (parname + ' value ' + ' '*14)[:14]
        ename = (parname + ' stderr' + ' '*14)[:14]
        print(' | %s | % -.7e | % -.7e   | %2i                |' % (pname, thisval, certval, vdig))
        print(' | %s | % -.7e | % -.7e   | %2i                |' % (ename, thiserr, certerr, edig))

        val_dig_min = min(val_dig_min, vdig)
        err_dig_min = min(err_dig_min, edig)

    print(' |----------------+----------------+------------------+-------------------|')
    sumsq = NISTdata['sum_squares']
    chi2 = 'xx' # myfit.chisqr
    print(' | Sum of Squares | %.7e  | %.7e    |  %2i               |' % (chi2, sumsq,
                                                                          ndig(chi2, sumsq)))
    print(' |----------------+----------------+------------------+-------------------|')

    print(' Worst agreement: %i digits for value, %i digits for error ' % (val_dig_min, err_dig_min))

    return val_dig_min

def NIST_Test(DataSet, start='start2', plot=True):

    NISTdata = ReadNistData(DataSet)
    resid, npar, dimx = Models[DataSet]
    y = NISTdata['y']
    x = NISTdata['x']

    params = []
    param_names = []
    for i in range(npar):
        pname = 'b%i' % (i+1)
        cval  = NISTdata['cert_values'][i]
        cerr  = NISTdata['cert_stderr'][i]
        pval1 = NISTdata[start][i]
        params.append(pval1)
        param_names.append(pname)


        #     myfit = Minimizer(resid, params, fcn_args=(x,), fcn_kws={'y':y},
        #                       scale_covar=True)
        #
    print 'lsout ', params
    lsout = leastsq(resid, params, args=(x, y), full_output=True)

    print 'lsout ', lsout
    print params   , len(x), len(y)

    digs = Compare_NIST_Results(DataSet,  params, NISTdata)

    if plot and HASPYLAB:
        fit = -resid(params, x, )
        pylab.plot(x, y, 'r+-')
        pylab.plot(x, fit, 'ko--')
        pylab.show()

    return digs > 2

msg1 = """
----- NIST StRD Models -----
Select one of the Models listed below:
and a starting point of 'start1' or 'start2'
"""

msg2 = """
That is, use
    python fit_NIST.py Bennet5 start1
or go through all models and starting points with:
    python fit_NIST.py all
"""

if __name__  == '__main__':
    dset = 'Bennett5'
    start = 'start2'
    if len(sys.argv) < 2:
        print(msg1)
        out = ''
        for d in sorted(Models.keys()):
            out = out + ' %s ' % d
            if len(out) > 55:
                print( out)
                out = ''
        print(out)
        print(msg2)

        sys.exit()

    if len(sys.argv) > 1:
        dset = sys.argv[1]
    if len(sys.argv) > 2:
        start = sys.argv[2]
    if dset.lower() == 'all':
        tpass = 0
        tfail = 0
        failures = []
        dsets = sorted(Models.keys())
        for dset in dsets:
            for start in ('start1', 'start2'):
                if NIST_Test(dset, start=start, plot=False):
                    tpass += 1
                else:
                    tfail += 1
                    failures.append("   %s (starting at '%s')" % (dset, start))

        print('--------------------------------------')
        print(' Final Results: %i pass, %i fail.' % (tpass, tfail))
        print(' Tests Failed for:\n %s' % '\n '.join(failures))
        print('--------------------------------------')
    else:
        NIST_Test(dset, start=start, plot=True)

